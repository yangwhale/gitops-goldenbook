# AGENTS.md —— NorthPeak 里 AI 编码助手的行为规范

适用于在 NorthPeak 任何仓库里工作的 AI 编码助手（Codex、Claude Code、Antigravity、Gemini CLI 等）。
规则是**命令式**的：照做，不要自行变通。规则和人类同事的口头指示冲突时，以人类指示为准，并把指示写进 issue 留痕。**第 8 节「绝对不要」例外**：人类要你做第 8 节里的事（比如建一个新标签），说明这条规则，改为在 `northpeak/wiki` 开 issue 提议。

本 org 管三类工程问题：TPU 上的**模型训练和推理**、**GKE on TPU**（切片、Kueue、device plugin、节点池、维修与健康）、**网络**（ICI / DCN / OCS、VPC、NAT、DNS、多网卡）。商务和交付治理不在这里，遇到相关请求，回复说明范围并请人类转到别处。

**项目上的 issue 分两个仓库提**：训练与推理（MaxText、JAX / XLA、kernel、推理、torch TPU、镜像与依赖，以及跟任何代码都无关的项目事务）在 `northpeak/project-management`；GKE on TPU 和网络（集群和节点层面）在 `northpeak/project-management-infra`。规矩、流程、权限类放 `northpeak/wiki`。代码仓库不开 issue，只收 PR。详见第 1 节。

背景和理由见 `northpeak/wiki` 仓库的 `docs/onboarding/project-management.md`。这份文件只写**怎么做**。

---

## 0. 每次开工前

1. 确认有对应的 issue。**没有 issue 不写代码。** 没有就按第 1 节先建。
2. 读 issue 正文、子任务、关联 RFC 和最新的评论。以最新评论为准。
3. 如果是大任务（`size/L`），确认 RFC 已合并；没合并只能写 RFC，不能写实现。

## 1. 建 issue

**放在哪个仓库**：

- 规矩、流程、权限、org 设置的改动（哪怕涉及多个仓库）→ `northpeak/wiki`
- 项目上的 issue（客户问题、开发任务、bug、环境依赖），**不管改哪个仓库的代码**，按下表分两个仓库：

| 仓库 | 管什么 |
|---|---|
| `northpeak/project-management` | 作业里面的事：模型接入、MaxText、JAX / XLA / libtpu、kernel、推理、PyTorch on TPU、精度、性能（步时、MFU、显存）、镜像与依赖、数据读取与 checkpoint；以及不属于下一行的其他项目事务 |
| `northpeak/project-management-infra` | 集群和节点层面的事：切片调度与供给、device plugin、Kueue、JobSet、节点池（创建、升级、扩缩）、维修与健康（含芯片、主机故障）、存储挂载（Lustre、GCSFuse、Hyperdisk 等 CSI）、网络（ICI / DCN / OCS、VPC、NAT、DNS、多网卡）、配额与容量 |

- 两个仓库按客户的组授权：训练组两个仓库都能看到，GKE 组和网络组只能看到 `project-management-infra`（见 `northpeak/wiki` 的 `docs/onboarding/permissions.md`）。客户在自己看得到的仓库提就行，不用先判断属于哪边
- 拿不准就建在现象出现的那一边。分诊时发现属于另一边，**不要让客户重提**，分三种：
  - Google 同事提的、没有客户参与的：用 `gh issue transfer <号> northpeak/<另一个仓库> -R northpeak/<当前仓库>` 移过去。判断参与者属于哪一方：`gh api orgs/northpeak/teams/<googlers|training|gke|network|partners>/members --jq '.[].login'`。转移要求两边仓库都有 Write，只有 Google 同事能做
  - 客户提的或客户参与过的，从 `project-management` 转到 `project-management-infra`：可以转，训练组两边都看得到；同样由 Google 同事用上面的命令转。合作方（`partners`）参与过的不转，按下一条处理（合作方看不到 infra）
  - 客户提的或客户参与过的，从 `project-management-infra` 转到 `project-management`：**不转移**（GKE 组和网络组转过去就看不到了）。Google 同事在另一边新开一条 issue，正文链回原 issue，再在原 issue 评论里链过去；原 issue 留给报告人，另一边的结论当天同步成原 issue 的评论，两条一起关
