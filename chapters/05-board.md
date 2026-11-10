# 第 5 章 看板

看板回答一个问题：**现在所有事情是什么状态？** 它是 issue 仓之上的一层视图，不存任何 issue 里没有的信息。

## 5.1 一块 org 看板，不建仓库看板

**规则：整个 org 只有一块看板（GitHub Projects，新版），两个 issue 仓的 issue 都进这一块。**

- 全局进度在一个地方看
- 字段、状态、自动规则只维护一套
- 按仓库看用**视图**（筛选），不用另建看板

看板的 README（Projects 设置里的 README 栏）写一句：「状态由规则自动改，别手动拖；规矩见 `<org>/wiki` 的 AGENTS.md。」

看板设为 **Private**（只有 org 成员能看）。

## 5.2 状态：6 个

```
Triage → Design Pending → Ready to Develop → In Progress ⇄ Blocked → Done
```

| 状态 | 意思 | 谁来改 |
|---|---|---|
| **Triage** | 刚进来，还没人看 | 规则自动（加入看板时） |
| **Design Pending** | 大任务，在写 RFC | **人**：认领了 `size/L` 任务、开始写 RFC 时 |
| **Ready to Develop** | RFC 已合并，可以开发 | **人**：RFC 的 PR 合并后 |
| **In Progress** | 在做 | 规则自动（PR 关联到 issue 时） |
| **Blocked** | 被外部卡住 | **人**：被外部依赖卡住时，**同时在 issue 里评论卡在哪、等谁** |
| **Done** | 完成 | 规则自动（issue 关闭或 PR 合并时） |

**人只改三个状态**：Design Pending、Ready to Develop、Blocked。唯一的例外是 P0：分诊时直接设 In Progress（见下）。其余全部由规则改。

几条规矩：

- 不要手动把状态拖到 Done。Done 只能由「issue 关闭」或「PR 合并」触发。手动拖到 Done 会触发 Auto-close 规则（5.4），把还没验证完的 issue 直接关掉
- 不要为了「看起来有进展」改状态。比如还没有 PR 就拖到 In Progress
- 认领 = 把负责的人设为 assignee，不另设「已认领」状态
- Blocked 必须配一条评论：卡在哪、等谁。只改状态不评论，一周后没人知道为什么卡着
- 修复给出但客户还没验证：不关 issue，设 Blocked，评论写「等客户在 X 环境验证」

**小任务（`size/S`）的路径**：Triage → In Progress（PR 关联时）→ Done（PR 合并时）。完全不用人改状态。
**大任务（`size/L`）的路径**：Triage → Design Pending → Ready to Develop → In Progress → Done。人改两次。
**Bug** 不分大小，直接进本月迭代；**P0** 直接设 In Progress。

## 5.3 字段：只建会被自动填、或每周真有人看的

**规则：只建会被规则自动改、或每周真有人看的字段。用不上的字段别建，建了就会产出假数据。**

原项目的看板除了自带的 Status，只加了两个字段 Size 和 Iteration（其余都是 GitHub 自带的，如 Assignees、Labels、Repository、Linked pull requests、Parent issue、Sub-issues progress）：

| 字段 | 类型 | 选项 | 谁填 |
|---|---|---|---|
| Status | 单选 | 见 5.2 | 规则 + 人（3 个状态） |
| Size | 单选 | `S`、`L` | 加入看板时用 `board.sh add <URL> S` 顺手设 |
| Iteration | 迭代 | 按自然月：每期标题写月份（`2026-11`、`2026-12`），起止日期对齐月初；GitHub 的 Iteration 只能按天或周设默认长度，大小月要逐期手动调 | 每月初圈定本月要做的 Task |

**为什么 Size 既有标签又有字段**：标签用于 issue 列表的筛选和搜索；看板字段用于看板的分组和排序。
两者重复是 GitHub 的限制（看板不能按标签分组）。`board.sh add` 一条命令同时设，减少不一致。

**不建的字段**（常见但原项目没建）：

| 字段 | 为什么不建 |
|---|---|
| 优先级（看板字段） | 已有 `P0`/`P1`/`P2` 标签；拿不准就不打 |
| 预估工时 / 剩余工时 | 没人会每天更新，一周后全是假数据 |
| 负责团队 | 已有 assignee 和 Repository |
| Start date / Target date | GitHub 自带但不用；排期按 Iteration 粗粒度圈 |

## 5.4 自动规则：全部打开

Projects 设置 → Workflows，以下内置规则全部 **On**：

| 规则 | 效果 |
|---|---|
| Item added to project | 设 Status = Triage |
| Item closed | 设 Status = Done |
| Item reopened | 设 Status 回到非 Done |
| Pull request linked to issue | 设 Status = In Progress |
| Pull request merged | 设 Status = Done |
| Auto-close issue | Status 被设为 Done 时关闭 issue |
| Auto-add sub-issues to project | 父 issue 在看板上时，挂上去的 sub-issue 自动加入看板 |

**状态靠人点一定会烂，靠规则改才准。**

### 普通 issue 不会自动进看板

GitHub 的「Auto-add to project」规则（按仓库和筛选条件自动收录新 issue）每条只能盯一个仓库，免费档每块看板**最多 1 条**（GitHub 文档 Adding items automatically：Free 1 条，Pro / Team 5 条，Enterprise 20 条）。
两个 issue 仓只能自动收录一个，规则就不统一了。原项目没有用它（文档里没写原因，这是本书的推测）：**新 issue 必须手动加进看板**。这一步交给脚本：

