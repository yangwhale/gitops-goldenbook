# AGENT-BOOTSTRAP.md —— 给 AI 助手：照这本书为新客户建一个 org

你是一个 AI 编码助手。用户（厂商的工程师）让你「照 gitops-goldenbook 给新客户建一个 GitOps org」。这份文件是你的任务书，照着做，不要自行变通。

整个过程分 6 步。**只有第 0 步和第 5 步需要人动手**，其余你自己做。每一步做完给用户一句话汇报，不要等到最后。

```
第 0 步  人：在网页上建一个空 org（API 建不了）
第 1 步  你：向人问清决定，填 org-config.yaml
第 2 步  你：plan（只读预演），把计划给人看
第 3 步  你：render，然后改写和领域有关的内容
第 4 步  你：apply，再 verify
第 5 步  人：接受邀请、用客户账号点几个链接
```

---

## 前提

- 你能跑 shell，有 `gh`、`git`、`python3`。先 `pip install pyyaml`
- `gh` 登录的是**用户本人的账号**，这个账号必须是新 org 的 Owner。令牌权限：

  ```bash
  gh auth refresh -s admin:org,project,workflow
  gh auth status      # 确认有 repo、admin:org、project、workflow
  ```

  `gh auth refresh` 会给出一个设备码让人在浏览器里确认。**这一步要人做**：把设备码和网址原样转给用户，等他说好了再继续
- 本书仓库 clone 到本地：`gh repo clone yangwhale/gitops-goldenbook`，下文路径都相对于它

## 第 0 步 人：建 org

请用户在网页上建 org（<https://github.com/organizations/plan> → Free），名字不含客户名、不含未公开的产品代号（第 2 章 2.9）。建好后告诉你 org 名。

你可以确认：`gh api orgs/<org> --jq .login`。

## 第 1 步 你：问清决定，填配置

复制 `bootstrap/org-config.example.yaml` 为 `org-config.yaml`，按里面的注释逐项问用户。**一次把问题列全**，不要一个一个问。要问的：

| 问题 | 对应字段 | 用户不知道时的默认 |
|---|---|---|
| org 名、展示写法 | `org`、`org_title` | — |
| 客户有几拨工程师？训练和集群（GKE / 网络）分开吗？ | `issue_repos` | 只有一拨就 `one`；第 2 章 2.3 的三个问题都答「是」才 `two` |
| 谁是 Owner（只有 Owner 能加人）？ | `owners` | 用户本人 |
| 各团队成员的 GitHub 账号 | `members` | 先只填用户本人，其他人以后再加 |
| 要建哪些代码仓？各是自研还是上游副本？上游地址？ | `code_repos` | 没有就留空 |
| 客户模型叫什么、开发分支叫什么、阶段叫什么 | `model`、`dev_branch`、`phase` | 开发分支名不带代数（第 9 章 9.3） |
| 有没有固定路由（某类 issue 固定给某人） | `fixed_route` | 没有就删掉这段 |
| 开不开 GitHub Actions | `actions` | `disabled`（第 14 章 14.3） |

规矩：

- **账号必须是用户给的真实账号**。书里的 `alice-g`、`bob-g` 等示例名在 GitHub 上可能是真实的陌生人，脚本会拒绝它们
- 一人只进一个团队；客户同时做训练和 GKE 的进 `training`
- 填完把 `org-config.yaml` 整个贴给用户确认

## 第 2 步 你：plan

```bash
python3 bootstrap/bootstrap.py plan org-config.yaml
```

只读，不改任何东西。把输出里的「将建哪些团队、仓库、授权、邀请谁」整理成一张短表给用户看，**等用户确认再往下走**。

plan 报错时：

| 报错 | 处理 |
|---|---|
| 令牌缺权限 | 回到「前提」，让用户确认设备码 |
| org 不存在 | 回到第 0 步 |
| 不是 Owner | 请 org 的 Owner 把用户升为 Owner，或者换 Owner 来跑 |
| 示例账号或占位符 | 回到第 1 步，问真实账号 |

## 第 3 步 你：render，然后改写领域内容

```bash
python3 bootstrap/bootstrap.py render org-config.yaml     # 输出到 /tmp/<org>-render
```

render 只做机械替换（org 名、模型名、分支名、厂商名、阶段名、固定路由账号、同步目标）。**和领域有关的内容要你来改**，在渲染目录里改：