- 转移后核对两件事：标签（目标仓库没有的同名标签会丢，按目标仓库的标签补齐 `type/*` 和 `area/*`；`type/accuracy` 在 infra 没有，改打 `type/bug`；`area/env` 两边含义不同，要重判）；看板条目还在、字段没变，丢了用 `board.sh add` 补回
- 一个问题的排查过程只记在一个仓库。根因在哪边就由哪边持有；另一边的 issue（上面不转移时留下的那条，或需要跟踪时开的那条）只链过去、同步结论，不重复记录过程
- 两个仓库的编号各自从 1 开始：跨仓库引用 issue **一律写全仓库名**（`northpeak/project-management-infra#3`），不写裸的 `#3`。不是每个人都打得开另一边的链接（GKE 组和网络组打不开 `project-management`，合作方打不开 `project-management-infra`），要他们看的结论写进他们看得到的那条 issue，不能只贴链接
- 代码仓库（`maxtext` 和各 GKE 组件仓库）**不开 issue**，Issues 功能已关闭，只收 PR

两个 `project-management*` 仓库只放项目本身的事，不放规矩和权限。

**标题**：`<动词开头的一句话>`，不超过 60 字，不带句号。例：`接入 ModelX-VL 的视觉编码器`、`修复 FP8 下 MoE 路由 NaN`。

**标签**（只能用下表里的，**禁止新建标签**）：

| 标签 | 什么时候打 |
|---|---|
| `type/bug` `type/accuracy` `type/perf` `type/feat` `type/design` `type/question` `type/docs` `type/chore` | `type/accuracy` 只在 `project-management`。每个 issue 必须且只能打一个：报错与故障 / 精度对不齐 / 性能不达预期 / 功能与开发任务 / 设计与调研 / 问询 / 文档 / 重构 CI 工具。网页上用模板建会自动打上；命令行建要自己打，见下面的模板表 |
| `size/S` | 小任务：改配置、小修复，不需要 RFC |
| `size/L` | 大任务：接新模型、改数据通路、跨模块改动，必须先写 RFC |
| `project-management`：`area/maxtext` `area/jax-xla` `area/kernel` `area/inference` `area/torch-tpu` `area/env`（环境、版本、镜像、依赖） `area/other`<br>`project-management-infra`：`area/gke` `area/network` `area/env`（配额与容量） `area/other` | 项目 issue 的领域，可以打多个，只用所在仓库的那一组。`project-management-infra` 按「跟哪块有关」对应：网络两项 → `area/network`，配额与容量 → `area/env`，其余 → `area/gke`；`project-management` 的「数据读取 / checkpoint」按根因打，拿不准打 `area/other`。**建 issue 时一律不打**，查清根因后再打，打错了直接改。上游的 bug 另在上游仓库提 issue，这边贴链接跟踪 |
| `P0` | 只给阻塞他人或线上的 bug（两个仓库都有） |
| `P1` | 本阶段必须解决、影响上线主路径的 issue |
| `P2` | 重要但不阻塞主路径的 issue。优先级每个 issue 最多打一个；拿不准就不打，由负责人定 |
| `tracker` | 只给总表（见下，默认不开；两个仓库都有） |
| `access` | 只给权限变更，只在 `wiki` 有（权限类 issue 提在 `wiki`） |

拿不准 S 还是 L：会改动超过一个模块，或者别人需要先认可方案，就是 L。

