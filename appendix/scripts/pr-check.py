#!/usr/bin/env python3
"""PR 正文自查：必须关联 issue；「和原计划的偏差」一栏不能删、不能空。

org 停用 GitHub Actions 后，提 PR 或合并前在本地跑：
    python3 pr-check.py < /tmp/body.md
    gh pr view <号> -R <org>/<repo> --json body --jq .body | python3 pr-check.py
    python3 pr-check.py --numeric < /tmp/body.md   # 代码仓里动了 src/ 或依赖的 PR，另查「数值影响」栏
退出码 0 = 通过，1 = 不通过。前两条规则与原项目的 .github/workflows/pr-check.yml 相同；
--numeric 对应原项目 maxtext 仓的第三条规则。本脚本是本书从原工作流里抽出来的，原 org 里没有这个文件。
"""
import re
import sys

numeric = '--numeric' in sys.argv[1:]
body = sys.stdin.read()
errs = []
if not re.search(r'(?i)\b(close[sd]?|fix(e[sd])?|resolve[sd]?|refs?)\s+([\w.-]+/[\w.-]+)?#\d+', body):
    errs.append("没有关联 issue：正文要写 `Closes <org>/<repo>#号` 或 `Refs <org>/<repo>#号`")
m = re.search(r'##\s*和原计划的偏差[^\n]*\n(.*?)(?=\n##\s|\Z)', body, re.S)
if not m:
    errs.append("缺少「## 和原计划的偏差」一栏（没有偏差写「无」，但不能删）")
elif not re.sub(r'<!--.*?-->', '', m.group(1), flags=re.S).strip():
    errs.append("「和原计划的偏差」一栏是空的（没有偏差写「无」）")
if numeric:
    n = re.search(r'##\s*数值影响[^\n]*\n(.*?)(?=\n##\s|\Z)', body, re.S)
    first = re.sub(r'<!--.*?-->', '', n.group(1), flags=re.S).strip().splitlines()[0].strip() if n and re.sub(r'<!--.*?-->', '', n.group(1), flags=re.S).strip() else ''
    if first not in ('数学不变', '会改数值', '升级依赖'):
        errs.append("「数值影响」栏第一行必须是 数学不变 / 会改数值 / 升级依赖 之一")
for e in errs:
    print(f"✗ {e}")
if not errs:
    print("✓ 通过")
sys.exit(1 if errs else 0)
