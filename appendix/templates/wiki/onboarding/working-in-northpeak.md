# 在 NorthPeak 里怎么干活

这页讲 NorthPeak 的几个仓库各管什么、客户问题怎么记、代码怎么改。例子全部取自 NorthPeak POC 的真实记录。

## 仓库

| 仓库 | 放什么 | 不放什么 |
|---|---|---|
| `wiki` | 规矩（`AGENTS.md`）、守则、RFC、新人入门；规矩、流程、权限的 issue | 项目上的具体任务 |
| `project-management` | 训练与推理的 issue（作业里面的事），包括这一侧的跨仓任务；这一方向的 `library/`（给客户的文档，由 Google 维护）、`meetings/`（训练例会的纪要，由 Google 维护）、`recipes/`、`repro/`；`assets/issues/` 存 issue 用的截图。四个目录的改动走 PR，模板和截图直接推 | 代码 |
| `project-management-infra` | GKE on TPU 和网络的 issue（集群和节点层面），包括这一侧的跨仓任务；这一方向的 `library/`（给客户的文档，由 Google 维护）、`meetings/`（GKE、网络和全体例会的纪要，由 Google 维护）、`recipes/`、`repro/`；`assets/issues/` 存 issue 用的截图。四个目录的改动走 PR，模板和截图直接推 | 正在开发的组件代码（在各组件仓库） |
| `maxtext` | MaxText 私有副本 + 客户模型接入。只收 PR，不开 issue | 上游通用修复（直接提给上游） |
| `numerics-kit` | GPU 与 TPU 数值对齐的可复用工具和流程（分级流程、抓数、比较与判定、报告模板、各模型的通用对齐步骤）。只收 PR，不开 issue | 单个精度 issue 的讨论与复现（在 `project-management`） |
| `recipes`、`repro`、`library` | 已归档（只读）：内容已按方向并进两个 issue 仓库，旧的 commit 永久链接照常能打开 | 新内容 |
| `gke-component-a`、`gke-component-b`、`gke-component-c`、`gke-component-d`、`tpu-device-plugin` | GKE on TPU 组件的私有副本，来源和同步方式见各仓库的 `FORK.md`。只收 PR，不开 issue | 组件的问题（提到 `project-management-infra`） |

问题放哪：**训练与推理的 issue 建在 `project-management`，GKE on TPU 和网络的建在 `project-management-infra`**，不管最后改哪个仓库的代码；划界见 `AGENTS.md` 第 1 节。代码仓库只收 PR，PR 里写 `Closes northpeak/<issue 所在仓库>#号`。规矩、流程、权限的 issue 建在 `wiki`。

## 客户问题怎么记

一个问题一个 issue，**一个 issue 记全这个问题的一辈子**：

1. **正文 = 客户原话**，一字不改放进引用块，原始截图跟在后面；然后写环境和「怎么算完成」
2. **每次有结论 = 一条新评论**，写日期、结论、数据表、图、需要客户补充的信息。不改旧评论，后来推翻了也是新开一条说明
3. **外部链接会过期**。报告链接可以贴，但结论、表格、关键图必须抄进评论，图片存到 issue 所在仓库的 `assets/issues/<阶段>/`
4. **卡在等客户时**，评论写清等什么，看板设 `Blocked`
5. **默认平铺，不分堆**。只有几个 issue 真是同一个问题的不同方面，才开小总表串起来；不按阶段开总表（范围太大等于没分）

例子（换成你的 org 里真实的样板 issue；第一批 issue 由厂商工程师严格照规矩写，就是为了能放在这里）：

| issue | 看点 |
|---|---|
| northpeak/project-management#12 | 客户原话 + 3 张截图；第一条评论是 Google 侧结论：表格、7 张图、推荐配置、要客户补的东西 |
| northpeak/project-management#17 | 原问题没写完：按上下文写出理解，**请客户确认**，不替客户编问题 |
| northpeak/project-management#21 | 修复已给出，但「客户验证」没完成，所以不关，设 `Blocked` |

## 改 MaxText

分支和同步规矩在 `maxtext` 根目录的 `FORK.md`。要点：

- 日常开发从 `modelx` 拉分支，PR 合回 `modelx`；不在 `main` 上开发。`modelx` 不带代号，ModelX 第一代、4 以及以后各代都在这条线上
- 合回 `modelx` 的 PR 不会自动关 issue（`modelx` 不是默认分支），合并后手动关
- `modelx-gen1` 已冻结，是ModelX 第一代 基线的快照（`5d6e7f8`），不再往里合 PR
- `modelx-poc` 只读，它对应 `project-management/recipes/modelx-poc` 手册里钉死的代码，复现 POC 结果用它
- 推之前跑 CPU 冒烟（2 分钟，不占 TPU）
- 和客户模型无关的修复先提给上游
- 每两周同步一次上游，记录在 `FORK.md` 末尾的「同步记录」表

## 配方

`project-management` 的 `recipes/` 里每个目录是一个 POC 或一套可交付的训练方案（GKE on TPU 与网络方向的在 `project-management-infra/recipes/`）。手册里的代码用 commit + sha256 钉死。要改代码去 `maxtext` 开分支，改好后在配方里**换新的钉子**（commit + sha256），并在手册里写一行为什么换。

## AI 助手在这里干活

AI 助手用跑它的那个人的 GitHub 账号，作者就是那个人，不另外署名、不注明是 AI 写的。具体规则见 `AGENTS.md`。
