#!/usr/bin/env python3
"""verify.py —— 只读检查一个 org 是否搭成了本书描述的样子（附录 D.1 的机器版）。

    python3 bootstrap/verify.py org-config.yaml

每条检查输出 PASS / FAIL / WARN；有 FAIL 时退出码 1。不改任何东西。
需要人用客户账号核的几项（GKE 组看不到训练仓、主页按钮能显示）在最后列成 TODO。
"""
import base64
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bootstrap import load_cfg, issue_repos, subteams  # noqa: E402

RESULTS = []


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def ghj(*args):
    out = gh(*args)
    try:
        return json.loads(out) if out else None
    except json.JSONDecodeError:
        return None


def check(name, ok, detail="", warn=False):
    tag = "PASS" if ok else ("WARN" if warn else "FAIL")
    RESULTS.append((tag, name, detail))
    print(f"{tag:4}  {name}" + (f" —— {detail}" if detail and not ok else ""))


def content(org, repo, path, ref=None):
    q = f"repos/{org}/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
    c = gh("api", q, "--jq", ".content")
    return base64.b64decode(c).decode("utf-8", "replace") if c else None


def c_name_is_code_readme(repo, path, cfg):
    return path == "README.md" and any(c["name"] == repo for c in cfg["code_repos"])


def main():
    cfg = load_cfg(sys.argv[1])
    org = cfg["org"]
    print(f"检查 {org}\n")

    o = ghj("api", f"orgs/{org}") or {}
    check("org 默认权限 None", o.get("default_repository_permission") == "none", str(o.get("default_repository_permission")))
    check("禁止 fork 私有仓", o.get("members_can_fork_private_repositories") is False)
    if cfg["actions"] == "disabled":
        a = ghj("api", f"orgs/{org}/actions/permissions") or {}
        check("Actions 已停用", a.get("enabled_repositories") == "none", str(a))

    teams = {t["slug"]: t for t in (ghj("api", f"orgs/{org}/teams", "--paginate") or [])}
    for t in ["maintainers", "googlers", "customer", "partners", "observers"] + subteams(cfg):
        check(f"团队 {t} 存在", t in teams)
    for t in subteams(cfg):
        if t in teams:
            check(f"{t} 的父团队是 customer", (teams[t].get("parent") or {}).get("slug") == "customer")

    # 一人一团队
    seen = {}
    for t in teams:
        for m in ghj("api", f"orgs/{org}/teams/{t}/members", "--paginate", "--jq", "[.[].login]") or []:
            seen.setdefault(m, []).append(t)
    multi = {m: ts for m, ts in seen.items() if len([x for x in ts if x not in ("customer",)]) > 1}
    check("一人只进一个团队", not multi, json.dumps(multi, ensure_ascii=False), warn=True)

    repos = {r["name"]: r for r in (ghj("api", f"orgs/{org}/repos", "--paginate") or [])}
    expect = ["wiki", ".github-private"] + issue_repos(cfg) + [c["name"] for c in cfg["code_repos"]]
    for r in expect:
        check(f"仓库 {r} 存在", r in repos)
    for name, r in repos.items():
        check(f"{name} 是私有仓", r.get("private") is True)
    for r in ["wiki"] + issue_repos(cfg):
        if r in repos:
            check(f"{r} 开 Issues", repos[r].get("has_issues") is True)
    for c in cfg["code_repos"]:
        if c["name"] in repos:
            check(f"{c['name']} 关 Issues（只收 PR）", repos[c["name"]].get("has_issues") is False)
    for name, r in repos.items():
        if not r.get("archived"):
            check(f"{name} 关 Wiki", r.get("has_wiki") is False, warn=True)

    # 授权
    def perm(team, repo):
        p = ghj("api", f"orgs/{org}/teams/{team}/repos/{org}/{repo}", "-H", "Accept: application/vnd.github.v3.repository+json")
        return (p or {}).get("role_name")
    want = [("maintainers", "wiki", "admin"), ("googlers", "wiki", "maintain"), ("customer", "wiki", "write"),
            ("observers", "project-management", "read")]
    for g in cfg["customer_groups"]:
        want += [(g["team"], r, "write") for r in g["repos"]]
    for t, r, p in want:
        got = perm(t, r)
        check(f"授权 {t} → {r} = {p}", got == p, f"实际 {got}")
    check("customer 父团队对 project-management 无直接授权", perm("customer", "project-management") in (None, ""), warn=True)
    for g in cfg["customer_groups"]:
        for r in issue_repos(cfg):
            if r not in g["repos"]:
                check(f"{g['team']} 看不到 {r}", perm(g["team"], r) in (None, ""))

    # 标签
    want_labels = {"type/bug", "type/feat", "type/docs", "type/chore", "size/S", "size/L", "P0", "tracker"}
    for r in issue_repos(cfg) + ["wiki"]:
        labels = set(ghj("api", f"repos/{org}/{r}/labels", "--paginate", "--jq", "[.[].name]") or [])
        check(f"{r} 标签齐全", want_labels <= labels, f"缺 {sorted(want_labels - labels)}")
        check(f"{r} 没有 GitHub 默认标签", not ({"bug", "enhancement", "good first issue"} & labels), warn=True)

    # 文件
    wiki_agents = content(org, "wiki", "AGENTS.md")
    check("wiki 有 AGENTS.md", bool(wiki_agents))
    for need in ["CLAUDE.md", "README.md", "scripts/board.sh", "scripts/sync-agents.sh", "scripts/pr-check.py", "docs/rfc/template.md",
                 "docs/onboarding/permissions.md", ".github/ISSUE_TEMPLATE/access.yml"]:
        check(f"wiki/{need}", content(org, "wiki", need) is not None)
    board_sh = content(org, "wiki", "scripts/board.sh") or ""
    check("board.sh 已填入真实看板 id", "PVT_xxxx" not in board_sh and "PROJECT=PVT_" in board_sh)
    for r in issue_repos(cfg):
        for need in ["AGENTS.md", "CLAUDE.md", "README.md", ".github/ISSUE_TEMPLATE/config.yml", ".github/ISSUE_TEMPLATE/1-bug.yml",
                     ".github/pull_request_template.md", ".github/CODEOWNERS", "meetings/README.md", "meetings/_template/notes.md",
                     "repro/README.md", "repro/common/check_dir_list.py", "library/README.md", "recipes/README.md"]:
            check(f"{r}/{need}", content(org, r, need) is not None)
        cy = content(org, r, ".github/ISSUE_TEMPLATE/config.yml") or ""
        check(f"{r} 关闭空白 issue", "blank_issues_enabled: false" in cy)
        if cfg["issue_repos"] == "one":
            check(f"{r} 的 config.yml 不指向不存在的 infra 仓", "project-management-infra" not in cy)
    if cfg["issue_repos"] == "two":
        cy = content(org, "project-management-infra", ".github/ISSUE_TEMPLATE/config.yml") or ""
        check("infra 的 config.yml 不指向训练仓（GKE 组打不开）", "project-management/issues" not in cy)

    # AGENTS.md 一致
    targets = [(r, None) for r in issue_repos(cfg)]
    for c in cfg["code_repos"]:
        for b in c.get("agents_branches") or [c.get("default_branch", "main")]:
            targets.append((c["name"], b))
    for repo, ref in targets:
        got = content(org, repo, "AGENTS.md", ref)
        check(f"{repo}{'@' + ref if ref else ''} 的 AGENTS.md 与 wiki 一致", got is not None and got == wiki_agents)

    # 示例名残留
    for repo, path in [("wiki", "AGENTS.md"), ("wiki", "README.md"), ("project-management", "README.md"), (".github-private", "profile/README.md")]:
        s = (content(org, repo, path) or "").lower()
        check(f"{repo}/{path} 没有示例名残留", "northpeak" not in s and "modelx" not in s)

    # 例会记录 issue
    for r in issue_repos(cfg):
        i = ghj("api", f"repos/{org}/{r}/issues/1") or {}
        check(f"{r}#1 是例会记录 issue", (i.get("title") or "") == cfg["meeting_titles"][r], i.get("title") or "不存在")

    # 主页
    prof = content(org, ".github-private", "profile/README.md")
    check(".github-private/profile/README.md", prof is not None)

    # 领域残留与占位符（换了领域的项目才查残留；占位符一律查）
    import re as _re
    key_files = [("wiki", "AGENTS.md"), ("wiki", "README.md"), (".github-private", "profile/README.md")]
    for r in issue_repos(cfg):
        key_files += [(r, "README.md"), (r, "library/README.md"), (r, "recipes/README.md"), (r, "repro/README.md"),
                      (r, ".github/ISSUE_TEMPLATE/1-bug.yml"), (r, ".github/ISSUE_TEMPLATE/config.yml")]
    for c in cfg["code_repos"]:
        key_files += [(c["name"], "README.md" if c["kind"] == "own" else "FORK.md"), (c["name"], ".github/pull_request_template.md")]
    residue = ["TPU", "MaxText", "libtpu", "JAX", "Pallas", "Tokamax", "GKE", "numerics-kit", "gke-component", "v5p", "v7x"]
    for repo, path in key_files:
        txt = content(org, repo, path, None) or ""
        ph = sorted(set(_re.findall(r"<(?:[^<>\n/!]{1,30})>", txt)) - {"org", "repo"})
        ph = [x for x in ph if any("\u4e00" <= ch <= "\u9fff" for ch in x)]
        syntax_files = ("AGENTS.md", "repro/README.md", ".github/pull_request_template.md")
        if c_name_is_code_readme(repo, path, cfg):
            ph = []
        if ph and not path.endswith(syntax_files) and path != "README.md" or (ph and repo == "wiki" and path == "README.md") or (ph and repo == ".github-private"):
            check(f"{repo}/{path} 没有未填的占位符", False, "、".join(ph[:6]), warn=True)
        if cfg["domain"] == "other":
            hit = [w for w in residue if w in txt]
            if hit:
                check(f"{repo}/{path} 没有原项目领域的残留", False, "、".join(hit), warn=True)

    # 看板
    q = '{organization(login:"%s"){projectsV2(first:20){nodes{title public number readme workflows(first:20){nodes{name enabled}} views(first:20){nodes{name filter}} fields(first:50){nodes{... on ProjectV2SingleSelectField{name options{name}}}}}}}}' % org
    d = ghj("api", "graphql", "-f", f"query={q}") or {}
    projs = (((d.get("data") or {}).get("organization") or {}).get("projectsV2") or {}).get("nodes") or []
    p = next((x for x in projs if x["title"] == cfg["org_title"]), None)
    check(f"看板「{cfg['org_title']}」存在", p is not None)
    if p:
        check("看板是私有的", p["public"] is False)
        f = {x["name"]: [o["name"] for o in x["options"]] for x in p["fields"]["nodes"] if x}
        check("Status 有 6 个状态", f.get("Status") == ["Triage", "Design Pending", "Ready to Develop", "In Progress", "Blocked", "Done"], str(f.get("Status")))
        check("Size 字段 S / L", f.get("Size") == ["S", "L"])
        wf = {w["name"]: w["enabled"] for w in p["workflows"]["nodes"]}
        for w in ["Item added to project", "Item closed", "Pull request linked to issue", "Pull request merged", "Auto-close issue", "Auto-add sub-issues to project", "Item reopened"]:
            check(f"看板规则「{w}」打开", wf.get(w) is True)
        filters = " ".join(v["filter"] or "" for v in p["views"]["nodes"])
        check("看板视图筛选指向本 org", "northpeak" not in filters and (org in filters or cfg["issue_repos"] == "one"), filters)
        check("主页里的看板链接指向这块看板", f"/orgs/{org}/projects/{p['number']}" in (prof or ""), f"看板是 #{p['number']}")

    # 汇总
    fails = [r for r in RESULTS if r[0] == "FAIL"]
    warns = [r for r in RESULTS if r[0] == "WARN"]
    print(f"\n{len(RESULTS)} 项：{len(RESULTS) - len(fails) - len(warns)} PASS，{len(warns)} WARN，{len(fails)} FAIL")
    print("""
需要人核的（脚本做不了）：
  [ ] 邀请都已接受：gh api orgs/%s/invitations 为空
%s
  [ ] 用客户账号打开 https://github.com/%s → 看到成员版主页，按钮图片能显示
  [ ] 两个 issue 仓的 issues/new/choose 页面，每个模板都能点开
  [ ] 让一个 AI 助手「先读 AGENTS.md，再提一个 issue」，模板字段、标签、看板都对""" % (org, "\n".join(
        f"  [ ] 用客户 {g['team']} 组（{g['desc']}）的账号打开 " + "、".join(g["repos"]) + " 和 wiki → 都能打开、能提 issue"
        + ("；打开 " + "、".join(r for r in issue_repos(cfg) if r not in g["repos"]) + " → 404" if any(r not in g["repos"] for r in issue_repos(cfg)) else "")
        for g in cfg["customer_groups"]), org))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