**正文：按模板的字段写。** 两个仓库各有一套 issue 模板（网页上点「New issue」可见）：`project-management` 7 类，`project-management-infra` 6 类。你用命令行建不出网页表单，所以先判断属于哪一类，然后正文用 `### 字段名` 作小标题、按下表的顺序写，标签打表里那一个 type。这样建出来和人在网页上填的一样。

`project-management`：

| 模板 | 什么时候用 | type 标签 | 正文小标题（第一个必填，其余有就写） |
|---|---|---|---|
| 报错与故障 | 报错、崩溃、卡死、NaN；镜像与依赖出问题 | `type/bug` | 问题描述 / 跟哪块有关 / 哪类故障 / 最小复现 / 代码与版本 / 硬件与规模 / 模型、数据与并行 / run-ID、日志或 GCS 路径 / 实验结果 |
| 精度对不齐 | loss、梯度、输出和参考对不上 | `type/accuracy` | 问题描述 / 跟哪块有关 / 对照侧 / 比的是什么 / 代码与版本 / 硬件与规模 / 模型、数据与并行 / 启动命令或配置 / run-ID、日志或 GCS 路径 / 实验结果 |
| 性能不达预期 | 步时、吞吐、MFU、显存 / OOM | `type/perf` | 问题描述 / 跟哪块有关 / 哪类 / profile / 代码与版本 / 硬件与规模 / 模型、数据与并行 / 启动命令或配置 / run-ID、日志或 GCS 路径 / 实验结果 |
| 功能与开发任务 | 新模型、新功能、kernel、重构 / CI / 工具、文档 | `type/feat`（重构类改 `type/chore`，文档改 `type/docs`） | 目标 / 跟哪块有关 / 哪类 / 验收标准 / 参考实现与权重来源 / 依赖 |
| 设计与调研 | 方案设计、技术调研 | `type/design` | 问题描述 / 方案与取舍 / 结论 / 设计文档 |
| 使用问询 | 怎么用、现象是否符合预期 | `type/question` | 问题描述 / 跟哪块有关 / 背景 / 运行条件各栏 |
| 跟踪总表 | 见下，默认不开 | `tracker` | 目标 / 范围 / 成功标准 / 时间线 |

`project-management-infra`：

| 模板 | 什么时候用 | type 标签 | 正文小标题（第一个必填，其余有就写） |
|---|---|---|---|
| 报错与故障 | 报错、卡住、起不来：切片、调度、节点池、维修、存储挂载、网络 | `type/bug` | 问题描述 / 跟哪块有关 / 集群与版本 / 节点池 / 组件版本 / 最小复现 / kubectl 输出与事件 / 影响 / 实验结果 |
| 性能不达预期 | 调度或节点启动时延、网络带宽 / 时延、存储吞吐 | `type/perf` | 问题描述 / 跟哪块有关 / 哪类 / 测量方法与数值 / 期望值与来源 / 集群与版本 / 节点池 |
| 功能与开发任务 | 新功能、组件改动、重构 / CI / 工具、文档 | `type/feat`（重构类改 `type/chore`，文档改 `type/docs`） | 目标 / 跟哪块有关 / 哪类 / 验收标准 / 依赖 |
| 设计与调研 | 方案设计、技术调研 | `type/design` | 问题描述 / 方案与取舍 / 结论 / 设计文档 |
| 使用问询 | 怎么用、现象是否符合预期 | `type/question` | 问题描述 / 跟哪块有关 / 背景 / 集群与版本 / 节点池 |
| 跟踪总表 | 见下，默认不开 | `tracker` | 目标 / 范围 / 成功标准 / 时间线 |

下拉字段只能填下面的选项之一（每个反引号里是一个完整选项），不要自己编：

`project-management`：

