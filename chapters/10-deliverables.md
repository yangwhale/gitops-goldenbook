# 第 10 章 交付物目录：library、recipes、repro

每个 issue 仓下有四个交付物目录。`meetings/` 见第 11 章，这里是另外三个。

| 目录 | 一句话 | 谁维护 | 怎么改 |
|---|---|---|---|
| `library/` | 给客户的成品文档 | 厂商 | PR |
| `recipes/` | 照着就能跑的配方，版本钉死 | 厂商与客户 | PR |
| `repro/` | issue 的复现 | 厂商与客户 | PR；**客户的材料直接推** |

三者的区别在**生命周期**：

```
issue 里排查  ──→  repro/（这个问题怎么复现，issue 关了就冻结）
                      │ 沉淀出要长期用的流程
                      ▼
                   recipes/（照着就能从空项目跑到结果，钉死版本、发版打 tag）
                      │ 整理成给人读的文档
                      ▼
                   library/（手册、讲义、报告）
```

## 10.1 `library/`：给客户的成品文档

**放什么**：手册、讲义、课件、技术报告。已经写完、给客户读的东西。

**规矩**：

- 每份材料一个目录，目录名用英文短横线，里面放正文（HTML / PDF / Markdown）和它用到的图
- 新材料放进来后在 `library/README.md` 的索引表加一行
- 网页版材料（HTML）要能离线打开：下载仓库后用浏览器打开 `library/<材料>/index.html` 就能读，图片用相对路径
- 有在线版的，索引表里同时给在线链接；**新读者该先看哪个**写清楚（比如完整版 + 简洁版，引导先看简洁版）
- 已经在别处的材料（比如配方手册在 `recipes/` 里）**不重复放**，索引表里指过去
- 公开的课程、公开文章直接给链接，不在仓库里存副本
- 另一个方向的材料在另一个 issue 仓的 `library/`，README 里指过去

索引表的样子：

```markdown
# library

训练方向给客户的成品文档：手册、讲义、课件、技术报告。由厂商维护。

每份材料一个目录，目录名用英文短横线，里面放正文和它用到的图。新材料放进来后在下表加一行。

| 材料 | 目录 | 版本 |
|---|---|---|
| MoE 模型的训练优化 | [`moe-optimization/`](moe-optimization/)（在线完整版；**新读者先看简洁版**，约 60 分钟） | 线上版 2026-04-01 |
| 加速器上的训练：基础设施、并行选择、容错（英文讲义） | [`training-on-accelerators/`](training-on-accelerators/) | 2026-04-04 |
| ModelX 预训练 POC 实施手册 | 在本仓库的 [`recipes/modelx-poc/`](../recipes/modelx-poc/)，这里不重复放 | — |

GKE 与网络方向的材料在 [`project-management-infra/library/`](https://github.com/northpeak/project-management-infra/tree/main/library)。
```

**什么不放进 `library/`**：还没定稿的、只是内部讨论用的、或者涉及别的客户的材料。成品文档代表厂商的正式立场，拿不准就先不放。

## 10.2 `recipes/`：照着就能跑的配方

**放什么**：每个目录是一套完整的「手册 + 脚本 + 配置」，从空项目到跑出结果。一个 POC、一套可交付的训练方案、一个集群搭建流程。

**规矩**：

- 一个配方一个目录，目录名用英文短横线
- 目录里的 `README.md`（或 `RUNBOOK.md`）写清：适用的环境和版本、前置条件、一步步的命令、怎么验证跑通
- **代码一律钉死版本：commit + sha256**。要改代码，去代码仓开分支，改好后在配方里**换新的钉子**（新的 commit + sha256），并在手册里写一行为什么换。**不在配方里直接改钉死的代码**
- 镜像写 `@sha256:<digest>`，不写会漂移的 tag
- **发版打 tag，名字带路径前缀：`recipes/<配方名>/v<N>`**。一个仓库里有多个配方，tag 不带前缀会撞
- 改动走 PR
- `recipes/README.md` 有一张索引表：目录、内容、状态（进行中 / 可用）

**为什么钉 sha256 而不只是 commit**：配方里常有代码包（tgz），commit 说的是代码仓的版本，sha256 证明你手上的包就是那个版本打出来的、没被改过。
原项目的配方要求「照着做得到同样的结果」，任何一个版本漂移都会让结果对不上。

**配方里的数字要说清口径**。例：「MFU 公式原值 41.20%，扣掉不训练的模块的反向多计后约 40.95%」。数字的规矩见第 12 章。

`recipes/` 下和客户共同维护的目录，可以在 `CODEOWNERS` 里加客户团队。注意 code owner 必须对仓库有 Write：issue 仓上写子团队（`training`、`gke`），不能写父团队 `customer`（它对 issue 仓没有授权，这一行会被 GitHub 忽略）：

```
*                 @northpeak/maintainers
/recipes/modelx-poc/  @northpeak/googlers @northpeak/training
```

