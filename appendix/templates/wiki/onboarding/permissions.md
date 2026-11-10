# 权限

## org 是公开的

GitHub 上 org 本身没有私有一说，名字谁都能搜到；所以 org 名、公开仓库、公开的成员资料里**不出现客户名和项目细节**。
仓库默认建成私有。成员身份默认对外隐藏，不要自己设成公开。

## 四层，从粗到细

| 层 | 说明 | 我们的设置 |
|---|---|---|
| 身份 | Owner（全权）/ Member（正式成员）/ Outside collaborator（只能碰明确给他的仓库） | Owner 只给 account team 里负责加人的人（现在是 <Owner 账号列表>）：只有 Owner 能往 org 里邀请新成员 |
| 默认权限 | 成员对所有仓库的基础权限 | **None**：进来什么都看不到，靠团队授权 |
| 团队 | 按团队给仓库授权：Read / Triage / Write / Maintain / Admin | 日常主力，见下表 |
| 单仓直授 | 直接给某个人某个仓库的权限 | 不用 |

## 五个团队

| 团队 | 谁 | wiki | project-management、project-management-infra | 联合开发仓库 | Google 专属仓库 |
|---|---|---|---|---|---|
| `@northpeak/maintainers` | 管理员：account team 的 Google 员工 | Admin | Admin | Admin | Admin |
| `@northpeak/googlers` | 支持客户的 Google 员工，项目主力 | Maintain | Maintain | Maintain | Maintain |
| `@northpeak/customer` | 客户工程师 | Write | 无（按子团队授权，见下一行） | Write | 无 |
| `@northpeak/customer` 的子团队 `training`、`gke`、`network` | 客户训练组、GKE 组、网络组 | 继承 customer | `training`：`project-management`、`project-management-infra` 都是 Write；`gke`、`network`：只有 `project-management-infra` Write，看不到 `project-management` | 继承 customer | 无 |
| `@northpeak/partners` | 第三方工程团队 | Write | `project-management` Triage；`project-management-infra` 暂不授权（团队还没有成员） | 只给负责的仓库 Write | 无 |
| `@northpeak/observers` | 客户管理层、PM 等 | Read | Read | Read | 无 |

- **一个人只进一个团队**（管理员除外，管理员同时也是 googlers 的成员没有意义，只进 maintainers）。客户里同时做训练和 GKE / 网络的人只进 `training`：`training` 两个 issue 仓库都能看
- 客户的人按组进子团队（训练组进 `training`，GKE 组进 `gke`，网络组进 `network`），不直接进 `customer`；子团队自动继承 `customer` 的仓库权限。两个 issue 仓库是例外：`customer` 不授权，由子团队各自授权（训练组两个都能看，GKE 组和网络组只看 `project-management-infra`），其他仓库不要单独给子团队授权
- 新仓库建好时，按上表给团队授权（表里写了例外的按例外）；不在表里的组合先在 `wiki` 开 issue 讨论
- **所有成员都能建仓库，但只许建私有仓库**；删除、转移仓库和改公开私有只有 owner 能做。免费档没法在设置里禁止建公开仓库，这一条靠规矩：误建了公开仓库，立刻告诉 maintainers 改成私有
- Maintain 和 Admin 的区别：Maintain 能推代码、管 issue 和标签、改大部分仓库设置；不能删仓库、改可见性、管权限
- 「Google 专属仓库」只放不能给客户看的东西。**能不放进这个 org 就不放**——org 里的一切迟早有人会误授权

## AI 编码助手

AI 助手（Codex、Claude Code、Antigravity 等）**用运行它的那个人的账号**，不单独开账号、不进任何团队。
GitHub 记下的作者就是那个人，不另外署名区分人和 AI（见 `AGENTS.md` 第 10 节）。
权限上，AI 助手能做的就是那个人能做的；那个人对 AI 用他账号做的一切负责。

## 加人的流程

1. 在 `wiki` 仓库开 issue「加人：@账号」（用「加人／撤人」模板），写明属于哪个团队、需要哪些仓库、什么级别
2. Owner 把人加进对应团队（只进一个），不单独授权
3. 在 issue 里回写已完成，关闭

离开项目同样走 issue，从团队移除。这样「谁在什么时候拿到了什么权限」有据可查。

## 和 CI 相关的权限

用到 TPU、存储密钥的评论命令（如 `/loss`）只对有仓库访问权的人生效；**从外部 fork 提来的 PR 一律不触发**，防止外部代码拿到密钥。
所以需要跑验证的人，要加进 org 并在本仓推分支。

## 档位

分支保护（「合并前至少 1 人批准」）在私有仓上需要 GitHub Team 档；免费档只对公开仓有效。现阶段评审本来就不强制（见 `AGENTS.md` 第 4 节）。
