#!/usr/bin/env python3
"""bootstrap.py —— 按 org-config.yaml 把一个空 org 搭成本书描述的样子。

    python3 bootstrap/bootstrap.py plan    org-config.yaml   # 只读：列出会做什么，不改任何东西
    python3 bootstrap/bootstrap.py render  org-config.yaml   # 把模板渲染到工作目录（默认 /tmp/<org>-render），不碰 GitHub
    python3 bootstrap/bootstrap.py apply   org-config.yaml   # 真正执行；可以重复跑（每一步都先查再改）
    python3 bootstrap/bootstrap.py apply   org-config.yaml --only teams,repos
    python3 bootstrap/bootstrap.py verify  org-config.yaml   # = python3 bootstrap/verify.py org-config.yaml

render 之后、apply 之前，按 AGENT-BOOTSTRAP.md 第 3 步改写渲染目录里和领域有关的内容。
apply 会用渲染目录里的文件；渲染目录不存在时先自动 render。

依赖：gh（已登录，令牌带 repo、admin:org、project、workflow）、git、python3、PyYAML。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
STEPS = ["preflight", "org", "teams", "repos", "grants", "labels", "meeting-issues",
         "wiki", "issue-repos", "board", "profile", "code-repos", "sync-agents", "invite"]
DRY = False
LOG = []


# ───────────────────────── 基础 ─────────────────────────
def die(msg):
    print(f"✗ {msg}")
    sys.exit(1)


def say(msg):
    print(msg)
    LOG.append(msg)


def run(cmd, check=True, cwd=None, inp=None, write=False):
    """跑命令。write=True 的在 plan / dry-run 下只打印不执行。"""
    if write and DRY:
        say("  [plan] " + (cmd if isinstance(cmd, str) else " ".join(cmd)))
        return ""
    r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, input=inp,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"命令失败：{cmd if isinstance(cmd, str) else ' '.join(cmd)}\n{r.stderr.strip()[:800]}")
    return r.stdout.strip()


def gh(*args, check=True, write=False, inp=None):
    return run(["gh", *args], check=check, write=write, inp=inp)


def gh_json(*args, check=True):
    out = gh(*args, check=check)
    try:
        return json.loads(out) if out else None
    except json.JSONDecodeError:
        return None


def exists(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    return r.returncode == 0


def graphql(query, **vars_):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in vars_.items():
        args += ["-F" if isinstance(v, (int, bool)) else "-f", f"{k}={json.dumps(v) if isinstance(v, bool) else v}"]
    out = gh(*args)
    data = json.loads(out)
    if data.get("errors"):
        die(f"GraphQL 错误：{data['errors']}")
    return data["data"]


def load_cfg(path):
    try:
        import yaml
    except ImportError:
        die("缺 PyYAML：pip install pyyaml")
    cfg = yaml.safe_load(open(path, encoding="utf-8"))
    for k in ["org", "org_title", "issue_repos", "owners", "members"]:
        if not cfg.get(k):
            die(f"org-config 缺必填字段：{k}")
    if cfg["issue_repos"] not in ("one", "two"):
        die("issue_repos 只能是 one 或 two")
    cfg.setdefault("vendor", "Google")
    cfg.setdefault("model", "ModelX")
    cfg.setdefault("dev_branch", "main")
    cfg.setdefault("phase", "poc")
    cfg.setdefault("code_repos", [])
    cfg.setdefault("actions", "disabled")
    cfg.setdefault("board_template", "https://github.com/users/yangwhale/projects/1")
    cfg.setdefault("domain", "same")
    if not cfg.get("customer_groups"):
        if cfg["issue_repos"] == "two":
            cfg["customer_groups"] = [
                {"team": "training", "desc": "客户训练组", "repos": ["project-management", "project-management-infra"]},
                {"team": "gke", "desc": "客户 GKE 组", "repos": ["project-management-infra"]},
                {"team": "network", "desc": "客户网络组", "repos": ["project-management-infra"]}]
        else:
            cfg["customer_groups"] = [{"team": "training", "desc": "客户工程师", "repos": ["project-management"]}]
    cfg.setdefault("repo_desc", {})
    cfg["repo_desc"].setdefault("project-management", "训练与推理的 issue；这一方向的文档、例会纪要、配方和复现")
    cfg["repo_desc"].setdefault("project-management-infra", "GKE 与网络的 issue；这一方向的文档、例会纪要、配方和复现")
    cfg.setdefault("meeting_titles", {"project-management": "训练例会记录", "project-management-infra": "基础设施例会记录"})
    cfg.setdefault("view_names", {})
    example = {"alice-g", "bob-g", "carol-c", "dave-c", "erin-g", "frank-c"}
    flat = [p for ps in (cfg["members"] or {}).values() for p in (ps or [])] + list(cfg["owners"])
    bad = [p for p in flat if p in example or p.startswith("<")]
    if bad:
        die(f"org-config 里还有书中的示例账号或占位符：{bad}。这些名字在 GitHub 上可能是真实的陌生人，换成真实成员")
    fr = cfg.get("fixed_route") or {}
    if fr and (not fr.get("assignee") or fr["assignee"].startswith("<")):
        die("fixed_route.assignee 还是占位符：填真实账号，或者删掉整个 fixed_route")
    seen = {}
    for team, people in (cfg["members"] or {}).items():
        for p in people or []:
            if p in seen:
                die(f"{p} 同时在 {seen[p]} 和 {team}：一人只进一个团队（第 3 章 3.4）")
            seen[p] = team
    cfg["work"] = cfg.get("work") or f"/tmp/{cfg['org']}-render"
    return cfg


def issue_repos(cfg):
    return ["project-management"] + (["project-management-infra"] if cfg["issue_repos"] == "two" else [])


def subteams(cfg):
    return [g["team"] for g in cfg["customer_groups"]]


# ───────────────────────── render ─────────────────────────
def render(cfg):
    """把 appendix/ 拷到工作目录，做纯机械的替换。语义改写留给 bot（AGENT-BOOTSTRAP.md 第 3 步）。"""
    W = cfg["work"]
    if os.path.exists(W):
        if "--force" not in sys.argv:
            die(f"渲染目录 {W} 已存在，里面可能有你改写过的内容。确定要重来就加 --force（会丢掉改写）")
        shutil.rmtree(W)
    shutil.copytree(os.path.join(BOOK, "appendix"), W)
    org = cfg["org"]
    src = os.path.join(W, "templates/wiki/onboarding/working-in-northpeak.md")
    os.rename(src, src.replace("northpeak", org))
    reps = [("northpeak", org), ("NorthPeak", cfg["org_title"]), ("modelx", cfg["dev_branch"]),
            ("ModelX", cfg["model"]), ("Google", cfg["vendor"]), ("<阶段>", cfg["phase"])]
    fr = cfg.get("fixed_route")
    if fr:
        reps.append(("<上游对接人账号>", fr["assignee"]))
    for root, _, files in os.walk(W):
        for f in files:
            p = os.path.join(root, f)
            try:
                s = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            t = s
            for a, b in reps:
                t = t.replace(a, b)
            if t != s:
                open(p, "w", encoding="utf-8").write(t)
    # AGENTS.md：没有固定路由就删掉那一段
    agents = os.path.join(W, "templates/AGENTS.md")
    s = open(agents, encoding="utf-8").read()
    if not fr:
        s = re.sub(r"\n\*\*固定路由\*\*：[^\n]*\n", "\n", s)
    open(agents, "w", encoding="utf-8").write(s)
    # sync-agents.sh：按配置生成同步目标
    targets = [f"{r}:main" for r in issue_repos(cfg)]
    for c in cfg["code_repos"]:
        for b in c.get("agents_branches") or [c.get("default_branch", "main")]:
            targets.append(f"{c['name']}:{b}")
    sp = os.path.join(W, "scripts/sync-agents.sh")
    s = open(sp, encoding="utf-8").read()
    s = re.sub(r'^TARGETS=.*$', f'TARGETS="{" ".join(targets)}"   # 新仓库建好后加进来', s, flags=re.M)
    s = re.sub(r'^DIRECT=.*$', f'DIRECT="{" ".join(issue_repos(cfg))}"   # 同步 AGENTS.md 算记录类改动，issue 仓直接推 main', s, flags=re.M)
    open(sp, "w", encoding="utf-8").write(s)
    for c in cfg["code_repos"]:
        if c["kind"] != "own":
            shutil.copyfile(os.path.join(W, "templates/FORK.md"), os.path.join(W, f"FORK-{c['name']}.md"))
        else:
            t = open(os.path.join(W, "templates/code-repo/README.md"), encoding="utf-8").read()
            open(os.path.join(W, f"README-{c['name']}.md"), "w", encoding="utf-8").write(
                t.replace("<仓库名>", c["name"]).replace("<一句话：这个仓库是什么>", c.get("description", "<一句话：这个仓库是什么>")))
    left = run(f"grep -rliI 'northpeak\\|modelx' {W} || true")
    say(f"✓ 已渲染到 {W}")
    if left:
        say("  还有示例名残留（多半在说明文字里，检查一下）：\n  " + left.replace("\n", "\n  "))
    say("  下一步：按 AGENT-BOOTSTRAP.md 第 3 步改写渲染目录里和领域有关的内容，再 apply")


# ───────────────────────── 各步骤 ─────────────────────────
def step_preflight(cfg):
    st = run("gh auth status 2>&1", check=False)
    scopes = re.findall(r"'([a-z:_]+)'", st)
    need = ["repo", "admin:org", "project", "workflow"]
    miss = [s for s in need if s not in scopes]
    if miss:
        die(f"gh 令牌缺权限 {miss}：gh auth refresh -s {','.join(miss)}")
    me = gh("api", "user", "--jq", ".login")
    cfg["me"] = me
    if not exists(f"orgs/{cfg['org']}"):
        die(f"org {cfg['org']} 不存在：先在网页上建 https://github.com/organizations/plan（Free）")
    role = gh("api", f"orgs/{cfg['org']}/memberships/{me}", "--jq", ".role", check=False)
    if role != "admin":
        die(f"{me} 不是 {cfg['org']} 的 Owner（当前角色：{role or '非成员'}）")
    if me not in cfg["owners"]:
        say(f"  注意：运行者 {me} 不在 owners 列表里")
    if shutil.which("git") is None:
        die("缺 git")
    run("gh auth setup-git", write=False)
    say(f"✓ preflight：{me} 是 {cfg['org']} 的 Owner，令牌权限齐全")


def step_org(cfg):
    org = cfg["org"]
    gh("api", "-X", "PATCH", f"orgs/{org}", "-f", "default_repository_permission=none",
       "-F", "members_can_fork_private_repositories=false", write=True)
    if cfg["actions"] == "disabled":
        gh("api", "-X", "PUT", f"orgs/{org}/actions/permissions", "-f", "enabled_repositories=none", write=True)
    say("✓ org：默认权限 None，禁止 fork 私有仓" + ("，Actions 停用" if cfg["actions"] == "disabled" else ""))


TEAM_DESC = {
    "maintainers": "管理员：account team 的厂商员工，所有仓库 Admin，管设置、权限和规矩",
    "googlers": "厂商员工：支持客户的工程师，所有仓库 Maintain",
    "customer": "客户工程师（父团队）：联合开发仓库读写，可提 PR、写 RFC",
    "partners": "合作方：第三方工程团队，只授权其负责的仓库",
    "observers": "旁观者：客户管理层、PM 等，只读看进度和 wiki",
    "training": "客户训练组（继承 customer 的全部仓库权限）",
    "gke": "客户 GKE 组（继承 customer 的全部仓库权限）",
    "network": "客户网络组（继承 customer 的全部仓库权限）",
}


def ensure_team(org, name, parent_id=None, desc=None):
    if exists(f"orgs/{org}/teams/{name}"):
        return gh("api", f"orgs/{org}/teams/{name}", "--jq", ".id")
    args = ["api", "-X", "POST", f"orgs/{org}/teams", "-f", f"name={name}", "-f",
            f"description={desc or TEAM_DESC.get(name, name)}", "-f", "privacy=closed", "--jq", ".id"]
    if parent_id:
        args += ["-F", f"parent_team_id={parent_id}"]
    return gh(*args, write=True) or "<new>"


def step_teams(cfg):
    org = cfg["org"]
    for t in ["maintainers", "googlers", "customer", "partners", "observers"]:
        ensure_team(org, t)
    cust = gh("api", f"orgs/{org}/teams/customer", "--jq", ".id", check=False) if exists(f"orgs/{org}/teams/customer") else "<customer-id>"
    for g in cfg["customer_groups"]:
        ensure_team(org, g["team"], cust, f"{g['desc']}（继承 customer 的全部仓库权限）")
    # 建团队的人自动进了每个团队；一人只进一个团队（第 3 章 3.4）
    me = cfg.get("me") or gh("api", "user", "--jq", ".login")
    home = next((t for t, ps in cfg["members"].items() if me in (ps or [])), "maintainers")
    for t in ["maintainers", "googlers", "customer", "partners", "observers"] + subteams(cfg):
        if t != home and exists(f"orgs/{org}/teams/{t}/memberships/{me}"):
            gh("api", "-X", "DELETE", f"orgs/{org}/teams/{t}/memberships/{me}", write=True)
    say(f"✓ teams：{', '.join(['maintainers', 'googlers', 'customer', 'partners', 'observers'] + subteams(cfg))}；{me} 只留在 {home}")


def repo_settings(org, name, issues):
    gh("api", "-X", "PATCH", f"repos/{org}/{name}", "-F", f"has_issues={'true' if issues else 'false'}",
       "-F", "has_wiki=false", "-F", "has_discussions=false", "-F", "delete_branch_on_merge=true", write=True)


def ensure_repo(org, name, desc, issues, readme=True):
    if not exists(f"repos/{org}/{name}"):
        args = ["repo", "create", f"{org}/{name}", "--private", "--description", desc]
        if readme:
            args.append("--add-readme")
        gh(*args, write=True)
    repo_settings(org, name, issues)


def step_repos(cfg):
    org = cfg["org"]
    ensure_repo(org, "wiki", "规矩（AGENTS.md）、守则、RFC、新人入门；规矩和权限的 issue", True)
    for r in issue_repos(cfg):
        ensure_repo(org, r, cfg["repo_desc"][r], True)
    ensure_repo(org, ".github-private", "org 主页（成员可见）", False)
    for c in cfg["code_repos"]:
        name = c["name"]
        if c["kind"] == "own":
            ensure_repo(org, name, c.get("description", "自研工具"), False)
            continue
        if exists(f"repos/{org}/{name}"):
            repo_settings(org, name, False)
            continue
        tmp = tempfile.mkdtemp()
        run(["git", "clone", "--bare", c["upstream"], f"{tmp}/{name}.git"], write=True)
        gh("repo", "create", f"{org}/{name}", "--private", "--description", f"{c['upstream']} 的私有副本", write=True)
        run(["git", "-C", f"{tmp}/{name}.git", "push", "--mirror", f"https://github.com/{org}/{name}.git"], write=True)
        repo_settings(org, name, False)
        if c.get("dev_branch_from"):
            pass
    say(f"✓ repos：wiki、{'、'.join(issue_repos(cfg))}、.github-private、{len(cfg['code_repos'])} 个代码仓")


def grant(org, team, repo, perm):
    gh("api", "-X", "PUT", f"orgs/{org}/teams/{team}/repos/{org}/{repo}", "-f", f"permission={perm}", write=True)


def step_grants(cfg):
    org = cfg["org"]
    core = ["wiki"] + issue_repos(cfg) + [c["name"] for c in cfg["code_repos"]]
    for r in core:
        grant(org, "maintainers", r, "admin")
        grant(org, "googlers", r, "maintain")
    joint = ["wiki"] + [c["name"] for c in cfg["code_repos"] if c.get("joint", True)]
    for r in joint:
        grant(org, "customer", r, "push")
        grant(org, "observers", r, "pull")
    grant(org, "partners", "wiki", "push")
    for g in cfg["customer_groups"]:
        for r in g["repos"]:
            grant(org, g["team"], r, "push")
    for r in issue_repos(cfg):
        grant(org, "observers", r, "pull")
    grant(org, "partners", "project-management", "triage")
    grant(org, "maintainers", ".github-private", "maintain")
    for t in ["googlers", "customer", "partners", "observers"]:
        grant(org, t, ".github-private", "pull")
    say("✓ grants：按第 3 章 3.3 的授权表")


def step_labels(cfg):
    org = cfg["org"]
    sh = os.path.join(cfg["work"], "scripts/setup-labels.sh")
    roles = [("wiki", "wiki"), ("project-management", "training")]
    if cfg["issue_repos"] == "two":
        roles.append(("project-management-infra", "infra"))
    for repo, role in roles:
        run(["bash", sh, f"{org}/{repo}", role], write=True)
    say("✓ labels：" + "、".join(r for r, _ in roles))


MEETING = {"project-management": "meeting-log-issue-training.md",
           "project-management-infra": "meeting-log-issue-infra.md"}


def step_meeting_issues(cfg):
    org = cfg["org"]
    for r in issue_repos(cfg):
        title, body = cfg["meeting_titles"][r], MEETING[r]
        if exists(f"repos/{org}/{r}/issues/1"):
            say(f"  {r} 已有 1 号 issue（例会记录），跳过")
            continue
        url = gh("issue", "create", "-R", f"{org}/{r}", "--title", title, "--label", "type/docs",
                 "--body-file", os.path.join(cfg["work"], "templates", body), write=True)
        if url and not url.endswith("/issues/1"):
            say(f"  ⚠ {url} 不是 1 号：把 {r} 的 meetings/README.md 和 PR 模板里的 #1 改成实际号码")
        if url:
            gh("issue", "pin", url, write=True)
    say("✓ meeting-issues：例会记录 issue 已建并置顶")


def push_files(cfg, repo, files, msg, branch=None):
    """files: {仓库内路径: 本地源文件}。只在内容有变化时提交。建站期间直接推默认分支。"""
    org = cfg["org"]
    if DRY:
        say(f"  [plan] 推 {len(files)} 个文件到 {org}/{repo}：{msg}")
        return
    tmp = tempfile.mkdtemp()
    run(["gh", "repo", "clone", f"{org}/{repo}", tmp, "--", "-q"])
    if branch:
        run(["git", "checkout", "-q", branch], cwd=tmp)
    for dst, src in files.items():
        p = os.path.join(tmp, dst)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if src is None:
            open(p, "a").close()
        else:
            shutil.copyfile(src, p)
    run(["git", "add", "-A"], cwd=tmp)
    if not run(["git", "status", "--porcelain"], cwd=tmp):
        say(f"  {repo}：已是最新")
        return
    mf = os.path.join(tmp, ".git", "BOOTSTRAP_MSG")
    open(mf, "w").write(msg + "\n")
    run(["git", "commit", "-q", "-F", mf], cwd=tmp)
    run(["git", "push", "-q"], cwd=tmp)
    say(f"  {repo}：已推送（{msg}）")


def tree(base, prefix=""):
    out = {}
    for root, _, files in os.walk(base):
        for f in files:
            src = os.path.join(root, f)
            out[os.path.join(prefix, os.path.relpath(src, base))] = src
    return out


def step_wiki(cfg):
    W, T = cfg["work"], os.path.join(cfg["work"], "templates")
    f = {"AGENTS.md": f"{T}/AGENTS.md", "CLAUDE.md": f"{T}/CLAUDE.md", "GEMINI.md": f"{T}/GEMINI.md",
         "README.md": f"{T}/wiki/README.md", ".github/CODEOWNERS": f"{T}/wiki/CODEOWNERS",
         ".github/pull_request_template.md": f"{T}/pull_request_template.md",
         "docs/best-practices/code-review.md": f"{T}/wiki/code-review.md"}
    f.update(tree(f"{T}/wiki/onboarding", "docs/onboarding"))
    f.update(tree(f"{T}/wiki/rfc", "docs/rfc"))
    f.update(tree(f"{T}/wiki/ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE"))
    for s in ["board.sh", "sync-agents.sh", "pr-check.py"]:
        f[f"scripts/{s}"] = f"{W}/scripts/{s}"
    push_files(cfg, "wiki", f, "docs: 初始规矩（bootstrap）")
    say("✓ wiki")


def step_issue_repos(cfg):
    W, T = cfg["work"], os.path.join(cfg["work"], "templates")
    for r in issue_repos(cfg):
        kind = "training" if r == "project-management" else "infra"
        S = f"{T}/issue-repo-{kind}"
        f = tree(f"{S}/ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE")
        if cfg["issue_repos"] == "one":
            f[".github/ISSUE_TEMPLATE/config.yml"] = f"{T}/issue-repo-infra/ISSUE_TEMPLATE/config.yml"  # 只指向 wiki
        f.update({"README.md": f"{S}/README.md", ".github/pull_request_template.md": f"{S}/pull_request_template.md",
                  ".github/CODEOWNERS": f"{S}/CODEOWNERS", "meetings/_template/notes.md": f"{T}/meetings-notes-template-{kind}.md",
                  "repro/common/check_dir_list.py": f"{W}/scripts/check_dir_list.py",
                  "AGENTS.md": f"{T}/AGENTS.md", "CLAUDE.md": f"{T}/CLAUDE.md", "GEMINI.md": f"{T}/GEMINI.md",
                  "assets/issues/.gitkeep": None, "repro/issues/.gitkeep": None})
        for d in ["library", "meetings", "recipes", "repro"]:
            f[f"{d}/README.md"] = f"{S}/{d}-README.md"
        push_files(cfg, r, f, "chore: 初始结构、模板、规矩（bootstrap）")
    say("✓ issue-repos")


def project_by_url(url):
    m = re.match(r"https://github.com/(users|orgs)/([^/]+)/projects/(\d+)", url)
    if not m:
        die(f"board_template 不是 Projects 地址：{url}")
    kind = "user" if m.group(1) == "users" else "organization"
    d = graphql(f'query($l:String!,$n:Int!){{{kind}(login:$l){{projectV2(number:$n){{id}}}}}}', l=m.group(2), n=int(m.group(3)))
    return d[kind]["projectV2"]["id"]


def step_board(cfg):
    org, title = cfg["org"], cfg["org_title"]
    found = graphql('query($l:String!){organization(login:$l){id projectsV2(first:50){nodes{id number title}}}}', l=org)["organization"]
    pid = next((p["id"] for p in found["projectsV2"]["nodes"] if p["title"] == title), None)
    if not pid:
        if DRY:
            say(f"  [plan] copyProjectV2 {cfg['board_template']} → {org}「{title}」")
            say("✓ board（plan）")
            return
        src = project_by_url(cfg["board_template"])
        pid = graphql('mutation($p:ID!,$o:ID!,$t:String!){copyProjectV2(input:{projectId:$p,ownerId:$o,title:$t,includeDraftIssues:false}){projectV2{id}}}',
                      p=src, o=found["id"], t=title)["copyProjectV2"]["projectV2"]["id"]
        say(f"  已从模板复制看板 {pid}")
    info = graphql('query($p:ID!){node(id:$p){... on ProjectV2{number views(first:20){nodes{id name filter}} fields(first:50){nodes{... on ProjectV2SingleSelectField{id name options{id name}}}}}}}', p=pid)["node"]
    # 视图筛选、README、可见性
    for v in info["views"]["nodes"]:
        new_name = cfg["view_names"].get(v["name"])
        if new_name and not DRY:
            graphql('mutation($v:ID!,$n:String!){updateProjectV2View(input:{viewId:$v,name:$n}){projectV2View{id}}}', v=v["id"], n=new_name)
        if v["filter"] and "northpeak" in v["filter"]:
            if cfg["issue_repos"] == "one" and "infra" in v["name"] + v["filter"] and "-repo" not in v["filter"]:
                gh("api", "graphql", "-f", f'query=mutation{{deleteProjectV2View(input:{{viewId:"{v["id"]}"}}){{deletedViewId}}}}', write=True)
                continue
            f = v["filter"].replace("northpeak", org)
            if cfg["issue_repos"] == "one":
                f = re.sub(r"\s*-repo:\S+", "", f)
            if not DRY:
                graphql('mutation($v:ID!,$f:String!){updateProjectV2View(input:{viewId:$v,filter:$f}){projectV2View{id}}}', v=v["id"], f=f)
    if not DRY:
        graphql('mutation($p:ID!,$r:String!,$d:String!){updateProjectV2(input:{projectId:$p,readme:$r,shortDescription:$d,public:false}){projectV2{id}}}',
                p=pid, r=f"状态由规则自动改，别手动拖；规矩见 {org}/wiki 的 AGENTS.md。", d=f"{title} 进度总览")
    # 团队访问：厂商 Write，客户和旁观者 Read
    collab = []
    for t, role in [("maintainers", "ADMIN"), ("googlers", "WRITER"), ("customer", "READER"), ("observers", "READER"), ("partners", "READER")]:
        tid = gh("api", f"orgs/{org}/teams/{t}", "--jq", ".node_id", check=False)
        if tid:
            collab.append(f'{{teamId:"{tid}",role:{role}}}')
    if collab and not DRY:
        gh("api", "graphql", "-f", f'query=mutation{{updateProjectV2Collaborators(input:{{projectId:"{pid}",collaborators:[{",".join(collab)}]}}){{clientMutationId}}}}')
    # 把 id 写进渲染目录的 board.sh
    fields = {f["name"]: f for f in info["fields"]["nodes"] if f}
    st, sz = fields["Status"], fields["Size"]
    bs = os.path.join(cfg["work"], "scripts/board.sh")
    s = open(bs, encoding="utf-8").read()
    s = re.sub(r"^PROJECT=\S+", f"PROJECT={pid}", s, flags=re.M)
    s = re.sub(r"^F_STATUS=\S+", f"F_STATUS={st['id']}", s, flags=re.M)
    s = re.sub(r"^F_SIZE=\S+", f"F_SIZE={sz['id']}", s, flags=re.M)
    so = " ".join(f'["{o["name"]}"]={o["id"]}' for o in st["options"])
    zo = " ".join(f'[{o["name"]}]={o["id"]}' for o in sz["options"])
    s = re.sub(r"^declare -A STATUS=.*$", f"declare -A STATUS=({so})", s, flags=re.M)
    s = re.sub(r"^declare -A SIZE=.*$", f"declare -A SIZE=({zo})", s, flags=re.M)
    open(bs, "w", encoding="utf-8").write(s)
    push_files(cfg, "wiki", {"scripts/board.sh": bs}, "chore: board.sh 填入看板 id（bootstrap）")
    prof = os.path.join(cfg["work"], "templates/org-profile/README.md")
    ps = open(prof, encoding="utf-8").read()
    ps2 = re.sub(rf"github.com/orgs/{re.escape(org)}/projects/\d+", f"github.com/orgs/{org}/projects/{info['number']}", ps)
    if ps2 != ps:
        open(prof, "w", encoding="utf-8").write(ps2)
    # 例会记录 issue 进看板
    for r in issue_repos(cfg):
        url = f"https://github.com/{org}/{r}/issues/1"
        if exists(f"repos/{org}/{r}/issues/1"):
            run(["bash", bs, "add", url, "S"], write=True)
    say(f"✓ board：看板 #{info['number']}，id 已写进 wiki/scripts/board.sh")


def step_profile(cfg):
    P = os.path.join(cfg["work"], "templates/org-profile")
    push_files(cfg, ".github-private", tree(P, "profile"), "docs: org 主页（bootstrap）")
    say("✓ profile：主页里的「正在做」「仓库表」请按项目改（见 AGENT-BOOTSTRAP.md 第 3 步）")


def step_code_repos(cfg):
    T = os.path.join(cfg["work"], "templates")
    for c in cfg["code_repos"]:
        f = {"CLAUDE.md": f"{T}/CLAUDE.md", "GEMINI.md": f"{T}/GEMINI.md", "AGENTS.md": f"{T}/AGENTS.md",
             ".github/pull_request_template.md": f"{T}/code-repo/pull_request_template.md",
             ".github/CODEOWNERS": f"{T}/code-repo/CODEOWNERS"}
        if c["kind"] == "own":
            f["README.md"] = os.path.join(cfg["work"], f"README-{c['name']}.md")
        else:
            fork = os.path.join(cfg["work"], f"FORK-{c['name']}.md")
            if not os.path.exists(fork):
                shutil.copyfile(f"{T}/FORK.md", fork)
            if open(fork, encoding="utf-8").read() == open(f"{T}/FORK.md", encoding="utf-8").read():
                say(f"  ⚠ {c['name']} 的 FORK.md 还是样例原文，按第 9 章改写 {fork} 后重跑 --only code-repos")
            f["FORK.md"] = fork
        push_files(cfg, c["name"], f, "chore: 本 org 的约定文件（bootstrap）", branch=c.get("default_branch"))
        dev = [b for b in (c.get("agents_branches") or []) if b != c.get("default_branch", "main")]
        for b in dev:
            if not exists(f"repos/{cfg['org']}/{c['name']}/branches/{b}"):
                ref = f"repos/{cfg['org']}/{c['name']}/git/ref/heads/{c.get('default_branch', 'main')}"
                sha = gh("api", ref, "--jq", ".object.sha", check=False) if exists(ref) else ("<default-branch-sha>" if DRY else "")
                if sha:
                    gh("api", "-X", "POST", f"repos/{cfg['org']}/{c['name']}/git/refs", "-f", f"ref=refs/heads/{b}", "-f", f"sha={sha}", write=True)
                    say(f"  {c['name']}：{'（plan）将' if DRY else ''}从默认分支拉出开发分支 {b}")
    say("✓ code-repos")


def step_sync_agents(cfg):
    """建站期间：所有目标分支直接推 AGENTS.md（之后的规则变更才用 sync-agents.sh 开 PR）。"""
    T = os.path.join(cfg["work"], "templates")
    for c in cfg["code_repos"]:
        for b in c.get("agents_branches") or []:
            if b == c.get("default_branch", "main"):
                continue
            push_files(cfg, c["name"], {"AGENTS.md": f"{T}/AGENTS.md", "CLAUDE.md": f"{T}/CLAUDE.md", "GEMINI.md": f"{T}/GEMINI.md"},
                       "chore: AGENTS.md（bootstrap）", branch=b)
    say("✓ sync-agents：所有目标分支的 AGENTS.md 与 wiki 一致")


def step_invite(cfg):
    org = cfg["org"]
    pending = gh("api", f"orgs/{org}/invitations", "--jq", "[.[].login]", check=False) or "[]"
    pending = set(json.loads(pending)) if pending.startswith("[") else set()
    for team, people in cfg["members"].items():
        for p in people or []:
            if p in pending or exists(f"orgs/{org}/members/{p}"):
                if exists(f"orgs/{org}/members/{p}") and not exists(f"orgs/{org}/teams/{team}/memberships/{p}"):
                    gh("api", "-X", "PUT", f"orgs/{org}/teams/{team}/memberships/{p}", write=True)
                continue
            uid = gh("api", f"users/{p}", "--jq", ".id", check=False)
            if not uid:
                say(f"  ⚠ 账号 {p} 不存在，跳过")
                continue
            tid = gh("api", f"orgs/{org}/teams/{team}", "--jq", ".id", check=False) if exists(f"orgs/{org}/teams/{team}") else "<team-id>"
            role = "admin" if p in cfg["owners"] else "direct_member"
            gh("api", "-X", "POST", f"orgs/{org}/invitations", "-F", f"invitee_id={uid}", "-F", f"team_ids[]={tid}",
               "-f", f"role={role}", write=True)
            say(f"  {'（plan）将邀请' if DRY else '已邀请'} {p} → {team}（{role}）")
    say("✓ invite：邀请 7 天有效，请对方在 GitHub 通知或邮箱里接受")


FUNCS = {"preflight": step_preflight, "org": step_org, "teams": step_teams, "repos": step_repos,
         "grants": step_grants, "labels": step_labels, "meeting-issues": step_meeting_issues,
         "wiki": step_wiki, "issue-repos": step_issue_repos, "board": step_board, "profile": step_profile,
         "code-repos": step_code_repos, "sync-agents": step_sync_agents, "invite": step_invite}


def main():
    global DRY
    if len(sys.argv) < 3 or sys.argv[1] not in ("plan", "render", "apply", "verify"):
        print(__doc__)
        sys.exit(2)
    cmd, cfg = sys.argv[1], load_cfg(sys.argv[2])
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
        bad = [s for s in only if s not in STEPS]
        if bad:
            die(f"未知步骤 {bad}；可选：{','.join(STEPS)}")
    if cmd == "verify":
        os.execvp(sys.executable, [sys.executable, os.path.join(HERE, "verify.py"), sys.argv[2]])
    if cmd == "render":
        render(cfg)
        return
    DRY = cmd == "plan"
    if not os.path.exists(cfg["work"]):
        render(cfg)
    for s in STEPS:
        if only and s not in only and s != "preflight":
            continue
        say(f"── {s}")
        FUNCS[s](cfg)
    say("\n完成。下一步：python3 bootstrap/verify.py " + sys.argv[2] + "，再按 AGENT-BOOTSTRAP.md 第 5 步把人要做的事交给人。")


if __name__ == "__main__":
    main()