## 10.3 `repro/`：issue 的复现

`repro/` 里有两种东西，规矩完全不同。

### 第一种：客户放的材料——什么规矩都没有

**客户在 issue 里放不下的东西（测试脚本、复现代码、日志文件等），放到 `repro/issues/<issue号>-<简述>/`，在 issue 里引用即可。**

- 不要求 README 或 `card.yaml`
- 不用登记进目录清单
- **可以直接推，不提 PR**
- issue 里能写清楚的，就不建目录

> 两个 issue 仓用同一种布局 `repro/issues/<号>-<简述>/`。原项目的 infra 仓少了一层 `issues/`，和训练仓不一致，AI 助手容易放错；模板已统一。

**为什么这么宽松**：客户放材料是在帮我们。加任何门槛，客户就会把文件发在聊天群里，然后过期、丢失。
我们后续要把它做成验证过的复现时，再补 `card.yaml` 并登记。

> 原项目在规矩里写这一条时，几次改措辞，最后定下来的原则是：「目录可有可无，有必要放东西才放」。
> 写给客户的话越短越好：不要规定分支名、不要规定描述格式。

### 第二种：验证过的复现——规矩很严

厂商把一个 issue 的结论做成「任何人照着都能重跑出同样数字」的复现时：

- 一个 issue 一个目录 `issues/<issue号>-<英文短横线简述>/`，issue 号指本仓库
- **必须有 `README.md` 和 `card.yaml`**
- 新增或删除带 `card.yaml` 的目录时，同步 `repro/README.md` 的「目录清单」表
- `card.yaml` 里镜像一律写 `@sha256:<digest>`；代码写 commit 或代码包路径 + sha256；产物写到 `gs://<POC 桶>/issues/<issue号>/<运行名>/`
- **不放客户模型的权重、数据、未授权公开的代码**，只引用它们在客户项目里的路径和 sha256；不放任何一方公司内部的链接、主机名、工具包装
- **issue 关闭后目录冻结**，只改 README 顶部的结论；能复用的脚本提到 `common/`

目录结构：

```
repro/
├── README.md                 规矩 + card.yaml 字段表 + 目录清单
├── common/                   多个复现共用的脚本
│   ├── launch.sh             在一个固定规格的池上起一次训练或一个探针
│   ├── wait.sh               等作业结束：DONE / FAIL / NOTFOUND / 超时
│   ├── compare_metrics.py    逐步比较两份 metrics，报逐位相同的步数和第一处不同
│   ├── collect_env.sh        在 pod 里采集版本、拓扑、flag
│   └── check_dir_list.py     检查目录清单和实际目录一一对应
└── issues/
    └── 31-cp-loss-offset/
        ├── README.md         问题、结论链接（指向 issue 评论）、怎么复现、预期输出
        ├── card.yaml         运行清单
        └── *.py / *.sh       这个 issue 专用的探针和脚本
```

### `card.yaml`：运行清单

`card.yaml` 是这套做法里最「重」的一个文件，它让一个数字可以被任何人重跑出来。字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `issue` | 是 | `<org>/project-management#N` |
| `question` | 是 | 这个目录回答的**一个**问题 |
| `status` / `last_verified` | 是 | `verified`（至少一条运行按本仓库命令端到端重跑、结果与原始运行一致）/ `partial` / `failed`，以及最后一次验证的日期 |
| `scope` | 是 | 结论的适用范围（模型、硬件、规模、运行次数） |
| `env.image` | 是 | 必须是 `@sha256:<digest>` |
| `env.code` | 是 | `{repo, commit}`，或代码包 `{path, sha256}` |
| `env.probe` | 有探针时 | `{path, sha256}`；本目录里的副本写 `repo_copy` 并说明差异 |
| `env.jax` / `env.libtpu` | 是 | 版本号（换成你的项目的关键依赖） |
| `env.flags` | 是 | 编译和运行时开关 |
| `cluster` | 是 | 拓扑、主机数、每主机芯片数、池、启动脚本 |
| `B` | 否 | 命令里 `$B` 的值（产物根目录） |
| `runs[]` | 是 | 每次运行：`name`（也是产物目录 `$B/<name>/`）、`command`、`output`、`expected`；按本仓库命令重跑核对过的加 `verified`（日期与结果） |
| `analysis[]` | 有统计时 | 重算 issue 评论里统计数字的命令、预期值、`verified` |

一个缩短的例子（虚构）：

