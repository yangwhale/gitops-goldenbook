# 第 7 章 分支、提交与 PR

issue 记录「问题和结论」，PR 记录「改了什么、为什么、和计划有什么不同」。下面的规则大多是为了让两者连得上。

## 7.1 分支

**分支名：`<type>/<issue号>-<英文短横线简述>`**，如 `feat/42-modelx-vl-encoder`、`fix/31-cp-loss-mask`。

- `type` 和 issue 的 type 标签对应：`feat`、`fix`（对应 `type/bug`）、`perf`、`docs`、`chore`
- issue 号是 issue 所在仓库的号。因为两个 issue 仓编号重复，建议 infra 仓的 issue 在分支名里加前缀：`fix/infra-14-node-repair`（原项目没有规定，本书附录的 `AGENTS.md` 模板加上了）

**分支推在本仓库，不要从个人 fork 提 PR。** 原因有二：org 禁止 fork 私有仓库；外部 fork 的 PR 触发不了需要密钥的验证（第 3 章）。

上游私有副本（第 9 章）的分支规矩以仓库根目录的 `FORK.md` 为准，比如 `maxtext` 的日常开发从 `modelx` 分支拉、合回 `modelx`，而不是 `main`。

### 客户的开发分支：不做规定

POC 阶段，客户本人或替客户工作的助手改代码时：

- **在代码仓里从开发主线（如 `maxtext` 的 `modelx`）拉一个自己的分支，改完推上去即可**
- **分支名不做规定，不要求提 PR**

为什么对客户这么宽松：客户的分支多是试验，提 PR 的门槛会让他们改在本地、不推上来，结果厂商这边看不到。
推上来了，厂商就能直接看代码、复现问题。要合进主线时，再由厂商按规矩开分支、提 PR。

**我们自己修 issue 时，仍按上面的分支命名开分支、按本章提 PR。**

## 7.2 提交

- 第一行：`<type>: <简述>`，如 `fix: cp 重排后同步重排 loss mask`
- 正文写**为什么**改（改了什么 diff 已经说明了）
- **不要把正文内联在命令行里，用 `git commit -F <文件>`**。命令行里的多行字符串容易被 shell 转义弄坏（反引号、`$`、感叹号），而且会留在 shell 历史里
- 不 force push 到 `main`，不改写已推送的公共历史
- 提交信息里引用 issue 写全名：`Refs northpeak/project-management#31`（裸的 `#31` 会按当前仓库解析）
- **不署名 AI**：不加 `Co-Authored-By: <AI>`、`Assisted-by` 之类的行（第 1 章原则 5）

## 7.3 哪些改动不走 PR

**例外：两个 issue 仓的「记录类改动」不走 PR，直接推 `main`：**

- 改 issue 模板
- 加截图（`assets/`）
- `AGENTS.md`（由 `sync-agents.sh` 直接同步）
- 客户放进 `repro/` 的材料

提交信息写清改了什么，并带上 `Refs #<issue号>`。

**其他改动照常走 PR**：issue 仓的四个交付物目录（`library/`、`meetings/`、`recipes/`、`repro/` 中我们写的部分）、根 README、PR 模板。

**为什么记录类改动不走 PR**：它们不是「交付物」，而是 issue 的附件和基础设施。改一个模板的下拉选项开一个 PR、等人批准，
流程比改动本身重得多。卡住它们没有收益。

## 7.4 PR 必须做的四件事

### 1. 关联 issue

**正文含 `Closes <org>/<issue 所在仓库>#<号>`**，如 `Closes northpeak/project-management-infra#12`。
只是相关、不该关闭时写 `Refs`。规矩类改动在 `wiki` 提 PR 时写 `Closes #<号>`（同仓库可以用短形式）。

**禁止在没有关联 issue 的情况下开 PR。**

**PR 合进的不是默认分支时**（如 `maxtext` 的 PR 合进 `modelx`），GitHub **不会**按 `Closes` 关 issue，看板也不会跳到 Done。
合并后手动关：

```bash
gh issue close <issue URL> --comment "由 northpeak/maxtext#58 完成"
```