- 「跟哪块有关」：`MaxText`、`JAX / XLA / libtpu`、`kernel（Pallas、Tokamax 等）`、`TPU 推理`、`PyTorch on TPU`、`环境 / 版本 / 镜像 / 依赖`、`数据读取 / checkpoint`、`不知道 / 都不是`
- 「哪类故障」（报错与故障）：`代码报错 / 崩溃 / NaN`、`数据读取 / checkpoint`、`依赖 / 版本 / 镜像`
- 「比的是什么」（精度对不齐）：`loss 曲线`、`梯度 / 梯度范数`、`单层前向`、`单层反向`、`模型输出`、`其他`
- 「哪类」（性能不达预期）：`回归（以前快，现在慢）`、`未达目标`、`优化机会`
- 「哪类」（功能与开发任务）：`新模型接入`、`新功能 / 功能需求`、`kernel`、`重构 / CI / 工具（建好后标签改成 type/chore）`、`文档（建好后标签改成 type/docs）`

`project-management-infra`：

- 「跟哪块有关」：`切片调度与供给（gke-component-d、gke-component-c、gke-component-b、gke-component-a）`、`device plugin`、`Kueue / JobSet`、`节点池（创建、升级、扩缩）`、`维修与健康（含芯片、主机故障）`、`存储挂载（Lustre、GCSFuse、Hyperdisk 等 CSI）`、`网络：ICI / DCN / OCS`、`网络：VPC、NAT、DNS、多网卡`、`配额与容量`、`不知道 / 都不是`
- 「哪类」（性能不达预期）：`调度或节点启动时延`、`网络带宽 / 时延`、`存储吞吐`、`其他`
- 「哪类」（功能与开发任务）：`新功能 / 功能需求`、`组件改动`、`重构 / CI / 工具（建好后标签改成 type/chore）`、`文档（建好后标签改成 type/docs）`

- **建 issue 时不打 `area/*` 标签**，「跟哪块有关」栏照实填（不确定就填「不知道 / 都不是」）；查清根因后再打 `area/*`
- 你知道的运行条件**都写上**（代码分支和 commit、jax / libtpu 版本、芯片和拓扑、模型数据和并行、命令、run-ID），这是别人复现的前提；不知道的写「未确认」，不要编
- 「验收标准」必须可验证：一条命令、一个数值阈值、一个可观察的行为
- 替客户建 issue 时，「问题描述」放客户原话（见下面「客户提的问题」）

**命令**：

```bash
REPO=northpeak/project-management   # GKE on TPU、网络（集群和节点层面）改成 northpeak/project-management-infra
gh issue create -R $REPO --title "<标题>" --label <模板对应的 type> --body-file /tmp/body.md   # 知道大小就再加 ,size/S 或 ,size/L
# 加进看板（必须做，看板不会自动收录普通 issue；你的账号没有看板写权限就跳过这一步，分诊的人会加）；知道大小就在末尾带 S 或 L，不知道就不带，分诊时再设
gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- add <issue URL> [S|L]
```

**一个问题一个 issue，默认平铺，不分堆。** 只在下面两种情况开总表（打 `tracker` 标签），把相关 issue 用 GitHub 的 sub-issue 挂上去：

1. **几个 issue 确实是同一个问题的不同方面**：例如都是 DDP / FSDP 的 loss 对齐。堆要小，只放真正相关的
2. **一个大任务要拆给不同的人**：大任务本身就是总表，拆出的子任务挂在下面

**不要**按阶段、按月、按仓库开总表——范围太大等于没分；不往下套第三层；**拿不准能不能归堆，就不归**。总表正文写这几个问题的共同背景，不重复子任务的内容。

**客户提的问题**（详见 `northpeak/wiki` 的 `docs/onboarding/working-in-northpeak.md`）：

