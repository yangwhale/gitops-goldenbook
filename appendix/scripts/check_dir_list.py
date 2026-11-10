#!/usr/bin/env python3
"""检查 repro/README.md 的「目录清单」和 repro/issues/ 下的实际目录一一对应。

用法（在 issue 仓的根目录）：
    python3 repro/common/check_dir_list.py repro <本仓库全名>
    python3 repro/common/check_dir_list.py repro northpeak/project-management
    python3 repro/common/check_dir_list.py repro northpeak/project-management-infra

规则：
- 「目录清单」表里列的目录必须存在
- issues/ 下带 card.yaml 的目录（验证过的复现）必须登记在表里；card.yaml 的 issue 必须指向本仓库；目录名以 issue 号开头
- 不带 card.yaml 的目录（客户放的材料，可直接推）不要求登记、不报错——检查会扫整棵树，报错会让别人无关的 PR 失败

两个 issue 仓的编号各自从 1 开始，所以 card.yaml 指向另一个仓库的目录一律报错：它的复现应该放在那个仓库的 repro/。
"""
import os
import re
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "repro"
this_repo = sys.argv[2] if len(sys.argv) > 2 else None
if not this_repo or "/" not in this_repo:
    print("用法：check_dir_list.py <repro 目录> <本仓库全名，如 northpeak/project-management>")
    sys.exit(2)

readme = open(os.path.join(root, "README.md"), encoding="utf-8").read()
m = re.search(r"^## 目录清单[^\n]*\n(.*?)(?=^## |\Z)", readme, re.M | re.S)
if not m:
    print("::error::repro/README.md 缺少「## 目录清单」一节")
    sys.exit(1)
listed = set(re.findall(r"`issues/([^/`]+)/`", m.group(1)))
issues_dir = os.path.join(root, "issues")
actual = {d for d in os.listdir(issues_dir) if os.path.isdir(os.path.join(issues_dir, d))} if os.path.isdir(issues_dir) else set()
carded = {d for d in actual if os.path.isfile(os.path.join(issues_dir, d, "card.yaml"))}

errs = [f"issues/{d}/ 有 card.yaml，但不在 repro/README.md 的「目录清单」表里" for d in sorted(carded - listed)]
errs += [f"「目录清单」表里的 issues/{d}/ 不存在" for d in sorted(listed - actual)]
for d in sorted(carded):
    card = open(os.path.join(issues_dir, d, "card.yaml"), encoding="utf-8").read()
    im = re.search(r"^issue:\s*([\w.-]+/[\w.-]+)#\d+", card, re.M)
    if not im:
        errs.append(f"issues/{d}/card.yaml 缺少 issue: <仓库全名>#<号>")
        continue
    if im.group(1) != this_repo:
        errs.append(f"issues/{d}/card.yaml 指向 {im.group(1)}：复现放在 issue 所在仓库的 repro/，不放这里")
        continue
    if not d[:1].isdigit():
        errs.append(f"issues/{d}/ 目录名要以本仓库的 issue 号开头：<号>-<简述>")

for e in errs:
    print(f"::error::{e}")
print(f"目录清单检查（{this_repo}）：issues/ 下 {len(actual)} 个目录（{len(carded)} 个带 card.yaml），表里 {len(listed)} 个，问题 {len(errs)} 个")
sys.exit(1 if errs else 0)
