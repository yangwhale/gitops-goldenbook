# project-management

**训练与推理的 issue 在这里提**：客户问题、bug、开发任务、环境和依赖，以及跟任何代码都无关的项目事务。GKE on TPU 和网络（集群和节点层面）的 issue 在 [project-management-infra](https://github.com/northpeak/project-management-infra)，划界见它的 README。代码仓库（`maxtext`、`recipes` 等）只收 PR，不开 issue。

两个仓库的 issue 编号各自从 1 开始，跨仓库引用时写全仓库名，如 `northpeak/project-management#22`。

有哪些模板、怎么填、为什么用 issue，见 [org 主页](https://github.com/northpeak)。

- 按领域分类用 `area/*` 标签，不按仓库分
- 本仓库的目录：
  - [`library/`](library/)：给客户的成品文档（MoE 训练优化、Training on TPUs 等）
  - [`meetings/`](meetings/)：训练方向例会的纪要与 slides
  - [`recipes/`](recipes/)：照着就能跑的配方和脚本
  - [`repro/`](repro/)：本仓库 issue 的复现；客户放不进 issue 的脚本、日志也放这里
  - `assets/issues/`：issue 用的截图
- `library/`、`meetings/`、`recipes/`、`repro/` 的改动走 PR；issue 模板、截图这类记录，以及客户放进 `repro/issues/` 的材料直接推
- 规矩、流程、权限（含加人撤人）的 issue 放 [wiki](https://github.com/northpeak/wiki/issues)

## 给 AI 编码助手

我们给 AI 助手（Codex、Claude Code、Antigravity、Gemini CLI 等）准备了行为规范：本仓库根目录的 [`AGENTS.md`](AGENTS.md)（Claude Code 读 `CLAUDE.md`，它引用 `AGENTS.md`）。里面写明了怎么选模板、正文写哪几个小标题、打什么标签、怎么加进看板。

让助手帮你提 issue 时，跟它说一句「**先读 AGENTS.md，再按里面的规矩提**」就行。