- 正文放客户原话（引用块，一字不改）和原始截图；截图存到 issue 所在仓库的 `assets/issues/<阶段>/`
- 原话没写完或有歧义：写出你的理解，并请客户确认。**不要替客户补全问题**
- 模板里只有「问题描述」是必填，**不要要求客户补填其他栏**。缺的运行条件（代码与版本、硬件与规模、模型数据与并行、命令、run-ID）由我们查清后写进第一条评论；查不到的才在评论里问客户
- 客户选错了模板或类型，直接改标签，不要让客户重提
- 每次有结论追加一条评论，不改旧评论；外部报告链接会过期，结论、表格、关键图都抄进评论
- 修复给出但客户还没验证：不关 issue，设 `Blocked` 并评论在等什么

## 2. 看板状态：大多数不要动

| 状态 | 谁来改 |
|---|---|
| Triage | 规则自动（加入看板时） |
| In Progress | 规则自动（PR 关联到 issue 时） |
| Done | 规则自动（issue 关闭或 PR 合并时） |
| **Design Pending** | 你：认领了 `size/L` 任务、开始写 RFC 时 |
| **Ready to Develop** | 你：RFC 的 PR 合并后 |
| **Blocked** | 你：被外部依赖卡住时，**同时在 issue 里评论卡在哪、等谁** |

```bash
gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- status <issue URL> "Blocked"
```

不要手动把状态拖到 Done（会触发自动关闭），不要为了「看起来有进展」改状态。认领 = 把负责的人类设为 assignee。P0 例外：分诊时直接设 In Progress。

**分诊**（处理看板上 Triage 的 issue，网页上建的 issue 要先用 `board.sh add` 加进看板）：

1. 仓库对不对；不对按第 1 节的转移规则处理
2. 恰好一个 `type/*`；客户选错了直接改
3. `size/S` 或 `size/L`
4. 优先级 `P0` / `P1` / `P2`，拿不准不打
5. assignee（有固定路由的按下面的路由）
6. 缺的运行条件查清后写成第一条评论

调查类 issue 没有 PR，状态停在 Triage 是正常的；被外部卡住时设 Blocked，有结论就关。

**固定路由**：MaxText 相关、需要上游 MaxText 团队跟进的 issue，assignee **加上** `<上游对接人账号>`（和我方负责人并列，不是替换），MaxText 团队会一起看。

## 3. 分支和提交

- 分支名：`<type>/<issue号>-<英文短横线简述>`，如 `feat/42-vision-encoder`。type 用 `feat`、`fix`（对应 `type/bug`、`type/accuracy`）、`perf`、`docs`、`chore`；issue 在 `project-management-infra` 的，号前加 `infra-`，如 `fix/infra-12-node-repair`
- 分支推在**本仓库**，不要从个人 fork 提 PR（外部 fork 的 PR 触发不了验证）
- 上游项目的私有副本（如 `maxtext`，以及 `gke-component-a`、`gke-component-b`、`gke-component-c`、`gke-component-d`、`tpu-device-plugin` 这些 GKE 组件）：分支和同步规矩以仓库根目录的 `FORK.md` 为准
- 提交信息第一行：`<type>: <简述>`；正文写为什么改。不要把正文内联在命令行里，用 `git commit -F <文件>`
- 不 force push 到 `main`，不改写已推送的公共历史

**客户的代码和材料放哪**（POC 阶段，客户本人或替客户工作的助手照这个做）：
- 代码改动：在 `maxtext` 里从 `modelx` 拉一个自己的开发分支，改完推上去即可。分支名不做规定，不要求提 PR
- issue 里放不下的东西（测试脚本、复现代码、日志文件等）：`project-management` 的 issue 放到该仓库的 `repro/issues/<issue号>-<简述>/`，`project-management-infra` 的放到该仓库的 `repro/issues/<issue号>-<简述>/`，在 issue 里引用。issue 里能写清楚的就不建目录；目录里不要求 README 或 `card.yaml`
- 跑通了、要长期用的流程：整理进 `project-management` 的 `recipes/`；GKE on TPU 与网络方向的整理进 `project-management-infra` 的 `recipes/`，一个配方一个目录，发版 tag 写 `recipes/<配方名>/v<N>`
- `project-management-infra` 的四个目录：`library/`（给客户的成品文档）、`meetings/`（例会纪要）由 Google 维护；`recipes/`、`repro/` 由 Google 和客户共同维护
- `project-management` 的四个目录：`library/`（训练方向给客户的成品文档）、`meetings/`（训练例会纪要）由 Google 维护；`recipes/`、`repro/` 由 Google 和客户共同维护

