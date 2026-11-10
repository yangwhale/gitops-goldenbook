# 第 4 章 标签与 issue 模板

标签表是封闭的，模板只有第一栏必填。这两条让 type 标签永远不漏，客户提 issue 的门槛又最低。

## 4.1 标签：一张封闭的表

**规则：只能用下表里的标签，禁止新建标签。**

标签一旦允许随手建，三个月后就会有 `bug`、`Bug`、`type/bug`、`缺陷` 四个同义标签，筛选全部失效。
所以标签表是封闭的，改动走 `wiki` 的 RFC。AI 助手的规则里「新建、改名、删除标签」列在「绝对不要」第一条。

### 训练与推理仓（`project-management`）的标签

| 标签 | 颜色 | 描述 | 什么时候打 |
|---|---|---|---|
| `type/bug` | `d93025` | 缺陷 | 报错与故障 |
| `type/accuracy` | `e99695` | 精度、数值和参考对不上（loss、梯度、输出） | 精度对不齐 |
| `type/perf` | `f9d0c4` | 性能不达预期（吞吐、步时、MFU、显存） | 性能不达预期 |
| `type/feat` | `1a73e8` | 新功能 | 功能与开发任务 |
| `type/design` | `bfdadc` | 设计、调研、RFC | 设计与调研 |
| `type/question` | `cfd3d7` | 问询：怎么用、是否符合预期 | 使用问询 |
| `type/docs` | `5f6368` | 文档 | 文档类任务 |
| `type/chore` | `9aa0a6` | 杂务 | 重构、CI、工具 |
| `size/S` | `1e8e3e` | 小任务，不需要 RFC | 改配置、小修复 |
| `size/L` | `9334e6` | 大任务，先写 RFC | 接新模型、改数据通路、跨模块改动 |
| `area/maxtext` | `1d76db` | 领域：MaxText 代码与配置 | 查清根因后 |
| `area/jax-xla` | `5319e7` | 领域：JAX、XLA 编译器、libtpu | 查清根因后 |
| `area/kernel` | `b60205` | 领域：kernel（Pallas、Tokamax 等） | 查清根因后 |
| `area/inference` | `0e8a16` | 领域：TPU 推理 | 查清根因后 |
| `area/torch-tpu` | `fbca04` | 领域：PyTorch on TPU | 查清根因后 |
| `area/env` | `c5def5` | 领域：环境、版本、镜像、依赖 | 查清根因后 |
| `area/other` | `d4c5f9` | 领域：以上都不是 | 查清根因后 |
| `P0` | `b60205` | 阻塞 | 只给阻塞他人或线上的 bug |
| `P1` | `d93f0b` | 优先级：本阶段必须解决，影响上线主路径 | |
| `P2` | `fbca04` | 优先级：重要但不阻塞主路径 | |
| `tracker` | `f9ab00` | 总表：同一问题的不同方面，或大任务拆给不同的人 | 见第 6 章 6.11 |
| `access` | `80868b` | 权限变更 | 只在 `wiki` 用（见下） |

> `tracker` 的描述原项目还是早期的「阶段总表或大任务总表」；规矩早已改为不开阶段总表，描述没跟上。复刻时用上表的写法。

### 基础设施仓（`project-management-infra`）的标签

和上表相同，除了：

- **没有** `type/accuracy`（精度是训练侧的问题）、`access`（权限类 issue 本来就提在 `wiki`）
- **没有**训练侧的五个 `area/*`（`maxtext`、`jax-xla`、`kernel`、`inference`、`torch-tpu`）
- **有**自己的 `area/gke`（`326ce5`，切片、device plugin、Kueue / JobSet、节点池、维修与健康、存储挂载）和 `area/network`（`006b75`，ICI / DCN / OCS、VPC、NAT、DNS、多网卡）
- `area/env` 的含义不同：在 infra 仓是「**配额与容量**」，在训练仓是「环境、版本、镜像、依赖」
- `type/perf` 的描述改为「调度与节点启动时延、网络带宽 / 时延、存储吞吐」

> `area/env` 两边含义不同是个历史决定（infra 仓的标签是从训练仓复制过来再改的）。
> 复刻时可以直接给 infra 仓起一个不同的名字，比如 `area/capacity`，省掉转移 issue 时「要重判 `area/env`」这一步。

### 规则仓（`wiki`）的标签

`wiki` 只放规矩类 issue，标签很少：`type/bug`、`type/feat`、`type/docs`、`type/chore`、`size/S`、`size/L`、`P0`、`tracker`、`access`。

### 四个维度，各自的规则

