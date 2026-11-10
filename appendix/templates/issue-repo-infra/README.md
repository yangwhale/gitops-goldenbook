# project-management-infra

**GKE on TPU 和网络的 issue 在这里提**：集群和节点层面的问题、开发任务、使用问询。

## 哪些问题在这里

- 切片调度与供给、device plugin、Kueue、JobSet
- 节点池的创建、升级、扩缩；维修与健康（含芯片、主机故障）
- 存储挂载（Lustre、GCSFuse、Hyperdisk 等 CSI）
- 网络：ICI / DCN / OCS、VPC、NAT、DNS、多网卡；配额与容量

拿不准是不是这一类也可以在这里提，我们分诊后处理，结论会回到你提的这条 issue，不用重提。各仓库的 issue 编号都从 1 开始，引用时写全仓库名，如 `northpeak/project-management-infra#3`。

有哪些模板、怎么填、为什么用 issue，见 [org 主页](https://github.com/northpeak)。

- 按领域分类用 `area/*` 标签
- 本仓库的目录：
  - [`library/`](library/)：给客户的成品文档（集群交付手册、GKE on TPU 材料）
  - [`meetings/`](meetings/)：GKE、网络方向和全体例会的纪要与 slides
  - [`recipes/`](recipes/)：照着就能跑的配方和脚本
  - [`repro/`](repro/)：本仓库 issue 的复现
  - `assets/issues/`：issue 用的截图
- `library/`、`meetings/`、`recipes/`、`repro/` 的改动走 PR；issue 模板、截图这类记录，以及客户放进 `repro/issues/` 的材料直接推
- GKE 组件（`gke-component-a`、`gke-component-b`、`gke-component-c`、`gke-component-d`、`tpu-device-plugin`）的改动在各自仓库提 PR，正文写 `Closes northpeak/project-management-infra#<号>`
- 规矩、流程、权限（含加人撤人）的 issue 放 [wiki](https://github.com/northpeak/wiki/issues)

## 给 AI 编码助手

我们给 AI 助手（Codex、Claude Code、Antigravity、Gemini CLI 等）准备了行为规范：本仓库根目录的 [`AGENTS.md`](AGENTS.md)（Claude Code 读 `CLAUDE.md`，它引用 `AGENTS.md`）。里面写明了怎么选仓库和模板、正文写哪几个小标题、打什么标签、怎么加进看板。

让助手帮你提 issue 时，跟它说一句「**先读 AGENTS.md，再按里面的规矩提**」就行。
