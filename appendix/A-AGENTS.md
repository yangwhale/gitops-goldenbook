# 附录 A `AGENTS.md` 完整模板

模板文件：[`templates/AGENTS.md`](templates/AGENTS.md)。它以原项目实际在用的版本为底，做了去标识处理（org 名换成 `northpeak`，客户模型和分支名换成 `modelx`，个人账号换成占位符），
又按评审意见补了几处原版没写清的地方（见文末「相对原项目版本的改动」）。**拷过去、按下表替换，就能用。**

为什么给一份完整的、带具体领域内容的模板，而不是一份抽象的骨架：骨架里的「<在这里写你的标签>」会被原样留下，
或者被填得很潦草。照着一份写完整的改，你会看到每一处具体写到什么程度。

## 替换表

| 搜索 | 换成 | 出现位置 |
|---|---|---|
| `northpeak` / `NorthPeak` | 你的 org 名（大小写两种都换） | 全文（仓库全名、命令、看板脚本地址） |
| `modelx` / `ModelX` | 你的代码仓开发分支名 / 模型名 | 第 1、3、4 节 |
| `<上游对接人账号>` | 固定路由的 assignee；没有固定路由就删掉这一段 | 第 2 节 |
| `Google 同事`、单独出现的 `Google` | 你的厂商的叫法（如果厂商不是 Google） | 第 1、3、6 节 |
| `docs/onboarding/working-in-northpeak.md`、`project-management.md`、`permissions.md` | 你的三份入职文档的文件名 | 开头、第 1 节 |
| `maxtext`、`gke-component-a`–`d`、`tpu-device-plugin` | 你的代码仓名 | 第 1、3 节 |
| `上游 MaxText 团队` | 固定路由对应的团队 | 第 2 节 |
| `northpeak/numerics-kit` 的精度清单 | 你的精度速查放在哪；不涉及数值的项目删掉这一条 | 第 5 节 |
| `training` / `gke` / `network` / `partners` 和「训练组 / GKE 组 / 网络组」 | 你的客户子团队 | 第 1 节 |
| 「POC 阶段」 | 你的项目阶段叫法 | 第 3 节 |
| 「org 已停用 GitHub Actions」 | 按你在第 15 章第 1 步的决定改；开了 Actions 就改成「CI 会检查……」 | 第 4 节 |
| `assets/issues/<阶段>/` | 定一个阶段命名（如 `poc`、`phase2`），写进来 | 第 1 节 |
| 「jax / libtpu 版本、芯片和拓扑」「GPU 对 TPU」 | 换成你的领域的运行条件 | 第 1、5 节 |

## 要按你的项目重写的部分

| 节 | 内容 | 怎么改 |
|---|---|---|
| 开头第三、四段 | org 管哪三类问题；两个 issue 仓的划界 | 换成你的领域。只有一个 issue 仓的话，删掉所有关于第二个仓库的段落（转移规则、跨仓库引用、可见性） |
| 第 1 节「放在哪个仓库」表 | 两个仓库各管什么 | 照第 2 章 2.3 你定下的划界表 |
| 第 1 节标签表 | `area/*` 两组 | 换成你的领域标签 |
| 第 1 节模板表、下拉枚举 | 13 个模板的字段和选项 | 和你实际放进 `.github/ISSUE_TEMPLATE/` 的文件逐字一致。**改了模板一定回来改这里** |
| 第 3 节「客户的代码和材料放哪」 | 开发分支、repro 路径 | 换成你的代码仓和分支 |
| 第 5 节最后一条 | 精度边界清单的路径 | 不涉及数值的项目删掉 |
| `sync-agents.sh` 目标 | 不在本文件里 | 见第 13 章 13.6 |

## 换领域：要改的地方一张表

原项目是 TPU 训练与推理 + GKE + 网络。你的项目领域不同时，下面这些地方都写着领域内容，逐个改（按渲染目录里的文件逐个列出的完整版在 [`AGENT-BOOTSTRAP.md`](../AGENT-BOOTSTRAP.md) 第 3 步）：