不手动关的后果：PR 都合进了开发分支，issue 却全都还开着，看板停在 In Progress，和实际进度对不上。

### 2. 按模板填四栏

```markdown
## 做了什么

<!-- 一两句话 -->

## 关联

Closes northpeak/project-management#

<!-- 大任务另附 RFC：docs/rfc/NNNN-... -->

## 怎么验证的

<!-- 涉及数值的改动附 run-ID -->

## 和原计划的偏差（必填，没有写「无」）

```

不同仓库的 PR 模板，关联行写法不一样：`wiki` 的写 `Closes #`（issue 在同一个仓库）；代码仓的写死 `Closes <org>/project-management#`（issue 在别的仓库）；issue 仓的写 `Refs <org>/<本仓库>#`，并在注释里提醒纪要 PR 保持 `Refs`。

**「和原计划的偏差」一栏：实现和 issue 或 RFC 写的不一样时，写「原计划 A → 实际 B → 原因」；完全一致写「无」。不许删这一栏。**

偏差较大时，**同时回到 issue 或 RFC 里更新原文**，让记录和代码一致。

**为什么这一栏是整套规则里最重要的一栏**：计划改了没回头记，三个月后 issue 上写的就是一个从没发生过的方案。
有人照着 issue 去理解代码，会发现对不上，然后浪费一下午。偏差栏强迫写代码的人在合并前回头看一眼计划。

偏差栏的例子：

```markdown
## 和原计划的偏差

- 原计划在 attention 层里修 mask → 实际在数据管道的 load balancing 重排里同步重排 loss mask → 
  在 attention 层修需要改三个 kernel，数据侧修只改一处，且不影响非 cp 路径
- RFC-0005 写的验证规模是 v5p-256 → 实际只跑了 v5p-128 → v5p-256 排队两天没有拿到；
  已在 northpeak/project-management#31 设 Blocked 等客户验证
```

### 3. 指定一位人类负责人

**assignee 设为一位人类负责人**，通常就是你用的那个账号的主人。AI 用谁的账号，谁就是作者和负责人，不另外署名。

### 4. 合并前本地自查

原项目一开始用 GitHub Actions 跑一个 `pr-check`：检查正文有没有关联 issue、偏差栏在不在、是不是空的。
后来 Actions 被整个 org 停用（第 14 章讲原因），所以**推之前自己核对**：

- [ ] 正文有 `Closes` 或 `Refs` + 全仓库名 + `#号`
- [ ] 有「## 和原计划的偏差」，内容不是空的（注释不算）
- [ ] 该跑的测试在本地跑完了

附录 C 提供了一个本地版的检查脚本，可以在推之前跑：`pr-check.py < body.md`。

## 7.5 尽量和禁止

**尽量**：

- 一个 PR 只做一件事
- 核心目录改动超过 200 行就拆

**禁止**：

- 在没有关联 issue 的情况下开 PR
- 把多个不相关的改动塞进一个 PR
- 没在本地跑过测试就合并

## 7.6 改 PR 正文：用 REST

AI 助手改 PR 正文时，**不要用 `gh pr edit`**：它走 GraphQL，要求令牌有 `read:org` 权限，很多人的令牌没有，会报一个看不懂的 GraphQL 权限错误。
用 REST：

```bash
gh api -X PATCH repos/<org>/<repo>/pulls/<号> -F body=@/tmp/body.md
```

## 7.7 评审：现阶段不强制

**需要别人看时，请他评审并等他批准再合并：**

```bash
gh api -X POST repos/<org>/<repo>/pulls/<号>/requested_reviewers -f 'reviewers[]=<GitHub 账号>'
```

**不需要时，本地自查完就可以自己合并。账号主人说了要谁看，就必须请那个人。**

**为什么不强制**：起步阶段人少，强制评审意味着每个 PR 都要等另一个人有空，节奏会慢一倍。
而免费档的私有仓库也做不到强制（没有分支保护）。人多起来、升级 Team 档后，再改成「合并前至少 1 人批准」并由分支保护强制。