| 维度 | 每个 issue 打几个 | 什么时候打 | 谁打 |
|---|---|---|---|
| `type/*` | **必须且只能一个** | 建 issue 时 | 模板自动打；命令行建的自己打 |
| `size/*` | 一个（任务类） | 认领时 | 负责人 |
| `area/*` | 可以多个 | **查清根因后**，建 issue 时不打 | 负责人 |
| `P0`/`P1`/`P2` | 最多一个；拿不准就不打 | 分诊时 | 负责人 |

**为什么建 issue 时不打 `area/*`**：建 issue 时往往还不知道问题在哪。客户报「loss 发散」，可能是 MaxText 的配置、可能是 XLA 的编译、可能是 kernel 的数值。
建的时候猜一个，后面多半是错的，而错的标签没人会回来改。所以模板里有一个「跟哪块有关」下拉框，让报告人照实填（可以填「不知道」），查清根因后由负责人打 `area/*`。**打错了直接改。**

**拿不准 S 还是 L**：会改动超过一个模块，或者别人需要先认可方案，就是 L。

**`P0` 只给 bug**，而且是阻塞他人或线上的 bug。P0 直接进 In Progress，不排队。

**上游的 bug 另在上游仓库提 issue**，这边贴链接跟踪，不打特殊标签。

## 4.2 issue 模板：只有第一栏必填

两个 issue 仓各有一套模板（GitHub issue forms，YAML 格式）：

| 训练与推理仓（7 类） | 基础设施仓（6 类） | type 标签 |
|---|---|---|
| `1-bug.yml` 报错与故障 | `1-bug.yml` 报错与故障 | `type/bug` |
| `2-accuracy.yml` 精度对不齐 | — | `type/accuracy` |
| `3-perf.yml` 性能不达预期 | `2-perf.yml` 性能不达预期 | `type/perf` |
| `4-task.yml` 功能与开发任务 | `3-task.yml` 功能与开发任务 | `type/feat` |
| `5-design.yml` 设计与调研 | `4-design.yml` 设计与调研 | `type/design` |
| `6-question.yml` 使用问询 | `5-question.yml` 使用问询 | `type/question` |
| `7-tracker.yml` 跟踪总表 | `6-tracker.yml` 跟踪总表 | `tracker` |

文件名带数字前缀，控制新建页上的排列顺序（GitHub 按文件名排序）。

完整的模板文件在 [`appendix/templates/issue-repo-training/ISSUE_TEMPLATE/`](../appendix/templates/issue-repo-training/ISSUE_TEMPLATE/)
和 [`appendix/templates/issue-repo-infra/ISSUE_TEMPLATE/`](../appendix/templates/issue-repo-infra/ISSUE_TEMPLATE/)，直接拷贝可用。

### 设计原则

**1. 只有第一栏必填。** 每个模板的第一栏（「问题描述」或「目标」）`required: true`，其余全部 `required: false`。
模板顶部一段 markdown：「只有第一项**必填**：用自己的话描述问题就行。其余都是建议，愿意填就填，不填我们来补。」

原因：客户提 issue 的门槛越低越好。十个必填栏会让客户回到聊天群里提问。
缺的信息由厂商工程师查清后补进第一条评论（第 6 章）。**选对模板，就已经帮了大忙**——因为模板决定了 type 标签和后续的字段。

**2. 第一栏用「用自己的话说」。** 描述写成「用自己的话说：出了什么错；有报错就贴关键几行」，而不是「请详细描述问题」。前者告诉客户写多少就够。

**3. 运行条件单独成组，标「建议填写」。** 中间插一段 markdown「### 运行条件（建议填写）：能填多少填多少，写全了我们拿到就能复现；不清楚的空着，我们来补」。
然后是代码与版本、硬件与规模、模型数据与并行、启动命令、run-ID 这些栏。

**4. 运行条件这类要写格式的文本栏，给一个真实格式的 placeholder。** 比如「代码与版本」的 placeholder：

```
northpeak/maxtext @ modelx @ 1a2b3c4
jax 0.11.1 / libtpu 0.0.46
image ...@sha256:...
```

客户看到例子就知道要写到 commit 级别、镜像要写 digest。

**5. 「跟哪块有关」下拉框的最后一项是「不知道 / 都不是」。** 逼客户选一个他不确定的选项，只会得到错误的数据。（「哪类」这种客户一般能判断的下拉框，原项目没加这一项；性能和 infra 功能类的有「其他」）

