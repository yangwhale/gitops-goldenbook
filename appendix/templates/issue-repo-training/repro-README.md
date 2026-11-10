# repro

NorthPeak 里和 issue 对应的复现：探针、启动模板、分析脚本，以及一张记录「用什么、怎么跑、预期看到什么」的 `card.yaml`。
任何一方照着目录里的 README 都应该能复现 issue 里引用的数字。

## 和其他仓库的分工

| 位置 | 放什么 |
|---|---|
| `project-management` 的 issue | 问题、结论、截图 |
| **`project-management` 的 `repro/`（本目录）** | 本仓库 issue 对应的复现 |
| `project-management` 的 `recipes/` | 对外交付、版本钉死的配方 |
| `project-management-infra` | GKE on TPU 与网络的 issue，以及它的 issue 的复现（`repro/`） |
| `maxtext` | 模型代码改动（私有副本） |

复现里沉淀出来、要长期执行的检查（例如某个数值验收），升级进 `recipes/` 或 `maxtext` 的 CI。


## 目录

```
common/
  launch.sh             在一个 v5p-8 池（2 主机）上起一次 MaxText 训练或一个探针；card.yaml 里的 command 都是它的一行调用
  wait.sh               等作业结束：两台主机都打出 REPRO_EXIT rc=0 ⇒ DONE，任一失败 / pod 消失 ⇒ FAIL，查不到这个名字的作业 ⇒ NOTFOUND，超时单独报
  compare_metrics.py    逐步比较两份 MaxText metrics（默认 learning/loss），报逐位相同的步数和第一处不同
  loss_diff.py          逐步 loss 差的分段统计、噪声上限与判定；issue 评论里的分段数字按它的口径算
  collect_env.sh        在 pod 里采集 jax / jaxlib / libtpu / maxtext 版本、TPU 拓扑、flag
  check_dir_list.py     检查本 README「目录清单」：表里的目录都存在，带 card.yaml 的目录都登记了、指向 project-management 且以 issue 号开头；infra- 开头的目录报警告（CI：dir-list-check）
issues/<issue号>-<简述>/         project-management 的 issue
  README.md             问题、结论链接（指向 issue 评论）、怎么复现、预期输出
  card.yaml             运行清单：镜像 digest、代码包与探针（路径 + sha256）、每次运行的命令、产物路径、预期输出
  *.py / *.sh           探针、这个 issue 专用的启动或分析脚本
```

`project-management-infra` 的 issue 的复现放 [`project-management-infra` 仓库的 `repro/`](https://github.com/northpeak/project-management-infra/tree/main/repro)，不放这里（两个 issue 仓库的编号各自从 1 开始，放在一起会撞号）。那边的复现要用本仓库的 `launch.sh` 时，运行名写 `infra-<issue号>/<运行名>`，产物在 `$BUCKET/issues/infra-<issue号>/<运行名>/`。`dir-list-check` 会拦下 `card.yaml` 指向 `project-management-infra` 的目录和以 `infra-` 开头的目录。

复现一条运行的通用步骤（在本仓库的 `repro/` 目录下执行）：

```bash
cd repro
export KUBECONFIG=<POC 集群的 kubeconfig>  POOL=<空闲的 2x2x2 池>
<card.yaml 里那条 command，运行名换成自己的>     # 不换会被拒绝：launch.sh 不覆盖已有产物
bash common/wait.sh <提交时打印的 JobSet 名>
python3 common/compare_metrics.py <我们那份 metrics_host0.txt> <你的 metrics_host0.txt>
```

## 客户放的材料

客户在 issue 里放不下的东西（测试脚本、复现代码、日志文件等）也放在 `issues/<issue号>-<简述>/`，在 issue 里引用即可。`project-management-infra` 的 issue 的材料和复现放 [`project-management-infra` 仓库的 `repro/`](https://github.com/northpeak/project-management-infra/tree/main/repro)，不放这里。这类目录不受本 README 其余规矩约束：不要求 README 或 `card.yaml`，不用登记进「目录清单」，可以直接推、不提 PR。我们后续要把它做成验证过的复现时，再补 `card.yaml` 并登记。

## card.yaml 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `issue` | 是 | `northpeak/project-management#N` |
| `question` | 是 | 这个目录回答的一个问题 |
| `status` / `last_verified` | 是 | `verified`（至少一条运行按本仓库命令端到端重跑、结果与原始运行一致）/ `partial` / `failed`，以及最后一次验证的日期 |
| `scope` | 是 | 结论的适用范围（模型、硬件、规模、运行次数） |
| `env.image` | 是 | 必须是 `@sha256:<digest>` |
| `env.code` | 是 | `{repo, commit}`，或代码包 `{path, sha256}` |
| `env.probe` | 有探针时 | `{path, sha256}`；本目录里的副本写 `repo_copy` 并说明差异 |
| `env.jax` / `env.libtpu` | 是 | 版本号 |
| `env.flags` | 是 | `XLA_FLAGS`、`LIBTPU_INIT_ARGS` 等 |
| `cluster` | 是 | 拓扑、主机数、每主机芯片数、池、启动脚本 |
| `B` | 否 | 命令里 `$B` 的值（产物根目录） |
| `runs[]` | 是 | 每次运行：`name`（也是产物目录 `$B/<name>/`）、`command`、`output`、`expected`；按本仓库命令重跑核对过的加 `verified`（日期与结果） |
| `analysis[]` | 有统计时 | 重算 issue 评论里统计数字的命令、预期值、`verified` |

## 规矩

- 一个 issue 一个目录 `issues/<issue号>-<英文短横线简述>/`，验证过的复现必须有 `README.md` 和 `card.yaml`；issue 号指本仓库（`northpeak/project-management`）
- 新增或删除带 `card.yaml` 的目录时，同步本 README 的「目录清单」表（CI `dir-list-check` 会查）
- `card.yaml` 里镜像一律写 `@sha256:<digest>`；代码写 commit 或代码包路径 + sha256；产物写到 `gs://<POC 桶>/issues/<issue号>/<运行名>/`
- 不放客户模型的权重、数据、未授权公开的代码，只引用它们在客户 POC 项目里的路径和 sha256；不放任何一方公司内部的链接、主机名、工具包装
- issue 关闭后目录冻结，只改 README 顶部的结论；能复用的脚本提到 `common/`

## 引用规则

issue 里引用这里的数字时给三样：commit permalink（`https://github.com/northpeak/project-management/blob/<commit>/repro/issues/...`，不用分支链接）、运行名、产物路径。permalink 不会过期，分支链接和报告链接会。

## 提 PR

和 NorthPeak 其他代码仓库一样：关联 issue（`Closes` 或 `Refs northpeak/<issue 所在仓库>#N`）、按模板填四栏、`pr-check` 通过。目录负责人（对应 issue 的 assignee）批准即可合并。

## 目录清单

| 目录 | issue | 运行 | 状态 |
|---|---|---|---|
| [`issues/31-cp-loss-offset/`](issues/31-cp-loss-offset/) | project-management#31 | 4 | verified（重跑 1 条：2000 步逐位相同） |