评审的规矩（`wiki/docs/best-practices/code-review.md`）：

- 先看 PR 关联的 issue 和 RFC，再看代码：判断它解决的是不是那个问题
- 看「和原计划的偏差」一栏：偏差有没有说明原因
- 涉及数值的改动，要求附验证运行的 run-ID
- 评审意见分两类：**必须改**（阻塞合并）和**建议**（不阻塞），写清是哪类
- **批准即表示你愿意为这次合并负责**

## 7.8 代码仓专属：数值影响栏

对于会影响模型数值的代码仓（原项目的 `maxtext`），PR 模板多一栏「数值影响」，动了 `src/` 或依赖的 PR 必填。
第一行写三种之一：

| 类型 | 意思 | 合并后回归门 |
|---|---|---|
| **数学不变** | 重构、加日志与监控、不进训练图的代码、预期逐位不变的性能改动 | 要求逐位相同 |
| **会改数值** | 再写三项：幅度（执行级：只改融合、调度、分块、重算位置 / 数学级：改精度、算法、公式、默认配置）、范围（回归清单里哪几行会变）、理由 | 按声明的范围判 |
| **升级依赖** | jax / jaxlib / libtpu、kernel 库、checkpoint 库、镜像、编译开关；再写新旧版本号、镜像 digest、变更日志里和数值有关的条目 | 按变更日志判 |

规则：**一个 PR 只做一种事**——会改数值的改动不要和性能改动捆在一起。会改数值、升级依赖的 PR 合并前在分支上跑过回归并把结果贴进来。

例：

```markdown
## 数值影响

会改数值
幅度：数学级
范围：R08、R09、R12、R13、R15
理由：路由权重先舍入成 BF16，对齐 GPU 的 BF16 路由权重
```

**为什么**：数值问题最难查的是「哪次改动引入的」。每个 PR 事先声明自己会不会改数值，日常回归一旦发现数值变了，
对照声明就知道是预期内（声明了会改，且在范围内）还是意外（声明了不变却变了）。复刻时如果你的项目不涉及数值，删掉这一栏。

完整的 PR 模板见附录 B。

## 7.9 一个完整 PR 的样子（虚构）

```markdown
标题：fix: cp 重排后同步重排 loss mask
分支：fix/31-cp-loss-mask → modelx
assignee：bob-g

## 做了什么

context parallelism 的 load balancing 会重排序列，loss mask 之前没跟着重排，
padding token 被算进了 loss。现在在同一处一起重排。

## 关联

Closes northpeak/project-management#31

## 怎么验证的

- CPU 冒烟（FORK.md 里的命令）：4 步完成，loss 8.450 → 8.220
- v5p-128，cp=4：2000 步 loss 2.4109，cp=1 为 2.4113，差 −0.0004（容差 ±0.002）。
  run-ID cp4-fix-r19，产物 gs://<POC 桶>/issues/31/cp4-fix-r19/
- 复现目录：northpeak/project-management/repro/issues/31-cp-loss-offset/

## 数值影响

会改数值
幅度：数学级
范围：所有 cp>1 的回归行（R11、R14）
理由：修正 loss 的计算范围

## 和原计划的偏差

原计划在 attention 层修 → 实际在数据侧修 → 只改一处、不影响非 cp 路径
```

合并后（`modelx` 不是默认分支）：`gh issue close https://github.com/northpeak/project-management/issues/31 --comment "由 northpeak/maxtext#58 完成"`。
——不过这个例子里客户还没验证，所以实际是设 Blocked、等客户验证后再关（第 6 章 6.14）。

## 7.10 复刻清单

- [ ] 每个可提 PR 的仓库放 `.github/pull_request_template.md`，关联行写死 issue 仓全名
- [ ] 涉及数值的代码仓加「数值影响」栏
- [ ] 写 `wiki/docs/best-practices/code-review.md`
- [ ] 把 7.1–7.7 写进 `AGENTS.md` 第 3、4 节
- [ ] 本地自查脚本放进 `wiki/scripts/`（附录 C）