**6. 下拉框的选项可以带说明。** 比如「重构 / CI / 工具（建好后标签改成 type/chore）」：
issue forms 一个模板只能自动打固定的标签，「功能与开发任务」模板自动打 `type/feat`，选了「重构」的要手动改成 `type/chore`。把这条写进选项本身，负责人看到就知道要改。

**7. 跟踪总表模板的 description 写「默认不开」。** 「默认不开。只在两种情况开：几个 issue 是同一个问题的不同方面；一个大任务要拆给不同的人」。
模板底部再提醒一次：「不按阶段、月份、仓库开；不往下套第三层」。

### 每个模板的字段

**训练与推理仓：**

| 模板 | 字段（按顺序；第一个必填） |
|---|---|
| 报错与故障 | 问题描述 / 跟哪块有关 / 哪类故障 / 最小复现 / 代码与版本 / 硬件与规模 / 模型、数据与并行 / run-ID、日志或 GCS 路径 / 实验结果 |
| 精度对不齐 | 问题描述 / 跟哪块有关 / 对照侧 / 比的是什么 / 代码与版本 / 硬件与规模 / 模型、数据与并行 / 启动命令或配置 / run-ID、日志或 GCS 路径 / 实验结果 |
| 性能不达预期 | 问题描述 / 跟哪块有关 / 哪类 / profile / 代码与版本 / 硬件与规模 / 模型、数据与并行 / 启动命令或配置 / run-ID、日志或 GCS 路径 / 实验结果 |
| 功能与开发任务 | 目标 / 跟哪块有关 / 哪类 / 验收标准 / 参考实现与权重来源 / 依赖 |
| 设计与调研 | 问题描述 / 方案与取舍 / 结论 / 设计文档 |
| 使用问询 | 问题描述 / 跟哪块有关 / 背景 / 代码与版本 / 硬件与规模 / 模型、数据与并行 / 启动命令或配置 / run-ID、日志或 GCS 路径 |
| 跟踪总表 | 目标 / 范围 / 成功标准 / 时间线 |

**基础设施仓：**

| 模板 | 字段 |
|---|---|
| 报错与故障 | 问题描述 / 跟哪块有关 / 集群与版本 / 节点池 / 组件版本 / 最小复现 / kubectl 输出与事件 / 影响 / 实验结果 |
| 性能不达预期 | 问题描述 / 跟哪块有关 / 哪类 / 测量方法与数值 / 期望值与来源 / 集群与版本 / 节点池 |
| 功能与开发任务 | 目标 / 跟哪块有关 / 哪类 / 验收标准 / 依赖 |
| 设计与调研 | 同训练仓 |
| 使用问询 | 问题描述 / 跟哪块有关 / 背景 / 集群与版本 / 节点池 |
| 跟踪总表 | 同训练仓 |

### 下拉框选项（封闭枚举）

AI 助手用命令行建 issue 时，下拉字段只能填下面的选项之一，不能自己编。这份枚举同时写进 `AGENTS.md`。

**训练与推理仓：**

- 「跟哪块有关」：`MaxText`、`JAX / XLA / libtpu`、`kernel（Pallas、Tokamax 等）`、`TPU 推理`、`PyTorch on TPU`、`环境 / 版本 / 镜像 / 依赖`、`数据读取 / checkpoint`、`不知道 / 都不是`
- 「哪类故障」（报错与故障）：`代码报错 / 崩溃 / NaN`、`数据读取 / checkpoint`、`依赖 / 版本 / 镜像`
- 「比的是什么」（精度对不齐）：`loss 曲线`、`梯度 / 梯度范数`、`单层前向`、`单层反向`、`模型输出`、`其他`
- 「哪类」（性能不达预期）：`回归（以前快，现在慢）`、`未达目标`、`优化机会`
- 「哪类」（功能与开发任务）：`新模型接入`、`新功能 / 功能需求`、`kernel`、`重构 / CI / 工具（建好后标签改成 type/chore）`、`文档（建好后标签改成 type/docs）`

**基础设施仓：**

- 「跟哪块有关」：`切片调度与供给（gke-component-d、gke-component-c、gke-component-b、gke-component-a）`、`device plugin`、`Kueue / JobSet`、`节点池（创建、升级、扩缩）`、`维修与健康（含芯片、主机故障）`、`存储挂载（Lustre、GCSFuse、Hyperdisk 等 CSI）`、`网络：ICI / DCN / OCS`、`网络：VPC、NAT、DNS、多网卡`、`配额与容量`、`不知道 / 都不是`
- 「哪类」（性能不达预期）：`调度或节点启动时延`、`网络带宽 / 时延`、`存储吞吐`、`其他`
- 「哪类」（功能与开发任务）：`新功能 / 功能需求`、`组件改动`、`重构 / CI / 工具（建好后标签改成 type/chore）`、`文档（建好后标签改成 type/docs）`

