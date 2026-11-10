# 第 2 章 org 与仓库拓扑

整个 org 只有四类仓库；issue 只开在 issue 仓，代码仓只收 PR，规矩单独放一个仓库。

## 2.1 一张图

```
<org>（GitHub org，免费档）
│
├── .github-private        org 主页（只有成员看得到的那一版）
│
├── wiki                   规则仓：AGENTS.md、守则、RFC、新人入门、脚本
│                          ── 规矩、流程、权限的 issue 提在这里
│
├── project-management     issue 仓 A（例：训练与推理）
│   ├── library/  meetings/  recipes/  repro/  assets/issues/
│                          ── 这一方向的项目 issue 全在这里
│
├── project-management-infra   issue 仓 B（例：GKE on TPU 与网络）
│   ├── library/  meetings/  recipes/  repro/  assets/issues/
│                          ── 这一方向的项目 issue 全在这里
│
├── maxtext                代码仓：上游项目的私有副本（长期分叉）
├── numerics-kit                  代码仓：自研工具
├── gke-component-a …       代码仓：上游组件的私有副本（跟随副本，自动同步）
│                          ── 代码仓一律关闭 Issues，只收 PR
│
└── recipes  repro  library    已归档（只读）：早期按内容类型分的仓库
```

整个 org 只有四类仓库：

| 类 | 仓库 | Issues | 收什么 |
|---|---|---|---|
| 主页仓 | `.github-private` | 关（建议；原项目这里开着但没人用） | org 主页 |
| 规则仓 | `wiki` | **开** | 规则、设计文档、规矩类 issue |
| issue 仓 | `project-management`、`project-management-infra` | **开** | 项目 issue；本方向的交付物目录 |
| 代码仓 | 其余 | **关** | 只收 PR |

## 2.2 为什么 issue 只开在 issue 仓

**规则：项目上的 issue（客户问题、开发任务、bug、环境依赖），不管最后改哪个仓库的代码，都提在 issue 仓。代码仓不开 issue。**

原因有三个：

1. **客户报上来的是现象，不是组件**。客户说「切片起不来」，多半分不清是调度器、device plugin 还是节点池的问题。
   要求客户先判断提到哪个代码仓，等于让客户做分诊
2. **很多问题没有对应的代码仓**。网络、配额、环境依赖、「这个现象正常吗」，都不属于任何一个代码仓
3. **入口越少越好找**。客户只需要记住一两个地方。issue 分散在十个代码仓里，没人看得全

代码仓的 PR 通过正文里的 `Closes <org>/<issue 仓>#号` 关联到 issue 仓的 issue。GitHub 支持跨仓库关闭，合并 PR 时自动关掉 issue（合进默认分支时才生效，见第 7 章）。

**规矩、流程、权限类的 issue 提在 `wiki`**，哪怕这次改动涉及多个仓库。两个 issue 仓只放项目本身的事，不放规矩和权限。
这样规则仓的 issue 列表就是「规则改动史」，issue 仓的 issue 列表就是「项目问题史」，两边不互相淹没。

## 2.3 为什么 issue 仓有两个

**规则：受众不同，就分 issue 仓。**

原项目的客户有两拨人：训练组关心模型、框架、精度、性能；GKE 组和网络组关心切片、调度、节点池、网络。
一开始所有 issue 都在一个仓库，靠 `area/*` 标签区分，三个问题很快暴露：

1. **标签分不开通知**。GitHub 只能按仓库订阅，不能按标签订阅。GKE 组的人订阅了仓库，就会收到训练组的全部 issue
2. **建 issue 时分不开**。规矩要求建 issue 时不打 `area/*`（还没查清是哪块），所以分诊前根本分不开
3. **一套模板两拨人用**。训练的模板问「模型、数据与并行」，GKE 的问题要的是「集群版本、节点池、`kubectl` 输出」

于是拆成两个仓库，全局进度靠 org 看板汇总（第 5 章）。

**复刻时怎么定拆不拆**：问三个问题。

