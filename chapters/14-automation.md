# 第 14 章 脚本与自动化

第 1 章原则 2：规则要么交给机器执行，要么卡在必经之路上。「交给机器」的部分就是五个小脚本，外加 GitHub 看板自带的规则。

## 14.1 自动化的边界

原则见第 1 章原则 4。落到每个动作上：

| 动作 | 谁做 |
|---|---|
| issue 关闭 → 看板 Done | GitHub 看板内置规则 |
| 新 issue 打 type 标签 | issue 模板 |
| 加进看板、设 Size / Status | `board.sh`（人或 AI 助手调用） |
| `AGENTS.md` 分发到各仓库 | `sync-agents.sh` |
| PR 正文有没有关联 issue、偏差栏 | `pr-check`（原为 Actions，现为本地脚本） |
| `repro/` 目录清单和实际目录一致 | `check_dir_list.py` |
| 上游组件同步 | 厂商一侧的定时任务（第 9 章），满足三个条件才自动合并 |
| 写周报、会议摘要、issue 拆分建议 | LLM，人审过再发 |
| 判断 issue 是否完成、要不要关 | **人** |

## 14.2 五个脚本

| 脚本 | 放哪 | 干什么 | 文件 |
|---|---|---|---|
| `board.sh` | `wiki/scripts/` | 加进看板、设 Size、设 Status | [appendix/scripts/board.sh](../appendix/scripts/board.sh) |
| `sync-agents.sh` | `wiki/scripts/` | 把 `AGENTS.md` 同步到各仓库 | [appendix/scripts/sync-agents.sh](../appendix/scripts/sync-agents.sh) |
| `pr-check.py` | `wiki/scripts/` | 本地检查 PR 正文 | [appendix/scripts/pr-check.py](../appendix/scripts/pr-check.py) |
| `check_dir_list.py` | 每个 issue 仓的 `repro/common/` | 检查复现目录清单 | [appendix/scripts/check_dir_list.py](../appendix/scripts/check_dir_list.py) |
| `setup-labels.sh` | 不放进 org，建站时本地跑 | 删 GitHub 默认标签、按角色建标签表 | [appendix/scripts/setup-labels.sh](../appendix/scripts/setup-labels.sh) |

共同的设计：

- **只依赖 `gh`、`jq`、`python3` 标准库**。任何人的机器上、任何 AI 助手的沙箱里都能跑。例外：`board.sh` 用了关联数组（`declare -A`），要 bash 4 以上；macOS 自带的是 bash 3.2，Mac 用户先 `brew install bash`
- **不需要 clone 就能用**：`board.sh` 可以 `gh api repos/<org>/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- ...` 直接从仓库取来执行。AI 助手在 `maxtext` 里工作时，不用去 clone `wiki`
- **幂等**：`board.sh add` 对已在看板上的条目返回已有的条目 id；`sync-agents.sh` 对已一致的目标跳过。重复跑不会出错
- **出错就停**：`set -euo pipefail`；参数不对打印用法、退出码 2

### `board.sh`

```bash
board.sh add    <issue或PR的URL> [S|L]
board.sh size   <URL> S|L
board.sh status <URL> "Design Pending"|"Ready to Develop"|"Blocked"|...
```

脚本顶部写死看板和字段的 id。复刻时用第 5 章 5.6 的两条命令查出来替换。

### `sync-agents.sh`

```bash
bash scripts/sync-agents.sh <org>/wiki#<关联 issue>
```

逻辑见第 13 章 13.6。两个要注意的实现细节：

- 目标仓库还没有 `AGENTS.md` 时，取 sha 的 `gh api` 会失败。脚本用 `|| true` 吞掉，然后在 PUT 时只在拿到 sha 时才带 `sha` 参数（`${fsha:+-f sha="$fsha"}`）。原项目第一次给新仓库同步时就是卡在这里
- 比较用的是 GitHub API 返回的 base64 内容（去掉换行），不是解码后的文本，避免换行符差异带来的误判

### `pr-check.py`

```bash
python3 pr-check.py < /tmp/body.md
gh pr view <号> -R <org>/<repo> --json body --jq .body | python3 pr-check.py
```

本书从原项目的 `pr-check.yml` 抽成的本地脚本（原 org 里没有这个文件）。两条规则：正文里有 `Closes`/`Fixes`/`Resolves`/`Refs` + 可选的 `owner/repo` + `#号`；有「## 和原计划的偏差」一栏，去掉 HTML 注释后不为空。加 `--numeric` 再查第三条：「数值影响」栏第一行是「数学不变 / 会改数值 / 升级依赖」之一（原项目 `maxtext` 仓对动了 `src/` 或依赖的 PR 要求这一条）。