**「跟哪块有关」到 `area/*` 的映射**（基础设施仓）：网络两项 → `area/network`；配额与容量 → `area/env`；其余 → `area/gke`。
训练仓的「数据读取 / checkpoint」按根因打，拿不准打 `area/other`。

## 4.3 `config.yml`：关掉空白 issue，互相指路

每个仓库的 `.github/ISSUE_TEMPLATE/config.yml`：

**训练与推理仓：**

```yaml
blank_issues_enabled: false
contact_links:
- name: GKE on TPU、网络、集群层面的问题
  url: https://github.com/northpeak/project-management-infra/issues/new/choose
  about: 切片、device plugin、Kueue / JobSet、节点池、维修、存储挂载、网络、配额，到 project-management-infra 提。打不开这个链接说明你没有那边的权限，直接在本仓库提，我们的工程师会处理
- name: 规矩、流程、权限
  url: https://github.com/northpeak/wiki/issues/new/choose
  about: 本 org 本身的规矩和权限，到 wiki 提
```

**基础设施仓：**

```yaml
blank_issues_enabled: false
contact_links:
- name: 规矩、流程、权限
  url: https://github.com/northpeak/wiki/issues/new/choose
  about: 本 org 本身的规矩和权限，到 wiki 提
```

注意两边**不对称**：基础设施仓**没有**指回训练仓的链接。因为基础设施仓的主要用户（GKE 组、网络组）打不开训练仓，
给一个点开是 404 的链接只会让人困惑。训练组能看两边，在训练仓的新建页能看到去 infra 的链接；
链接说明里写明「打不开说明你没有权限，直接在本仓库提」，照顾到合作方这类只能看训练仓的人。

**`blank_issues_enabled: false`**：关掉「Open a blank issue」入口，所有 issue 都必须走模板，这样 type 标签永远不会漏。

## 4.4 命令行建 issue：和网页填的一样

AI 助手用命令行建不出网页表单，所以规则要求：**先判断属于哪一类模板，然后正文用 `### 字段名` 作小标题、按模板的顺序写，标签打模板对应的那一个 type。**
这样建出来的 issue 和人在网页上填的一模一样（网页表单提交后，GitHub 生成的正文就是 `### 字段名` + 内容）。

```bash
REPO=northpeak/project-management
cat > /tmp/body.md <<'MD'
### 问题描述

> 客户原话，一字不改

### 跟哪块有关

不知道 / 都不是

### 代码与版本

northpeak/maxtext @ modelx @ 1a2b3c4
jax 0.11.1 / libtpu 0.0.46
MD
gh issue create -R $REPO --title "修复 FP8 下 MoE 路由 NaN" --label type/bug --body-file /tmp/body.md
```

**标题规则**：动词开头的一句话，不超过 60 字，不带句号。例：`接入 ModelX-VL 的视觉编码器`、`修复 FP8 下 MoE 路由 NaN`。

## 4.5 给标签和模板做变更

- 加、改、删标签：在 `wiki` 开 issue，必要时写 RFC，Owner 或 Maintain 执行，`AGENTS.md` 同步更新
- 删标签前**先确认用这个标签的 issue 数为 0**：`gh issue list -R <repo> -s all -l <标签> -L 1000`。删除后已关闭 issue 上的标签不能恢复
- 改模板：模板属于「记录类改动」，issue 仓里直接推 `main`，提交信息写清改了什么、带 `Refs #<issue号>`（第 7 章）
- 推模板之前查 YAML 语法：`python3 -c 'import yaml,sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]' *.yml`。
  推之后在新建页确认每个模板都能打开——**GitHub 对表单格式错误只在页面上提示**，YAML 合法但字段不对时，模板会从新建页上静默消失

## 4.6 复刻清单

- [ ] 删掉新仓库自带的默认标签（`bug`、`enhancement`、`good first issue` 等）
- [ ] 按 4.1 建标签：用 `appendix/scripts/setup-labels.sh`（第 15 章第 5 步），它会顺带删掉 GitHub 默认标签
- [ ] 把附录里的模板拷进 `.github/ISSUE_TEMPLATE/`，把 `northpeak` 换成你的 org，把领域选项换成你的
- [ ] 写 `config.yml`，注意不对称
- [ ] 在新建页逐个打开模板确认
- [ ] 把标签表和下拉枚举写进 `AGENTS.md`
