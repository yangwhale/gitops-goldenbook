# 第 3 章 人员、团队与权限

默认谁都看不到，按团队授权；一人只进一个团队；AI 助手不开账号。

## 3.1 四层权限，从粗到细

GitHub org 的权限有四层：

| 层 | 说明 | 我们的设置 |
|---|---|---|
| 身份 | Owner（全权）/ Member（正式成员）/ Outside collaborator（只能碰明确给他的仓库） | Owner 只给负责加人的几个人；其余都是 Member；不用 Outside collaborator |
| 默认权限 | 成员对所有仓库的基础权限 | **None**：进来什么都看不到，靠团队授权 |
| 团队 | 按团队给仓库授权：Read / Triage / Write / Maintain / Admin | 日常主力 |
| 单仓直授 | 直接给某个人某个仓库的权限 | **不用** |

**为什么默认权限是 None**：默认 Read 意味着每个新成员一进来就能看到所有仓库，包括以后新建的。
新建一个只给厂商看的仓库时，你必须记得去收权限——总有一次会忘。默认 None 时，新仓库谁也看不到，按表授权才看得到，忘了的后果只是「有人看不到」，不是「有人看到了不该看的」。

**为什么不用单仓直授**：直授散落在各个仓库的设置页里，没有一个地方能看全「某人能看什么」。
全部走团队，「某人能看什么」= 「他在哪个团队」+ 「那个团队的授权表」，一眼看清。

**为什么不用 Outside collaborator**：外部协作者不进团队，只能单仓直授，回到上一条的问题。客户工程师一律邀请成 Member 再进团队。

## 3.2 Owner：只给负责加人的人

免费档里，**只有 Owner 能往 org 里邀请新成员**。所以 Owner 给 account team 里负责加人的几个人，不多给。

原项目最后有 5 个 Owner。原规矩是「Owner 限 2 人以内」，后来发现 `maintainers` 团队的人在 org 层面只是普通成员，加不了人；客户陆续来人时，2 个 Owner 不在线就卡住。
于是把 account team 里经常对接客户的人升成 Owner。**Owner 数量按「加人请求能不能当天处理」来定**，不是越少越好。

Owner 的权力很大（删仓库、改可见性、管所有权限），所以：

- Owner 只能是厂商的人
- Owner 同时是 `maintainers` 团队成员（团队授权表里体现 Admin）
- Owner 做的设置改动（建仓库、改权限、改看板字段）在 `wiki` 开 issue 留痕

## 3.3 团队

原项目的团队结构：

```
maintainers            管理员：account team 的厂商员工
googlers               支持客户的厂商员工，项目主力
customer               客户工程师（父团队，承载继承的权限）
├── training           客户训练组
├── gke                客户 GKE 组
└── network            客户网络组
partners               第三方工程团队
observers              客户管理层、PM 等，只读
```

授权表：

| 团队 | `wiki` | `project-management` | `project-management-infra` | 联合开发的代码仓 | 厂商专属仓 |
|---|---|---|---|---|---|
| `maintainers` | Admin | Admin | Admin | Admin | Admin |
| `googlers`（厂商工程师） | Maintain | Maintain | Maintain | Maintain | Maintain |
| `customer`（父团队） | Write | **无** | **无** | Write | 无 |
| └ `training` | 继承 | **Write** | **Write** | 继承 | 无 |
| └ `gke`、`network` | 继承 | 无（看不到） | **Write** | 继承 | 无 |
| `partners` | Write | Triage | 暂不授权 | 只给负责的仓库 Write | 无 |
| `observers` | Read | Read | Read | Read | 无 |

几个要点：

**客户的人进子团队，不直接进 `customer`。** 子团队自动继承父团队的仓库权限。
父团队 `customer` 承载「所有客户都该有的」权限（`wiki`、联合开发的代码仓），子团队只额外授权两个 issue 仓。

**两个 issue 仓是例外：父团队不授权，由子团队各自授权。** 这就是可见性边界：训练组两个仓库都能看，GKE 组和网络组只能看 infra 仓。
**其他仓库不要单独给子团队授权**，否则继承关系就乱了。

**为什么可见性是不对称的**（训练组能看 infra，GKE 组不能看训练）：训练组跑作业时会碰到集群层面的问题（切片起不来、节点坏了），需要在 infra 提 issue、看结论；
而 GKE 组、网络组不需要知道模型、精度这些事。原项目先做了对称隔离（各看各的），同一天就改成了不对称。第 16 章细讲。