```yaml
# 复现清单：project-management#31 cp=4 时 loss 偏高
issue: northpeak/project-management#31
question: cp=4 比 cp=1 的 loss 高约 0.02，是不是 load balancing 重排后 loss mask 没跟着重排
status: verified   # cp4-fix-r19 已按本目录命令重跑，2000 步 loss 逐位相同
last_verified: 2026-04-09
scope: ModelX 32 层、v5p-128（4x4x8）、C4 2000 步、每组单次运行

B: gs://<POC 桶>/issues

env:
  image: <registry>/<image>@sha256:b152355a...
  jax: 0.11.1
  libtpu: 0.0.46
  code:
    before: {repo: northpeak/maxtext, commit: 1a2b3c4}
    after:  {repo: northpeak/maxtext, commit: 9a1c2e0}
  flags:
    rng: LIBTPU_INIT_ARGS 加 --xla_tpu_spmd_rng_bit_generator_unsafe=false

cluster:
  topology: 4x4x8
  hosts: 32
  chips_per_host: 4
  launcher: ../../common/launch.sh

runs:
  - name: 31/cp1-r17
    command: POOL=$POOL bash ../../common/launch.sh 31/cp1-r17 ...
    output: $B/31/cp1-r17/metrics_host0.txt
    expected: 第 2000 步 loss 2.4113
  - name: 31/cp4-fix-r19
    command: POOL=$POOL bash ../../common/launch.sh 31/cp4-fix-r19 ...
    output: $B/31/cp4-fix-r19/metrics_host0.txt
    expected: 第 2000 步 loss 2.4109
    verified: 2026-04-09，重跑 31/cp4-fix-r19-v，2000 步逐位相同
```

**几个关键设计**：

- **运行名就是产物目录**。`launch.sh` **不覆盖已有产物**：复现时把运行名换成自己的（`31/cp4-fix-r19-yourname`），照抄会被拒绝。这防止重跑覆盖掉原始证据
- **`status: verified` 有明确定义**：至少一条运行被端到端重跑、结果一致。没重跑过的只能是 `partial`
- **探针的仓库副本和实际运行的版本可能不同**（比如去掉了内部命名），记下两个 sha256，并说明差异只在注释
- **`question` 只能是一个问题**。一个目录回答一个问题，问题多了就拆目录

### 目录清单和检查

`repro/README.md` 末尾有一张「目录清单」表，每个带 `card.yaml` 的目录一行：

```markdown
| 目录 | issue | 运行 | 状态 |
|---|---|---|---|
| [`issues/31-cp-loss-offset/`](issues/31-cp-loss-offset/) | project-management#31 | 4 | verified（重跑 1 条 2000 步逐位相同） |
```

`common/check_dir_list.py` 检查：表里的目录都存在；带 `card.yaml` 的目录都登记了、指向本仓库、以 issue 号开头。
**不带 `card.yaml` 的目录（客户材料）不检查**，只在名字可疑时给警告——检查会扫整棵树，对客户材料报错会让别人无关的 PR 失败。

原项目用一个 GitHub Actions 工作流（`dir-list-check`）在 PR 改到 `repro/` 时跑这个脚本。Actions 停用后改为提 PR 前本地跑：
`python3 repro/common/check_dir_list.py repro <本仓库全名>`。

### 两个 issue 仓的复现不能混放

两个 issue 仓的编号各自从 1 开始，放在一起会撞号。所以：

- 每个 issue 仓的复现放自己的 `repro/`
- 产物放在共享的桶里时，**另一个仓库的 issue 加前缀**：`gs://<POC 桶>/issues/infra-<issue号>/<运行名>/`。infra 仓的 README 写明「`infra-` 前缀不能省」
- infra 的复现要用训练仓的 `launch.sh` 时，运行名写 `infra-<issue号>/<运行名>`

### 引用复现：用 commit permalink

**issue 里引用 `repro/` 里的数字时给三样：commit permalink、运行名、产物路径。**

```
https://github.com/northpeak/project-management/blob/<commit>/repro/issues/31-cp-loss-offset/card.yaml
```

**不用分支链接**（`/blob/main/...`）：分支会变，目录会挪，三个月后分支链接指向的可能是另一个内容，或者 404。permalink 永远指向那一刻的文件。

原项目把三个旧仓库并进 issue 仓时，旧仓库**归档而不删除**，就是为了保住 issue 评论里那些指向旧仓库的 permalink。

## 10.4 大文件

- PDF、图片**直接提交，不用 Git LFS**：客户 clone 时多半不装 git-lfs，拿到的是一行指针文本而不是文件
- 单个文件不超过 20 MB，超过先压缩
- 整个仓库超过 1 GB 时再考虑迁到 LFS 或对象存储
- 运行产物（checkpoint、日志、metrics）**不进仓库**，放对象存储，仓库里只写路径

## 10.5 复刻清单

- [ ] 每个 issue 仓建 `library/`、`recipes/`、`repro/` 三个目录，各放一个 README（模板见附录 B）
- [ ] `repro/README.md` 写清两种材料的区别、`card.yaml` 字段表、目录清单
- [ ] 定产物桶的布局：`gs://<桶>/issues/<号>/<运行名>/`，另一个仓库加前缀
- [ ] 如果有共用的启动脚本，写进 `repro/common/`，并让它拒绝覆盖已有产物
- [ ] `CODEOWNERS` 里给客户共同维护的目录加客户团队