### `check_dir_list.py`

```bash
python3 repro/common/check_dir_list.py repro <org>/<本仓库>
```

规则见第 10 章。注意它对**不带 `card.yaml` 的目录只给警告**：那是客户的材料，报错会让别人无关的 PR 失败。

## 14.3 GitHub Actions：为什么停了

原项目一开始在每个仓库放了 `pr-check` 工作流（附录 B 有原文件），在 `repro/` 有 `dir-list-check`。建 org 第三周**整个 org 停用了 Actions**（org 设置 → Actions → Disable for all repositories）。原因：

- **免费档私有仓库的 Actions 分钟数有限**。不到一个月就烧完了 2,000 分钟的月度免费额度，大头是某个自研工具仓每次推送都跑的测试
- **失败通知打扰人**：检查一红就给相关的人发通知，而大部分红是测试环境的问题
- **免费档的检查本来就拦不住合并**（没有分支保护），检查失败只是一个红叉
- 提 PR 的人（以及 AI 助手）推之前已经自查过，CI 只是重复一遍

停用后的做法：

- `AGENTS.md` 第 4 节改为「org 已停用 GitHub Actions，没有 CI 替你检查：推之前自己核对这一条和下面的偏差栏，该跑的测试在本地跑完」
- 检查逻辑保留成本地脚本（`pr-check.py`、`check_dir_list.py`）
- 上游项目的私有副本里，上游自带的工作流本来就停用了

**复刻时的建议**：

| 情况 | 做法 |
|---|---|
| 免费档、人少 | 不开 Actions，用本地脚本 |
| 升级了 Team 档、要强制检查 | 开 Actions，只放 `pr-check` 这种秒级的检查；配合分支保护设为必过 |
| 有自托管 runner | 重的验证（训练回归、数值对齐）放自托管 runner，不占 GitHub 分钟数 |

无论哪种，`pr-check` 都应该只做**秒级的文本检查**。不要在每次推送时跑编译和测试——那是 Actions 分钟数被吃光的主要原因。

用命令停用：

```bash
gh api -X PUT orgs/<org>/actions/permissions -f enabled_repositories=none
gh api orgs/<org>/actions/permissions   # 确认 {"enabled_repositories":"none"}
```

## 14.4 评论命令触发的验证

如果有自托管的计算资源，可以做「在 PR 里评论 `/loss`，触发一次小规模训练对比」这类验证。规矩：

- 只对有仓库访问权的人生效；**外部 fork 的 PR 一律不触发**（防止外部代码拿到密钥）
- **跑完要把结论评论回 PR**，不能只回一条「已派发」
- 失败要区分「基础设施挂了」和「数字不对」（第 12 章）

## 14.5 厂商一侧的工具

厂商工程师（和他们的 AI 助手）在 org 外面还会有一些自己的工具：批量建 issue、发布检查、内部门禁（比如交付前检查 issue 链接和复现目录是否齐全）。

- 这些工具**不放进 org**（会带出内部依赖、内部链接）
- 但它们要**跟着 org 的结构变**：原项目把复现目录从独立仓库并进 issue 仓时，内部的 issue 工具、发布检查、内部门禁都要改「认哪个仓库」——RFC-0002 的「影响范围」里专门列了这一项，实施时还多发现一处漏改的
- RFC 的「影响范围」一节要列出厂商一侧受影响的工具

## 14.6 不做的自动化

原项目刻意**没有**做这些（RFC-0001 的「非目标」）：

- org 配置写成代码（Terraform 之类）
- 用 Actions 自动加看板、超时提醒、自动同步 `AGENTS.md`
- 按组件建标签

RFC-0001 把它们都留给了「第二阶段」。本书的看法：人少的阶段，这些自动化的维护成本高于收益，而且每一条都要先跑一段时间手工流程，才知道规则该怎么定。
**先手工跑通，再把稳定下来的那部分自动化。**

## 14.7 复刻清单

- [ ] 五个脚本拷进对应位置（`setup-labels.sh` 只在建站时本地跑），替换 org 和 id
- [ ] `board.sh` 用测试 issue 跑一遍
- [ ] `sync-agents.sh` 跑一遍
- [ ] 决定开不开 Actions；不开就在 org 设置里停掉，并在 `AGENTS.md` 写明「没有 CI，推前自查」
