# NorthPeak wiki

NorthPeak：<一句话说 org 名的来历，和客户、产品都无关>。

NorthPeak 的规矩、设计文档和新人入门都在这里。

**这里的规矩主要写给 AI 编码助手**（Codex、Claude Code、Antigravity 等）：它们照着写 issue、PR、打标签、改看板，项目才管得利索。

- **AI 助手**：读 [`AGENTS.md`](AGENTS.md)（Codex、Antigravity 直接读它；Claude Code 通过 `CLAUDE.md` 引用它）
- **人**：读 `docs/onboarding/project-management.md`，那里讲每条规矩为什么这么定

## 这个 org 管什么

管三类工程问题：

- **模型训练和推理**：模型接入、精度对齐、性能优化、kernel、框架改动
- **GKE on TPU**：切片、Kueue、device plugin、节点池、维修与健康
- **网络**：ICI / DCN / OCS、VPC、NAT、DNS、多网卡

商务和交付治理不在这里。

## 目录

| 路径 | 内容 |
|---|---|
| `docs/onboarding/project-management.md` | 项目管理守则：任务怎么分层、怎么流转、PR 怎么写、数字怎么留证 |
| `docs/onboarding/working-in-northpeak.md` | 各个仓库管什么、客户问题怎么记、怎么改 MaxText（带真实例子） |
| `docs/onboarding/permissions.md` | 谁能看什么、谁能改什么 |
| `docs/rfc/` | 设计文档（RFC）：模板、索引、提案 |
| `docs/best-practices/` | 代码评审、编码规范；[TPU 训练数值差异速查](docs/best-practices/tpu-numerics.md) |
| `AGENTS.md` / `CLAUDE.md` | AI 助手行为规范。**每个代码仓库根目录都要放一份**，内容与这里一致（改完用 `scripts/sync-agents.sh` 同步） |
| `scripts/sync-agents.sh` | `AGENTS.md` 改完合并后，一条命令给各仓库开同步 PR |
| `scripts/board.sh` | 一条命令把 issue 加进看板、设大小和状态 |
| `.github/` | issue / PR 模板，`pr-check` 工作流（检查关联 issue 和偏差栏）；新仓库照抄 |

## 命名

自研工具和服务用**<一个主题>**命名：<例：Orion、Vega、Lyra……>
半年后说「去看 Vega 的 issue」，所有人都知道是哪块。上游 fork 保留原名。

**不要用真实芯片的内部代号给任何东西起名**——org 名和仓库名对外可见。