| 位置 | 改什么 |
|---|---|
| `AGENTS.md` 开头、第 1 节 | org 管什么；两个 issue 仓的划界表；`area/*` 两组；模板表；下拉枚举；运行条件举例 |
| `AGENTS.md` 第 2、3、5 节 | 固定路由；代码仓名和开发分支；精度清单 |
| issue 模板（13 个 `.yml`） | 「跟哪块有关」等下拉选项；运行条件各栏的 description 和 placeholder；训练仓独有的「精度对不齐」要不要留 |
| `config.yml` | 两个仓库互指链接的 `name` 和 `about` |
| `setup-labels.sh` | `area/*`、`type/perf` 的描述 |
| 两个 issue 仓的 `README.md` | 「这里提什么」 |
| org 主页 | 两组按钮上的划界、模板表、「正在做」、仓库表 |
| `wiki/README.md`、入职文档 | 「这个 org 管什么」、仓库表、例子 |
| 看板视图 | 视图名 |

改完后对照：`AGENTS.md` 里的模板表和下拉枚举，必须和 `.github/ISSUE_TEMPLATE/` 里的文件逐字一致。

## 不要改的部分

下面这些和领域无关，原样保留：

- 第 0 节（开工前三步）
- 第 2 节的状态表、分诊清单和「不要动」的规矩（固定路由那一段按你的项目改）
- 第 4 节的 PR 四件事、REST 改正文、评审规矩、禁止项（Actions 那一句按你的决定改）
- 第 6 节的评论规矩，尤其是「不写分派和流程」那一条的逐项列举
- 第 7 节 RFC 流程
- 第 8 节「绝对不要」
- 第 9 节完成的定义
- 第 10 节不署名

## 检查

替换完后：

```bash
# 不应再有示例 org 名和占位符
grep -ni 'northpeak\|modelx\|<上游对接人账号>\|numerics-kit\|gke-component' AGENTS.md
# 标签表里的每个标签都真的存在
for l in $(grep -o '`type/[a-z]*`\|`area/[a-z-]*`\|`size/[SL]`' AGENTS.md | tr -d '`' | sort -u); do
  gh label list -R <org>/project-management --search "$l" --json name --jq '.[].name' | grep -qx "$l" || echo "缺标签 $l"
done
```

> 第二条检查会把 infra 仓独有的 `area/gke`、`area/network` 报成缺失，对 infra 仓再跑一次即可。

## 相对原项目版本的改动

评审时让一个 AI 助手只读这份文件、推演 8 个日常任务，找出了原版几处会让 AI 卡住或误读的地方。模板里已改：

| 原版 | 模板 |
|---|---|
| 「和人类口头指示冲突时以人类为准」，没有例外 | 第 8 节「绝对不要」除外：改为在 wiki 开 issue 提议 |
| `access` 标签的位置说法有歧义 | 写明只在 `wiki` |
| 「刚建、不知道是哪块的先不打 area」与「建 issue 时不打 area」两种说法 | 统一为建 issue 时一律不打 |
| 示例命令写死 `size/S` | 大小不知道就不带 |
| 没有分诊步骤 | 第 2 节加分诊清单；调查类 issue 停在 Triage 是正常的 |
| 固定路由的 assignee 是替换还是追加不清楚 | 写明追加 |
| 分支名的 type 没枚举；两个仓库撞号 | 列出 type；infra 的 issue 号加 `infra-` |
| 「推之前自查」没给命令；「该跑的测试」没定义 | 给出 `pr-check.py` 的命令；测试指冒烟加相关单测 |
| 合进非默认分支后手动关 issue，和「不关别人的 issue」冲突 | 写明由 PR 作者关，不受那条限制 |
| Actions 已停用，却还写「CI 失败时」 | 改为「验证失败时」 |
| RFC 放哪个仓库、状态枚举、能否自己合并都没写 | 一律放 wiki；列出状态；请人评审后合并 |
| 例会记录 issue 号没写；混合会议放哪没写 | 两个仓库的 1 号 issue；混合会议放 infra 仓 |
| 「不写客户数据」与「贴客户原话」冲突 | 收窄为「客户的训练数据和模型权重」 |
| infra 仓的 repro 少一层 `issues/` | 两个仓库统一为 `repro/issues/<号>-<简述>/` |
| 入职文档路径没写仓库名 | 写明在 `wiki` 仓库 |