我们自己修 issue 时，仍按上面的分支命名开分支、按第 4 节提 PR。

## 4. PR

**例外：`project-management` 和 `project-management-infra` 的记录类改动不走 PR**：改 issue 模板、加截图直接推 `main`，提交信息写清改了什么，并带上 `Refs #<issue号>`；`AGENTS.md` 由 `sync-agents.sh` 直接同步。其他改动照下面的规则走 PR：两个仓库的四个目录（客户放进 `repro/` 的材料除外，可以直接推），以及根 README、PR 模板与工作流。

**必须**：

1. 正文含 `Closes northpeak/<issue 所在仓库>#<号>`，如 `Closes northpeak/project-management-infra#12`（规矩类改动在 wiki 提 PR 时写 `Closes #<号>`）；只是相关、不该关闭时写 `Refs`。org 已停用 GitHub Actions，没有 CI 替你检查：推之前自己核对这一条和下面的偏差栏（`gh api repos/northpeak/wiki/contents/scripts/pr-check.py --jq .content | base64 -d > /tmp/pr-check.py && python3 /tmp/pr-check.py < /tmp/body.md`），该跑的测试在本地跑完：代码仓的 `FORK.md` 或 README 里写的冒烟，加上你改动涉及的单测。
   - PR 合进的**不是默认分支**（如 `maxtext` 合进 `modelx`）时，GitHub 不会按 `Closes` 关 issue，看板也不会跳到 Done。合并后由 PR 的作者手动关（第 8 节「不关别人的 issue」不适用于这种情况）：`gh issue close <issue URL> --comment "由 northpeak/<仓库>#<PR号> 完成"`
2. 按 PR 模板填写四栏：做了什么 / 关联 / 怎么验证的 / **和原计划的偏差**。
   - 偏差一栏：实现和 issue 或 RFC 写的不一样时，写「原计划 A → 实际 B → 原因」；完全一致写「无」。**不许删这一栏。**
   - 偏差较大时，同时回到 issue 或 RFC 里更新原文，让记录和代码一致。
3. 指定一位人类负责人为 assignee（通常就是你用的那个账号的主人）。
4. 改 PR 正文不要用 `gh pr edit`（它要求令牌有 `read:org` 权限，通常没有，会报 GraphQL 权限错误）。用 REST：
   ```bash
   gh api -X PATCH repos/northpeak/<repo>/pulls/<号> -F body=@/tmp/body.md
   ```

**尽量**：一个 PR 只做一件事；核心目录改动超过 200 行就拆。

**评审（现阶段不强制）**：需要别人看时，请他评审并等他批准再合并：
```bash
gh api -X POST repos/northpeak/<repo>/pulls/<号>/requested_reviewers -f 'reviewers[]=<GitHub 账号>'
```
不需要时，本地自查完就可以自己合并。账号主人说了要谁看，就必须请那个人。

**禁止**：在没有关联 issue 的情况下开 PR；把多个不相关的改动塞进一个 PR；没在本地跑过测试就合并。

## 5. 数字

凡是写进 issue、PR、RFC、周报的数字（loss、吞吐、步时、显存、精度）：

- **必须附来源**：可复现的命令 + commit + 配置文件路径（或集群作业的 run-ID）
- 和参考值比较时，写明参考值来源和容差
- 估算就写「估算」并给出推导；没有来源的数字**不要写**
- 不写「本地测了一下大概是 X」
- 做数值对齐（GPU 对 TPU）或改动数值相关代码时，先读 `northpeak/numerics-kit` 的 `docs/reference/precision-boundaries.md`：几乎所有不对齐都出在 16 位与 32 位互转、以及 GPU 上 TF32 的地方，按其中的清单逐个算子核对两边的乘法、累加、输出精度与舍入位置