```bash
gh api repos/<org>/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- add <issue URL> S
```

这条命令不需要 clone `wiki`，在任何目录都能跑。AI 助手的规则里「建 issue 后加进看板」是必做步骤。

> 复刻时如果只有一个 issue 仓，或者升级到了 Team 档，可以打开 Auto-add：Projects → Workflows → Auto-add to project，选仓库、筛选 `is:issue`。
> 打开后 `board.sh add` 只用来设 Size，但规则里仍保留这一步（重复加不会出错）。

## 5.5 视图

| 视图 | 筛选 | 用途 |
|---|---|---|
| View 1 | 无 | 全局 |
| 训练与推理 | `repo:<org>/project-management -repo:<org>/project-management-infra` | 训练方向的分诊和周会 |
| 基础设施 | `repo:<org>/project-management-infra` | 基础设施方向 |

**注意第二个视图的筛选**：原项目在 `repo:<org>/project-management` 后面又加了 `-repo:<org>/project-management-infra`，把另一个仓库显式排除掉。GitHub 文档没写 `repo:` 是不是按前缀匹配，照抄这个写法最保险；建完视图看一眼条目数，确认没混进另一个仓库。

视图类型用表格（Table）。按 Status 分组的看板视图（Board layout）可以按需加，不加也行。

## 5.6 `board.sh`：一条命令加进看板、设字段

`board.sh` 是一个只依赖 `gh` 和 `jq` 的脚本，放在 `wiki/scripts/`：

```bash
board.sh add    <issue或PR的URL> [S|L]      # 加进看板（可顺带设大小）
board.sh size   <URL> S|L
board.sh status <URL> "Design Pending"|"Ready to Develop"|"Blocked"|...
```

它的原理：

1. 把 issue URL 换成 node id（`gh api repos/.../issues/N --jq .node_id`）
2. 用 GraphQL `addProjectV2ItemById` 加进看板（已在看板上的会返回已有条目的 id，所以可以重复调用）
3. 用 `updateProjectV2ItemFieldValue` 设单选字段

脚本里写死了看板的 project id、字段 id、选项 id。**复刻时这些 id 要重新查**：

```bash
# project id
gh api graphql -f query='{organization(login:"<org>"){projectV2(number:1){id}}}' --jq .data.organization.projectV2.id
# 字段和选项 id
gh project field-list 1 --owner <org> --format json \
  --jq '.fields[]|select(.options)|{name,id,options:[.options[]|{name,id}]}'
```

完整脚本见 [`appendix/scripts/board.sh`](../appendix/scripts/board.sh)。

### 谁能改看板

看板设 Private 后，org 成员默认看不到它。在 Projects → Settings → Manage access 里按团队给：

| 团队 | 看板权限 | 理由 |
|---|---|---|
| `maintainers`、`googlers` | Write | 分诊时要加条目、改状态 |
| 客户各组、`observers` | Read | 看进度 |

跑 `board.sh` 的人还要令牌带 `project` 权限（`gh auth refresh -s project`）。
客户的 AI 助手照 `AGENTS.md` 建完 issue 会去跑 `board.sh add`，没有写权限会失败——这没关系，`AGENTS.md` 里写明「没有看板权限就跳过，分诊的人会加」。

**为什么用脚本而不是让人去网页上点**：网页上加进看板、设两个字段是五六次点击，人会漏；AI 助手根本没法点网页。
一条命令就能做完，AI 助手每次都会做。

## 5.7 每月排期

- 每月初，看板的 Iteration 字段圈定本月要做的 Task。没圈进来的留在 backlog（Iteration 为空）
- Task 到了「一个模块」的工作量就必须拆成 SubTask（用 sub-issue 挂在 Task 下）
- Bug 不排期，直接进本月

任务分层：

```
Goal（方向，跨月）       ← 不建 issue，写在 RFC 或主页「正在做」里
 └─ Task（一件开发工作，一个 issue）
     └─ SubTask（最小可交付单元，自带测试，sub-issue 挂在 Task 下）
```

**不往下套第三层**。三层以上的层级没人维护。

## 5.8 两条路：小任务和大任务

| | 小任务（Size = S） | 大任务（Size = L） |
|---|---|---|
| 例子 | 改个配置、修个小 bug | 接一个新模型、改一条数据通路 |
| 设计文档 | 不需要 | 先写 RFC（第 8 章） |
| 拆子任务 | 不拆 | 按 RFC 拆 |
| 完成 | 自己的 PR 合并 | 所有子任务关闭 |

**不要把两种塞进同一条流程。流程太重，被绕过的一定是重的那条。**

## 5.9 复刻清单

- [ ] 建 org 看板（Projects → New project → Table），设 Private，写 README
- [ ] Status 字段改成 6 个选项（默认是 Todo / In Progress / Done，要改）
- [ ] 加 Size（单选 S / L）、Iteration（按月）
- [ ] Workflows 全部打开；Item added 设为 Triage
- [ ] 加两个视图，注意 `-repo:` 排除
- [ ] 查 id，改好 `board.sh`，放进 `wiki/scripts/`
- [ ] 用一个测试 issue 跑一遍 `add` / `status`，确认字段变了