1. 先读 [`appendix/A-AGENTS.md`](appendix/A-AGENTS.md) 的「换领域：要改的地方一张表」
2. 新客户的领域**和原项目一样**（TPU 训练 + GKE + 网络）：只改下面第 5 条，其余不动
3. 领域不同：按那张表逐个改 `templates/AGENTS.md`、两套 issue 模板的下拉选项、`scripts/setup-labels.sh` 的 `area/*`、两个 issue 仓的 README、org 主页。**`AGENTS.md` 里的模板表和下拉枚举必须和 `.github/ISSUE_TEMPLATE/` 里的文件逐字一致**
4. `issue_repos: one` 时：按第 2 章 2.3「只有一个 issue 仓时」删掉 `templates/AGENTS.md` 里关于第二个仓库的段落（转移规则、跨仓库可见性、infra 的标签和模板表）
5. 每个项目都要改的：
   - `templates/org-profile/README.md`：org 名来历、「正在做」、仓库表
   - `templates/AGENTS.md` 第 3 节和 `templates/wiki/onboarding/working-in-<org>.md`：代码仓清单换成 `code_repos` 里的
   - 上游副本：渲染目录里有 `FORK-<仓库>.md`（样例原文），按第 9 章改写来源、跟上游的方式、分支表
   - `templates/wiki/onboarding/working-in-<org>.md` 的「例子」表：先清空，第一批 issue 有了再填（第 18 章 18.1）

改完自检：

```bash
W=/tmp/<org>-render
grep -rniI 'northpeak\|modelx\|<上游对接人账号>\|numerics-kit\|gke-component' $W/templates $W/scripts   # 应为空（或只剩你确认要保留的）
python3 -c 'import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob("'$W'/templates/**/*.yml",recursive=True)]' && echo YAML ok
```

把改了什么列给用户（一行一处）。

## 第 4 步 你：apply，再 verify

```bash
python3 bootstrap/bootstrap.py apply org-config.yaml
python3 bootstrap/verify.py org-config.yaml
```

- apply 可以**重复跑**：每一步先查再改，已经做好的会跳过。中途失败，修好原因后直接重跑
- 只想重做某几步：`--only wiki,issue-repos`（步骤名见 `bootstrap.py` 顶部的 `STEPS`）
- 建站期间 apply 会**直接推默认分支**（这时还没有可以关联的 issue）。建站完成后，一切改动按 `AGENTS.md` 走 issue 和 PR
- verify 有 FAIL 就修，修完重跑 verify，直到 0 FAIL。WARN 逐条看，写进给用户的汇报

apply 做的事，对应第 15 章：

| apply 的步骤 | 第 15 章 |
|---|---|
| preflight、org | 准备、第 1 步 |
| teams | 第 2 步（含「建团队的人只留在一个团队」） |
| repos、grants | 第 3、4 步 |
| labels | 第 5 步 |
| meeting-issues | 第 6 步（例会记录 issue 是两个仓库的 1 号） |
| wiki、issue-repos | 第 8、9 步 |
| board | 第 10 步：从模板项目复制看板（自带 6 个状态、Size、Iteration、7 条自动规则、视图），改视图筛选、给团队授权、把 id 写进 `board.sh` |
| profile | 第 11 步 |
| code-repos、sync-agents | 第 12 步 |
| invite | 第 13 步 |

## 第 5 步 人：交给人做的事

verify 最后会列出「需要人核的」几项。整理成一条消息发给用户：

```
org 已建好：https://github.com/<org>
verify：N 项 PASS，0 FAIL，M 项 WARN（逐条列）

还需要你做：
1. 被邀请的人接受邀请（邀请 7 天过期）。查还没接受的：gh api orgs/<org>/invitations --jq '.[].login'
2. 请客户 GKE 组和训练组各一人接受邀请后，帮忙点三个链接：
   - GKE 组的人打开 https://github.com/<org>/project-management → 应该是 404
   - 训练组的人打开 wiki 和两个 issue 仓 → 都能打开
   - 两人都打开 https://github.com/<org> → 能看到主页和按钮
3. 打开两个 issue 仓的 issues/new/choose，确认每个模板都能点开
4. 给客户发通知（第 15 章第 16 步有样例）
```

然后**你自己**跑冒烟测试（第 15 章第 14 步的自动部分）：

```bash
python3 bootstrap/smoke.py org-config.yaml
```

它建一条测试 issue → 加看板 → 在自研代码仓提 PR → 合并 → 检查 issue 自动关闭、看板 Done → 删掉测试 issue 和分支。全部通过才算建完。

## 想先演练一遍

第一次做、或者改过脚本，先在一个**专门演练用的空 org** 里从头跑一遍第 1–4 步加 smoke，确认没问题，再用 `bootstrap/teardown.py` 清掉（它会删仓库，绝不要对客户的 org 跑）。
本书的脚本就是这样在一个空沙箱 org 里实测过的：apply 一次跑完，verify 118 项全部 PASS，重跑 apply 每一步都是「已是最新」，smoke 5/5。

## 你不能做的

照 `appendix/templates/AGENTS.md` 第 8 节，再加上建站特有的几条：

- 不建公开仓库
- 不邀请 `org-config.yaml` 之外的人
- 不改别的 org
- 不替用户确认设备码、不处理任何密码
- 不在任何文件里写入客户名、厂商内部链接（这些都会被客户看到）
- 不在用户确认 plan 之前跑 apply