| 问题 | 都是「是」就拆 |
|---|---|
| 两拨人订阅的内容是否大部分不重叠？ | |
| 分诊的人是不是两拨？ | |
| 需要的模板字段是否明显不同？ | |

只有一拨受众，就只建一个 `project-management`。不要预先拆：拆仓库容易，合并难（issue 编号会冲突）。
原项目先一个仓库跑了两周，等 GKE 组真的进来了才拆，代价是转移两条 issue，可以接受。

**只有一个 issue 仓时**，书里关于第二个仓库的内容都可以删掉：转移规则（第 6 章 6.6）、跨仓库引用的可见性问题、`config.yml` 里的互指链接、`area/*` 只留一组、客户子团队可以不建（客户直接进 `customer`，`customer` 对 issue 仓授 Write）、`sync-agents.sh` 的 `DIRECT` 只留一个、看板不用分视图、例会纪要只有一个 `meetings/`。第 15 章按「只建一个」走，跳过所有 infra 仓的命令。

**两个 issue 仓怎么划界**（原项目的划法，复刻时换成你的领域）：

| | `project-management`（训练与推理） | `project-management-infra`（基础设施） |
|---|---|---|
| 管什么 | **作业里面的事**：模型接入、MaxText、JAX / XLA / libtpu、kernel、推理、PyTorch on TPU、精度、性能（步时、MFU、显存）、镜像与依赖、数据读取与 checkpoint；以及不属于另一边的其他项目事务 | **集群和节点层面的事**：切片调度与供给、device plugin、Kueue、JobSet、节点池（创建、升级、扩缩）、维修与健康（含芯片、主机故障）、存储挂载（Lustre、GCSFuse、Hyperdisk 等 CSI）、网络（ICI / DCN / OCS、VPC、NAT、DNS、多网卡）、配额与容量 |
| 对应客户组 | 训练组 | GKE 组、网络组 |

注意左边最后一句「以及不属于另一边的其他项目事务」：**两个仓库中必须有一个是兜底的**，
否则跟任何代码都无关的项目事务（比如「客户要一份交付验收清单」）就没地方放。

**网络为什么没有单独再拆一个仓库**：当时没有网络 issue，网络问题大多在集群层面，和节点池、切片交叉，
厂商一侧由同一批人分诊。再拆一个入口只会让客户多一次选择。等网络 issue 真多起来、分诊的人分开了，再按 2.3 的三个问题判断。

## 2.4 为什么交付物放进 issue 仓

每个 issue 仓下有四个目录：

| 目录 | 放什么 | 谁维护 |
|---|---|---|
| `library/` | 给客户的成品文档：手册、讲义、课件、技术报告 | 厂商 |
| `meetings/` | 例会纪要与 slides | 厂商 |
| `recipes/` | 照着就能跑的配方：手册 + 脚本 + 配置，版本钉死 | 厂商与客户 |
| `repro/` | issue 的复现：脚本、代码、日志 | 厂商与客户 |
| `assets/issues/` | issue 里用的截图（不算交付物，是 issue 的附件） | 都可以 |

这四个目录原来是三个独立仓库（`library`、`recipes`、`repro`）。并进 issue 仓的原因是**可见性**：
GKE 组不该看训练方向的材料，而 GitHub 的读权限最小单位是仓库。按内容类型分的仓库对所有客户可见，和按受众划的边界不一致；
要对齐，要么把三个仓库按方向各拆两份（变成六个），要么并进已经按受众划好的两个 issue 仓。后者自有仓库从 5 个减到 2 个。

**一个推论**：两组都要看的内容（比如全体例会纪要、集群交付手册）放在**两组都能看的那个仓库**。
原项目里训练组也能看 infra 仓，所以全体内容放 infra 仓。复刻时先定可见性矩阵（第 3 章），再定共享内容放哪。

旧的三个仓库没有删，而是**归档**（只读）。归档后旧的 commit permalink 照常能打开，issue 评论里的老链接不会断。

## 2.5 规则仓 `wiki` 的结构

