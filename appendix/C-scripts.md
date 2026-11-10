# 附录 C 脚本

所有脚本在 [`scripts/`](scripts/) 下，只依赖 `gh`、`jq`、`python3` 标准库。

| 脚本 | 放到 | 用法 | 拷贝后要改 | 见 |
|---|---|---|---|---|
| `board.sh` | `wiki/scripts/` | `board.sh add <URL> [S\|L]`、`size <URL> S\|L`、`status <URL> "<状态>"` | 顶部的 `PROJECT`、`F_STATUS`、`F_SIZE`、两个选项表；注释里的 `northpeak` | 第 5 章 5.6 |
| `sync-agents.sh` | `wiki/scripts/` | `bash scripts/sync-agents.sh <org>/wiki#<issue>` | `ORG`、`TARGETS`（含每个仓库的目标分支）、`DIRECT` | 第 13 章 13.6 |
| `pr-check.py` | `wiki/scripts/` | `python3 pr-check.py < body.md` | 无 | 第 7 章 7.4 |
| `check_dir_list.py` | 每个 issue 仓的 `repro/common/` | `python3 repro/common/check_dir_list.py repro <org>/<本仓库>` | 无（本仓库名作参数传入，两个 issue 仓用同一份） | 第 10 章 10.3 |
| `setup-labels.sh` | 建站时在本地跑，不用放进 org | `setup-labels.sh <org>/<repo> training\|infra\|wiki` | `area/*` 换成你的领域 | 第 4 章、第 15 章第 5 步 |

## 测试记录

| 脚本 | 怎么测的 | 结果 |
|---|---|---|
| `pr-check.py` | 一份合规正文；一份没有关联 issue、偏差栏只有注释的正文 | 前者通过；后者报两条错，退出码 1 |
| `check_dir_list.py` | 每个 issue 仓的 `repro/common/` | `python3 repro/common/check_dir_list.py repro <org>/<本仓库>` | 无（本仓库名作参数传入，两个 issue 仓用同一份） | 第 10 章 10.3 |
| `setup-labels.sh` | 新建临时私有仓库跑 `training`，然后删掉仓库 | 得到 22 个标签，与原项目训练仓一致，默认标签全部删掉 |
| `board.sh`、`sync-agents.sh` | 原项目实际在用的版本，只替换了 org 名和 id | — |

## 从仓库直接取来执行

在任何目录下，不 clone `wiki`：

```bash
gh api repos/<org>/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- add <URL> S
gh api repos/<org>/wiki/contents/scripts/pr-check.py --jq .content | base64 -d > /tmp/pr-check.py && python3 /tmp/pr-check.py < body.md
```