**子团队名不带父团队前缀。** 叫 `training`、`gke`、`network`，不叫 `customer-training`。
GitHub 上子团队的显示本来就带层级（`customer / training`），再加前缀是重复。

**Write 而不是 Triage**：客户在两个 issue 仓上是 Write，因为 `recipes/`、`repro/` 由客户共同维护，客户要能推分支、提 PR、合并 PR。
只提 issue 的话 Triage 就够了。原项目早期是 Triage，交付物目录并进 issue 仓后改为 Write（RFC-0002）。

**客户在 `wiki` 上是 Write**：客户要能提 RFC、评审 RFC（`CODEOWNERS` 把 RFC 目录给了客户）。代价是免费档没有分支保护，客户可以直接推 `wiki` 的 `main`，包括改 `AGENTS.md`。原项目接受这个风险（改动都在提交历史里，看得见、能回退）。不放心的话，客户在 `wiki` 上给 Triage，RFC 由客户写好、厂商代为提 PR。

**`partners` 的授权跟着负责的仓库走**，没有成员时新仓库不给它授权，有了再在加人 issue 里定。

**厂商专属仓库：能不建就不建。** 只放不能给客户看的东西。org 里的一切迟早有人会误授权。

## 3.4 一个人只进一个团队

**规则：一个人只进一个团队。**

- 管理员只进 `maintainers`，不同时进 `googlers`（Admin 已经包含 Maintain，再进没意义，只会让成员列表重复）
- 客户里同时做训练和 GKE / 网络的人，**只进 `training`**：`training` 两个 issue 仓都能看，已经覆盖了

**为什么**：一人多团队时，「某人能看什么」要把几个团队的授权叠起来算，审计时容易漏。
一人一团队，查一个人的权限只要看他在哪个团队。

## 3.5 成员身份默认隐藏

org 是公开的，名字谁都能搜到。org 成员列表默认对外隐藏，**不要把自己的成员身份设成公开**——
公开后，你的 GitHub 主页会显示「属于 `<org>`」，任何人都能顺藤摸瓜知道你在和谁合作。

## 3.6 所有成员都能建仓库，但只许建私有仓库

免费档没法在设置里只禁止建公开仓库（只能全部禁止或全部允许）。原项目选择允许成员建仓库，这一条靠规矩：

- **建仓库一律选 Private**
- 误建了公开仓库，立刻告诉 maintainers 改成私有
- 删除、转移仓库、改公开私有只有 Owner 能做

AI 助手的规则里把「建公开仓库」列进了「绝对不要」（`AGENTS.md` 第 8 节）。

## 3.7 Maintain 和 Admin 的区别

| | Maintain | Admin |
|---|---|---|
| 推代码、管 issue、管标签 | ✓ | ✓ |
| 改大部分仓库设置 | ✓ | ✓ |
| 删仓库、改可见性 | ✗ | ✓ |
| 管仓库权限 | ✗ | ✓ |

厂商工程师给 Maintain：能做所有日常工作（包括转移 issue、改标签、合并 PR），但不能误删仓库或误改权限。

## 3.8 AI 编码助手不开账号

**AI 助手用运行它的那个人的账号，不单独开账号、不进任何团队。**

- 权限上，AI 助手能做的就是那个人能做的
- 那个人对 AI 用他账号做的一切负责
- GitHub 记下的作者就是那个人，不另外署名区分人和 AI（第 1 章原则 5）

**为什么不给 AI 单独开账号**：单独账号要进团队、要授权，等于多了一个「谁都能用」的身份，
出了问题找不到具体的负责人。而且 AI 账号的权限要么太大（所有人共用一个高权限账号），要么太小（每个人用时都要临时加权限）。

## 3.9 加人和撤人

**主流程**（原项目实际这么做）：

1. 加人请求大多来自聊天群（「请帮我加一下权限，我的 GitHub 是 xxx」）。Owner 收到后**直接按团队加**，不要求请求人先开 issue
2. 要确认的只有一件事：**这个人属于哪个团队**。客户的人问清是训练组、GKE 组还是网络组；厂商的人进 `googlers`
3. 拿不准对方是不是厂商员工，看邮箱域名或问介绍人；拿不准 GitHub 账号对不对，先查账号存在（`gh api users/<账号>`）
4. 更新厂商内部的账号对照表（3.10）