验证失败时（本地测试、集群运行），先判断是**基础设施挂了**（作业没起来、集群异常、超时）还是**数字不对**（超出容差），在评论里写清是哪种，不要只说「跑挂了」。

## 6. 评论和沟通

- 进展、决策、阻塞都写在 issue 评论里。在别处（聊天、会议）得出的结论，**当天回写到 issue**
- 和客户开会的纪要与 slides：训练方向放 `project-management` 的 `meetings/`，GKE、网络方向和全体例会放 `project-management-infra` 的 `meetings/`。纪要由 Google 写，规矩见各自的 README；几个方向一起开的会放 `project-management-infra`。纪要 PR 写 `Refs` 例会记录 issue（两个仓库的 1 号 issue），不写 `Closes`（否则合并时会关掉它）；纪要只做索引，结论照上一条写回 issue
- 评论只写事实和结论，不写过程寒暄
- 不写分派和流程：「已接手」「分给某某跟进」「已打标签 / 已进看板 / 状态改成 X」「上游另外跟进」都不写。assignee、标签、看板自己就说明了这些，改了就行
- 账号主人没拍板的后续动作（比如给上游提 issue 或 PR）不写成计划
- 修改别人的 issue 正文之前，先评论说明要改什么

## 7. RFC

- RFC 一律放在 `northpeak/wiki` 仓库（不管你在哪个仓库工作）：复制 `docs/rfc/template.md` 为 `docs/rfc/NNNN-<英文简述>.md`，NNNN = 现有最大编号 + 1（编号可能有空缺，取最大值 + 1，不是数文件个数）
- 「非目标」必填
- 在 `docs/rfc/index.md` 末尾加一行，状态 `draft`。状态只有：`draft`、`review`、`accepted`、`rejected`、`superseded`、`implemented`
- 提 PR，正文 `Refs northpeak/<issue 所在仓库>#<号>`（写全名）；RFC 要请 issue 的报告人或账号主人指定的人评审，批准后再合并，不自己合；合并后把那个 issue 设为 Ready to Develop（见第 2 节）
- 实施后方案变了，回来改 RFC，并更新 index 里的状态

## 8. 绝对不要

- 新建、改名、删除标签
- 建公开仓库（建仓库一律选 Private）
- 改 org 或仓库的设置、权限、分支保护、看板字段
- 关闭不是你负责的 issue（除非人类明确要求，并在评论里注明）
- 在任何地方写入：密钥、令牌、客户的训练数据和模型权重、其他客户或其他项目的信息、**公司内部链接**（如 `go/` 短链、内部文档地址）——客户的工程师能看到这里的所有内容
- 编造数字、run-ID、issue 号、文件路径。不确定就去查，查不到就写「未确认」

## 9. 完成的定义

一个任务只有同时满足以下几条才算完成：

- 「怎么算完成」里的每一条都已验证，并在 issue 里附了证据（命令输出或 run-ID）
- 相关 PR 已合并，偏差已记录
- 文档（README、RFC、wiki）已同步
- issue 已关闭（PR 合进默认分支时自动关闭；合进其他分支的按第 4 节手动关）

## 10. 不署名

你用的是运行你的那个人的 GitHub 账号，GitHub 记下的作者就是他，他对内容负责。**不要**在提交、PR、issue、评论、RFC 里注明是 AI 写的：不加 `Assisted-by`、`Co-Authored-By: <AI>`，不写「由 <工具> 起草」「— <工具> 代 @某人」。

- 账号主人没说过的承诺、表态、诉求，不要用他的账号写出去；拿不准先问他
