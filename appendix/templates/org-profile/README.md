# NorthPeak

<一句话说 org 名的来历，和客户、产品都无关>。NorthPeak 管三类工程问题：TPU 上的**模型训练和推理**（模型接入、精度对齐、性能优化、kernel、框架改动），**GKE on TPU**（切片、Kueue、device plugin、节点池、维修与健康），以及**网络**（ICI / DCN、VPC、NAT、DNS）。

<p align="center"><b>训练与推理</b>：模型、框架、精度、性能、镜像与依赖</p>
<p align="center">
  <a href="https://github.com/northpeak/project-management/issues/new/choose"><img src="submit-issue.svg" alt="提交训练与推理的 issue" width="320"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/northpeak/project-management/issues"><img src="view-issues.svg" alt="查看训练与推理的 issue" width="320"></a>
</p>
<p align="center"><b>GKE on TPU 与网络</b>：切片、Kueue、device plugin、节点池、维修、存储挂载、网络、配额</p>
<p align="center">
  <a href="https://github.com/northpeak/project-management-infra/issues/new/choose"><img src="submit-issue.svg" alt="提交 GKE on TPU 与网络的 issue" width="320"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/northpeak/project-management-infra/issues"><img src="view-issues.svg" alt="查看 GKE on TPU 与网络的 issue" width="320"></a>
</p>

## 有问题，就提 issue

这个入口是**给客户工程师准备的**，Google 同事也在这里提。问题分两个入口：

- **训练与推理**（作业里面的事：MaxText、JAX / XLA、kernel、推理、torch TPU、精度、性能、镜像与依赖，以及跟任何代码都无关的项目事务）→ [project-management](https://github.com/northpeak/project-management/issues)
- **GKE on TPU 与网络**（集群和节点层面：切片、device plugin、Kueue / JobSet、节点池、维修与健康、存储挂载、ICI / DCN、VPC、NAT、DNS、配额与容量）→ [project-management-infra](https://github.com/northpeak/project-management-infra/issues)

拿不准就提到现象出现的那一边，我们分诊后会移到对的仓库，不用重提。

训练与推理准备了 7 类模板，选一个，按栏填就行（GKE 与网络那边是 6 类，没有「精度对不齐」，字段换成集群、节点池、组件版本和 `kubectl` 输出）：

| 模板 | 什么时候用 |
|---|---|
| 报错与故障 | 报错、崩溃、卡死、NaN；镜像与依赖出问题 |
| 精度对不齐 | loss、梯度、输出和 GPU / Megatron / 另一种并行对不上 |
| 性能不达预期 | 步时、吞吐、MFU、显存 / OOM 不达预期 |
| 功能与开发任务 | 想要新模型、新功能、kernel 支持，或一件开发工作 |
| 设计与调研 | 方案怎么选、技术调研 |
| 使用问询 | 怎么用、某个现象是否符合预期 |
| 跟踪总表 | 几个问题其实是同一件事时，串起来跟踪 |

每个模板**只有「问题描述」必填**，用自己的话说清楚就行，其余都是建议。能写上运行条件（代码分支和 commit、版本号、芯片和规模、模型数据和并行、启动命令、run-ID）最好，我们拿到就能复现；不清楚的空着，我们来补。截图直接拖进输入框。**选对模板，就已经帮了大忙。**

## 让 AI 助手帮你提

我们给 AI 编码助手（Codex、Claude Code、Antigravity、Gemini CLI 等）准备了行为规范：每个仓库根目录都有一份 [`AGENTS.md`](https://github.com/northpeak/project-management/blob/main/AGENTS.md)，内容相同。助手读完就知道该选哪个模板、正文怎么写、打什么标签、提 PR 要注意什么。

用助手时跟它说一句「**先读 AGENTS.md，再按里面的规矩来**」就行。

## 为什么用 issue，不用聊天

- **问题不会丢**。聊天记录会被刷走、换群、换人；issue 一直在，项目做大了上千个也能搜到
- **一个问题一条完整的线**。提问、截图、每一次分析和结论按时间记在同一个地方，三个月后还能看懂当时为什么这么定
- **状态一眼看清**。每个问题在看板上有状态：处理中、卡住（等谁）、已解决
- **经验攒下来**。解决过的问题就是下一次的答案，新同事、新项目直接翻


## 正在做

**<项目代号> POC**：<一句话描述在做什么>。

| 要看什么 | 去哪 |
|---|---|
| 开着的问题 | [org 里所有未关闭的 issue](https://github.com/issues?q=org%3Anorthpeak%20is%3Aissue%20is%3Aopen) |
| 看板 | [NorthPeak 看板](https://github.com/orgs/northpeak/projects/1) |
| 实施手册 | <链到 recipes/ 里的主配方> |
| 代码 | [maxtext · `modelx` 分支](https://github.com/northpeak/maxtext/tree/modelx) |

## 仓库

| 仓库 | 放什么 |
|---|---|
| [wiki](https://github.com/northpeak/wiki) | 规矩（`AGENTS.md`）、项目管理守则、RFC、新人入门；规矩和权限的 issue |
| [project-management](https://github.com/northpeak/project-management) | 训练与推理的 issue；这一方向的文档、例会纪要、配方和复现 |
| [project-management-infra](https://github.com/northpeak/project-management-infra) | GKE on TPU 与网络的 issue；这一方向的文档、例会纪要、配方和复现 |
| [maxtext](https://github.com/northpeak/maxtext) | MaxText 私有副本 + 客户模型接入 |
| `recipes`、`repro`、`library` | 已归档（只读），内容已按方向并进两个 issue 仓库 |

## 第一次来

- **人**：先读 [在 NorthPeak 里怎么干活](https://github.com/northpeak/wiki/blob/main/docs/onboarding/working-in-northpeak.md)，再读 [项目管理守则](https://github.com/northpeak/wiki/blob/main/docs/onboarding/project-management.md)
- **AI 编码助手**：读任一仓库根目录的 `AGENTS.md`，照做（见上面「让 AI 助手帮你提」）

三条最常用的规矩：没有 issue 不写代码；PR 必须关联 issue 并填「和原计划的偏差」；写进 issue 的数字必须附来源。