```
wiki/
├── AGENTS.md                  给 AI 助手的规则（权威版本，同步到各仓库）
├── CLAUDE.md                  一行：@AGENTS.md
├── README.md                  这个 org 管什么、去哪读什么、命名规矩
├── docs/
│   ├── onboarding/
│   │   ├── project-management.md   项目管理守则：每条规矩为什么这么定（给人）
│   │   ├── working-in-<org>.md     各仓库管什么、客户问题怎么记、怎么改代码（带例子）
│   │   └── permissions.md          谁能看什么、谁能改什么
│   ├── rfc/
│   │   ├── index.md                RFC 索引表
│   │   ├── template.md
│   │   └── NNNN-<英文简述>.md
│   └── best-practices/             代码评审、编码规范、领域速查
├── scripts/
│   ├── board.sh                    一条命令把 issue 加进看板、设字段
│   └── sync-agents.sh              把 AGENTS.md 同步到各仓库
└── .github/
    ├── ISSUE_TEMPLATE/             规矩类 issue 模板：加人／撤人、任务、Bug
    ├── pull_request_template.md
    └── CODEOWNERS
```

为什么叫 `wiki` 而不用 GitHub 自带的 Wiki 功能：自带 Wiki 不走 PR、没有评审、改动不进 issue 时间线。
规则必须走 PR，所以用普通仓库。所有仓库的 GitHub Wiki 功能都**关闭**，免得有人往里写东西。

## 2.6 org 主页

GitHub org 有两种主页：`.github` 仓库的 `profile/README.md` 对所有人可见；
`.github-private` 仓库的 `profile/README.md` 只对 org 成员可见。**用 `.github-private`**——主页里会列仓库、看板、正在做的项目，
这些不该对外。org 本身是公开可搜的，所以公开主页（如果有）里不出现客户名和项目细节。

主页是客户进 org 后看到的第一个页面，它要做到：

1. **两个大按钮组**：每个 issue 仓一组「提交 issue」「查看 issue」，按钮直接链到 `issues/new/choose`
2. **一句话划界**：每组按钮上方一行说清这个仓库管什么
3. **「拿不准就提到现象出现的那一边，我们分诊后会移到对的仓库，不用重提」**——降低提 issue 的心理门槛
4. **模板表**：有几类模板、什么时候用；**只有「问题描述」必填**
5. **「让 AI 助手帮你提」**：告诉客户跟助手说「先读 AGENTS.md，再按里面的规矩来」
6. **为什么用 issue 不用聊天**：四句话（问题不会丢、一条完整的线、状态一眼看清、经验攒下来）
7. **正在做**：开着的 issue、看板、实施手册、代码分支的链接
8. **仓库表**：每个仓库放什么
9. **第一次来**：人读哪两篇，AI 读哪个文件；三条最常用的规矩

完整的主页模板见 [`appendix/templates/org-profile/README.md`](../appendix/templates/org-profile/README.md)。

## 2.7 每个仓库的设置（建议值）

下表是本书建议的设置。原项目大部分仓库如此，个别仓库的 Projects 标签页、「合并后自动删分支」没有统一。

| 设置 | 规则仓 | issue 仓 | 代码仓 |
|---|---|---|---|
| 可见性 | Private | Private | Private |
| Issues | 开 | 开 | **关** |
| Wiki | 关 | 关 | 关 |
| Discussions | 关 | 关 | 关 |
| Projects 标签页 | 开（默认） | 开 | 开。不建仓库级看板，只用 org 看板 |
| 允许 fork | 否（org 级设置） | 否 | 否 |
| 默认分支 | `main` | `main` | 跟上游（`main` 或 `master`） |
| 合并方式 | merge / squash / rebase 都允许 | 同左 | 同左；迁移历史时临时只留 merge commit（第 16 章） |
| 合并后自动删分支 | 开 | 开 | 开 |
| GitHub Actions | org 级停用（见第 14 章） | | |