团队成员列表本身就是「谁有什么权限」的记录；GitHub 的 org 审计日志（Settings → Audit log）记下了谁在什么时候加的。

**什么时候开 issue**：权限要例外处理（不在授权表里的组合）、批量调整、或者撤人有争议时，在 `wiki` 用「加人 / 撤人」模板开 issue 留档，Owner 做完在 issue 里回写、关闭。
`wiki` 的守则原文要求每次都走 issue；实际运行中客户一天来好几个人，Owner 都是直接加的。复刻时二选一写进你的 `permissions.md`，不要两种说法并存。

「加人 / 撤人」模板（`wiki/.github/ISSUE_TEMPLATE/access.yml`）：

```yaml
name: 加人 / 撤人
description: 权限变更，留档用
title: "[权限] <加入|移出> @账号"
labels: ["access"]
body:
  - type: input
    id: who
    attributes: {label: GitHub 账号}
    validations: {required: true}
  - type: dropdown
    id: action
    attributes: {label: 操作, options: [加入, 移出, 调整]}
    validations: {required: true}
  - type: dropdown
    id: team
    attributes:
      label: 团队（一人只进一个；客户同时做训练和 GKE / 网络的选 training）
      options: [googlers（厂商员工）, training（客户训练组）, gke（客户 GKE 组）, network（客户网络组）, partners（合作方）, observers（旁观者，只读）, maintainers（管理员）]
    validations: {required: true}
  - type: textarea
    id: why
    attributes: {label: 原因}
```

用命令加人（邀请成 Member 并直接进团队）：

```bash
# 查账号的数字 ID
uid=$(gh api users/<账号> --jq .id)
# 邀请进 org，同时指定团队（team_ids 是团队的数字 ID，用 gh api orgs/<org>/teams/<slug> --jq .id 查）
gh api -X POST orgs/<org>/invitations -F invitee_id=$uid -F 'team_ids[]=<团队数字ID>' -f role=direct_member
# 只有邮箱、没有 GitHub 账号时，用邮箱邀请
gh api -X POST orgs/<org>/invitations -f email=<邮箱> -F 'team_ids[]=<团队数字ID>' -f role=direct_member
```

邀请 7 天内有效，过期要重发。查待接受的邀请：`gh api orgs/<org>/invitations --jq '.[].login'`。

升 Owner：

```bash
gh api -X PUT orgs/<org>/memberships/<账号> -f role=admin
```

> 这些操作需要 `gh` 令牌带 `admin:org` 权限。默认登录的令牌通常没有，用 `gh auth refresh -s admin:org` 加。

## 3.10 维护一份账号对照表

GitHub 账号名往往和真名对不上（`blue-harbor-77` 是谁？）。厂商一侧要维护一份「GitHub 账号 → 真名 → 公司 → 团队 → 角色」的对照表，
**放在厂商内部，不放进 org**——它包含客户员工的真名和角色，属于客户数据。

用途：

- 有人在 issue 里 @ 了一个账号，你要知道那是谁
- 季度对账时核对团队成员是否都还在项目上
- 有人离开项目时，知道要撤哪个账号

## 3.11 和验证相关的权限

需要用到计算资源、存储密钥的验证（比如 PR 里评论 `/loss` 触发一次训练）只对有仓库访问权的人生效；
**从外部 fork 提来的 PR 一律不触发**，防止外部代码拿到密钥。
所以需要跑验证的人，要加进 org 并在本仓推分支。

## 3.12 档位

免费档私有仓没有分支保护，评审不强制（第 1 章原则 10、第 7 章 7.7）。

升级到 Team 档的时机：**人多起来、出现过一次「没人看就合进去、后来出了问题」的事故**。在那之前，强制评审只会拖慢起步阶段。

## 3.13 复刻清单

- [ ] org 默认权限设 None：`gh api -X PATCH orgs/<org> -f default_repository_permission=none`
- [ ] 禁止 fork 私有仓：`gh api -X PATCH orgs/<org> -F members_can_fork_private_repositories=false`
- [ ] 建团队，子团队用 `parent_team_id` 挂到 `customer` 下
- [ ] 按授权表给每个仓库授权
- [ ] 写 `wiki/docs/onboarding/permissions.md`（模板见附录 B）
- [ ] 建账号对照表（厂商内部）
- [ ] 定 Owner 名单

具体命令见第 15 章。
