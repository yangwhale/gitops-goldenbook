#!/usr/bin/env python3
"""teardown.py —— 只用于演练：把 bootstrap.py 在一个**沙箱 org** 里建的东西全部删掉。

    python3 bootstrap/teardown.py org-config.yaml --yes-delete-everything-in <org>

删除：org-config 里列出的仓库（wiki、issue 仓、.github-private、code_repos）、八个团队、标题为 org_title 的看板。
不删 org 本身，不动配置里没列的仓库。需要令牌带 delete_repo（gh auth refresh -s delete_repo）。

⚠ 这是不可恢复的删除。只在专门用来演练的空 org 上用，绝不要对客户的 org 跑。
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bootstrap import load_cfg, issue_repos  # noqa: E402


def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True)


def main():
    cfg = load_cfg(sys.argv[1])
    org = cfg["org"]
    if sys.argv[2:4] != ["--yes-delete-everything-in", org]:
        print(__doc__)
        sys.exit(2)
    repos = ["wiki", ".github-private"] + issue_repos(cfg) + [c["name"] for c in cfg["code_repos"]]
    for r in repos:
        res = gh("repo", "delete", f"{org}/{r}", "--yes")
        print(("删除仓库 " if res.returncode == 0 else "跳过仓库 ") + r)
    for t in ["training", "gke", "network", "customer", "maintainers", "googlers", "partners", "observers"]:
        res = gh("api", "-X", "DELETE", f"orgs/{org}/teams/{t}")
        print(("删除团队 " if res.returncode == 0 else "跳过团队 ") + t)
    q = '{organization(login:"%s"){projectsV2(first:50){nodes{id title}}}}' % org
    d = json.loads(gh("api", "graphql", "-f", f"query={q}").stdout or "{}")
    for p in ((d.get("data") or {}).get("organization") or {}).get("projectsV2", {}).get("nodes", []):
        if p["title"] == cfg["org_title"]:
            gh("api", "graphql", "-f", f'query=mutation{{deleteProjectV2(input:{{projectId:"{p["id"]}"}}){{clientMutationId}}}}')
            print("删除看板 " + p["title"])


if __name__ == "__main__":
    main()
