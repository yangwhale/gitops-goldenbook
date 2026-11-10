#!/usr/bin/env python3
"""smoke.py —— 建站后走一遍真实流程（第 15 章第 14 步的自动部分），跑完自己清理。

    python3 bootstrap/smoke.py org-config.yaml

做的事：在 project-management 建一条测试 issue → board.sh add → 在第一个自研代码仓开分支提 PR（Closes 那条 issue）
→ 看板变 In Progress → 合并 PR → issue 自动关闭、看板变 Done → 删除测试 issue 和分支。
需要一个 kind: own 的代码仓（默认分支就是合并目标）。没有的话只测 issue 和看板那一半。
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bootstrap import load_cfg  # noqa: E402

OK = []


def gh(*a, check=True):
    r = subprocess.run(["gh", *a], capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"✗ gh {' '.join(a)}\n{r.stderr[:500]}")
        sys.exit(1)
    return r.stdout.strip()


def step(name, ok):
    OK.append(ok)
    print(("✓ " if ok else "✗ ") + name)


def status_of(org, number, title):
    q = '{organization(login:"%s"){projectsV2(first:20){nodes{title items(first:100){nodes{content{... on Issue{number repository{name}}} fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}}' % org
    d = json.loads(gh("api", "graphql", "-f", f"query={q}"))
    for p in d["data"]["organization"]["projectsV2"]["nodes"]:
        if p["title"] != title:
            continue
        for it in p["items"]["nodes"]:
            c = it["content"] or {}
            if c.get("number") == number and c.get("repository", {}).get("name") == "project-management":
                return (it["fieldValueByName"] or {}).get("name")
    return None


def wait_status(org, number, title, want, secs=60):
    for _ in range(secs // 5):
        s = status_of(org, number, title)
        if s == want:
            return s
        time.sleep(5)
    return status_of(org, number, title)


def main():
    cfg = load_cfg(sys.argv[1])
    org, title = cfg["org"], cfg["org_title"]
    board = f"gh api repos/{org}/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s --"
    body = "### 目标\n\nsmoke.py 的测试 issue，跑完自动删除。\n\n### 跟哪块有关\n\n不知道 / 都不是\n"
    url = gh("issue", "create", "-R", f"{org}/project-management", "--title", "冒烟测试：走一遍 issue 到 PR 的流程",
             "--label", "type/feat", "--body", body)
    num = int(url.rsplit("/", 1)[1])
    print(f"测试 issue：{url}")
    subprocess.run(f"{board} add {url} S", shell=True, check=True, capture_output=True)
    step("board.sh add 后看板 Status = Triage", wait_status(org, num, title, "Triage") == "Triage")

    own = next((c for c in cfg["code_repos"] if c["kind"] == "own"), None)
    br = None
    if own:
        repo, base = own["name"], own.get("default_branch", "main")
        br = f"chore/{num}-smoke"
        sha = gh("api", f"repos/{org}/{repo}/git/ref/heads/{base}", "--jq", ".object.sha")
        gh("api", "-X", "POST", f"repos/{org}/{repo}/git/refs", "-f", f"ref=refs/heads/{br}", "-f", f"sha={sha}")
        gh("api", "-X", "PUT", f"repos/{org}/{repo}/contents/SMOKE.md", "-f", "message=chore: 冒烟测试", "-f",
           "content=" + __import__("base64").b64encode("smoke\n".encode()).decode(), "-f", f"branch={br}")
        pr_body = f"## 做了什么\n\n冒烟测试。\n\n## 关联\n\nCloses {org}/project-management#{num}\n\n## 怎么验证的\n\nsmoke.py\n\n## 和原计划的偏差\n\n无\n"
        pr = gh("api", "-X", "POST", f"repos/{org}/{repo}/pulls", "-f", "title=chore: 冒烟测试", "-f", f"head={br}",
                "-f", f"base={base}", "-f", f"body={pr_body}", "--jq", ".number")
        chk = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "appendix/scripts/pr-check.py")],
                             input=pr_body, capture_output=True, text=True)
        step("pr-check.py 通过", chk.returncode == 0)
        step("PR 关联 issue 后看板 Status = In Progress", wait_status(org, num, title, "In Progress") == "In Progress")
        gh("api", "-X", "PUT", f"repos/{org}/{repo}/pulls/{pr}/merge", "-f", "merge_method=squash")
        time.sleep(5)
        state = gh("api", f"repos/{org}/project-management/issues/{num}", "--jq", ".state")
        step("PR 合进默认分支后 issue 自动关闭", state == "closed")
        step("看板 Status = Done", wait_status(org, num, title, "Done") == "Done")
        # 清理：撤掉 SMOKE.md
        fsha = gh("api", f"repos/{org}/{repo}/contents/SMOKE.md", "--jq", ".sha", check=False)
        if fsha:
            gh("api", "-X", "DELETE", f"repos/{org}/{repo}/contents/SMOKE.md", "-f", "message=chore: 撤掉冒烟测试文件", "-f", f"sha={fsha}", "-f", f"branch={base}")
        gh("api", "-X", "DELETE", f"repos/{org}/{repo}/git/refs/heads/{br}", check=False)
    else:
        gh("issue", "close", url)
        step("issue 关闭后看板 Status = Done", wait_status(org, num, title, "Done") == "Done")

    gh("issue", "delete", url, "--yes")
    print("已删除测试 issue")
    print(f"\n{sum(OK)}/{len(OK)} 通过")
    sys.exit(0 if all(OK) else 1)


if __name__ == "__main__":
    main()