**为什么所有仓库都是 Private**：org 名是公开的，私有仓库里才能放客户相关的东西。规则是「建仓库一律选 Private」，
免费档没法在设置里禁止成员建公开仓库，这一条靠规矩：误建了公开仓库，立刻告诉管理员改成私有（第 3 章）。

**为什么禁止 fork 私有仓库**：fork 出去的副本不受 org 权限管理，人离开团队后副本还在。
另外外部 fork 提的 PR 触发不了需要密钥的验证。规则是**分支推在本仓库，不从个人 fork 提 PR**。

## 2.8 每个仓库根目录都该有的文件

| 文件 | 内容 |
|---|---|
| `AGENTS.md` | 和 `wiki/AGENTS.md` 逐字节相同，由 `sync-agents.sh` 同步，**不手改**。新仓库建好就要加进同步目标——原项目有三个后加的代码仓忘了加，那里的 AI 助手读不到规矩 |
| `CLAUDE.md`、`GEMINI.md` | 各一行 `@AGENTS.md`。Claude Code 读 `CLAUDE.md`、Gemini CLI 默认读 `GEMINI.md`，两者都支持 `@` 引用另一个文件；Codex、Antigravity 等直接读 `AGENTS.md`（原项目只放了 `CLAUDE.md`，`GEMINI.md` 是本书补的） |
| `README.md` | 这个仓库管什么、不管什么、去哪提 issue、给 AI 助手的一句话 |

代码仓另有：

| 文件 | 内容 |
|---|---|
| `FORK.md` | 上游私有副本才有：跟上游的方式、分支表、同步记录（第 9 章） |
| `.github/pull_request_template.md` | 四栏 PR 模板，关联行写死 issue 仓的全名（第 7 章） |
| `.github/CODEOWNERS` | 默认 `* @<org>/maintainers`，客户共同维护的目录加客户团队 |

**为什么每个仓库都放一份 `AGENTS.md`，而不是只放在 `wiki`**：AI 助手只读当前工作目录里的文件。
客户在 `maxtext` 里开一个助手，它看不到 `wiki`。

## 2.9 命名

- **org 名和仓库名对外可见**：不用客户名，不用未公开的产品或芯片代号。取一个和客户、产品都无关的名字
- **自研工具和服务用一个主题命名**：比如用星座（Orion、Vega、Lyra……）。
  半年后说「去看 Vega 的 issue」，所有人都知道是哪块
- **上游的私有副本保留上游原名**（`maxtext`、`gke-component-a`），不改名。改名会让人找不到对应的上游
- **issue 仓用 `project-management` 加后缀**，两个仓库在列表里排在一起
- 目录名、分支名、文件名用英文短横线（`modelx-v5p-poc`、`feat/42-vl-encoder`）

## 2.10 跨仓库引用：一律写全名

**两个 issue 仓的编号各自从 1 开始。跨仓库引用 issue 一律写全仓库名：`<org>/project-management-infra#3`，不写裸的 `#3`。**

裸的 `#3` 在 GitHub 上会按**当前仓库**解析。在 `maxtext` 的 PR 里写 `Closes #3`，GitHub 会去找 `maxtext#3`
（代码仓关了 Issues，找不到），而不是你想关的那个 issue。在 infra 仓的提交信息里写 `#5`，会在 infra 仓不相干的 #5 时间线上留下一条引用。

还有一层：**不是每个人都打得开另一边的链接**。GKE 组打不开 `project-management`，合作方打不开 `project-management-infra`。
要某个人看的结论，写进他看得到的那条 issue，不能只贴一个链接。

## 2.11 复刻清单

- [ ] 定 org 名（不含客户名和代号）
- [ ] 按 2.3 的三个问题决定 issue 仓建一个还是两个，写下划界表，指定兜底的那个
- [ ] 建 `wiki`、issue 仓、`.github-private`，按 2.7 设置
- [ ] 代码仓按需建，关 Issues
- [ ] 每个仓库放 `AGENTS.md`、`CLAUDE.md`、`README.md`
- [ ] 写 org 主页

具体命令见第 15 章。
