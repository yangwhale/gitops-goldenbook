# 第 15 章 建站手册：从零搭一个 org

可以照着敲的步骤。前面各章讲每样东西为什么这样设计，这里只讲怎么做、按什么顺序做。
一个熟练的人大约一天做完；第一次做留两天。

## 准备

全程用 `gh` 命令行和 `git`。令牌权限：

| 权限 | 用途 |
|---|---|
| `repo` | 建仓库、推代码 |
| `admin:org` | 建团队、授权、邀请成员、改 org 设置 |
| `project` | 建看板、改字段 |
| `workflow` | 推带 `.github/workflows/` 的上游代码（镜像上游时会带上） |
| `delete_repo` | 只在清理测试仓库时需要 |

```bash
gh auth refresh -s admin:org,project,workflow
gh auth setup-git          # 让 git push 用 gh 的凭据
gh auth status             # 确认 scopes
pip install pyyaml         # 第 9 步检查模板 YAML 用

ORG=<你的 org 名>
B=$HOME/gitops-goldenbook  # 本书仓库 clone 下来的绝对路径
ME=$(gh api user --jq .login)
```

## 第 0 步 先做决定（半小时，写在一张纸上）

| 决定 | 原项目的答案 | 依据 |
|---|---|---|
| org 名 | 一座山的名字 | 不含客户名、产品代号（第 2 章 2.9） |
| issue 仓几个、怎么划界、谁兜底 | 两个：训练与推理（兜底）、基础设施 | 第 2 章 2.3 的三个问题 |
| 客户分几个组、可见性矩阵 | 训练组看两个，GKE 组和网络组只看 infra | 第 3 章 3.3、第 16 章 16.2 |
| 两组都要看的内容放哪 | infra 仓 | 第 2 章 2.4 |
| Owner 名单 | account team 里负责加人的几个人 | 第 3 章 3.2 |
| 要建哪些代码仓、各走哪种上游方式 | 一个长期分叉、五个跟随上游的副本、一个自研 | 第 9 章 9.2 |
| 开不开 Actions | 不开 | 第 14 章 14.3 |
| 有没有固定路由 | 有一条 | 第 6 章 6.5 |
| 加人要不要开 issue | 不要，Owner 直接按团队加 | 第 3 章 3.9 |

**只有一拨受众时**：只建一个 `project-management`，下面所有涉及 `project-management-infra` 的步骤跳过，客户只建一个子团队或者直接进 `customer`。

## 第 1 步 建 org（网页）

GitHub 不能用 API 建 org，在网页上建：<https://github.com/organizations/plan> → Free。然后：

```bash
gh api -X PATCH orgs/$ORG -f default_repository_permission=none -F members_can_fork_private_repositories=false
gh api orgs/$ORG --jq '{default_repository_permission, members_can_fork_private_repositories, plan: .plan.name}'
# 不开 Actions 的话
gh api -X PUT orgs/$ORG/actions/permissions -f enabled_repositories=none
```

网页上再确认 Settings → Member privileges：Base permissions 是 **No permission**；「Allow forking of private repositories」**不勾**。
建公开仓库在免费档关不掉，靠规矩（第 3 章 3.6）。

## 第 2 步 建团队

```bash
mkteam() {  # 名字 描述 [父团队 id]
  gh api -X POST orgs/$ORG/teams -f name="$1" -f description="$2" -f privacy=closed ${3:+-F parent_team_id=$3} --jq '"\(.slug) \(.id)"'
}
mkteam maintainers "管理员：account team 的厂商员工，所有仓库 Admin，管设置、权限和规矩"
mkteam googlers    "厂商员工：支持客户的工程师，所有仓库 Maintain"
mkteam customer    "客户工程师：联合开发仓库读写，可提 PR、写 RFC；不能访问厂商专属仓库"
mkteam partners    "合作方：第三方工程团队，只授权其负责的仓库"
mkteam observers   "旁观者：客户管理层、PM 等，只读看进度和 wiki"
CUST=$(gh api orgs/$ORG/teams/customer --jq .id)
mkteam training "客户训练组（继承 customer 组的全部仓库权限）" $CUST
mkteam gke      "客户 GKE 组（继承 customer 组的全部仓库权限）" $CUST
mkteam network  "客户网络组（继承 customer 组的全部仓库权限）" $CUST

# 建团队的人会自动成为每个团队的成员。一人只进一个团队（第 3 章 3.4）：只留在 maintainers
for t in googlers customer partners observers training gke network; do
  gh api -X DELETE orgs/$ORG/teams/$t/memberships/$ME
done
```

子团队名不带父团队前缀（第 3 章 3.3）。

## 第 3 步 建仓库

```bash
settings() { gh api -X PATCH repos/$ORG/$1 -F has_issues=$2 -F has_wiki=false -F has_discussions=false -F delete_branch_on_merge=true >/dev/null; }
mkrepo() {  # 名字 描述 issues(true|false)
  gh repo create $ORG/$1 --private --add-readme --description "$2" && settings $1 $3
}
mkrepo wiki                      "规矩（AGENTS.md）、守则、RFC、新人入门；规矩和权限的 issue" true
mkrepo project-management        "训练与推理的 issue；这一方向的文档、例会纪要、配方和复现" true
mkrepo project-management-infra  "GKE on TPU 与网络的 issue；这一方向的文档、例会纪要、配方和复现" true
mkrepo .github-private           "org 主页（成员可见）" false
```

`--add-readme` 让仓库一建好就有 `main` 分支。空仓库没有分支，后面的同步脚本会失败。

代码仓：

```bash
# 自研工具
mkrepo <工具名> "<一句话>" false

# 上游私有副本（第 9 章 9.1）
git clone --bare https://github.com/<上游>/<项目>.git /tmp/<项目>.git
gh repo create $ORG/<项目> --private --description "<上游> 的私有副本"
git -C /tmp/<项目>.git push --mirror https://github.com/$ORG/<项目>.git
settings <项目> false
```

> `push --mirror` 会把上游的所有分支和 tag 都推过来。只想要默认分支的，改为 `git -C /tmp/<项目>.git push https://github.com/$ORG/<项目>.git main:main --tags`。

## 第 4 步 给团队授权

权限值：`pull`（Read）、`triage`、`push`（Write）、`maintain`、`admin`。

```bash
grant() { gh api -X PUT orgs/$ORG/teams/$1/repos/$ORG/$2 -f permission=$3 >/dev/null && echo "$1 → $2: $3"; }

for r in wiki project-management project-management-infra <代码仓...>; do
  grant maintainers $r admin
  grant googlers    $r maintain
done
for r in wiki <联合开发的代码仓...>; do
  grant customer  $r push
  grant observers $r pull
done
grant partners wiki push

# 两个 issue 仓：customer 不授权，子团队各自授权
grant training project-management       push
grant training project-management-infra push
grant gke      project-management-infra push
grant network  project-management-infra push
grant observers project-management       pull
grant observers project-management-infra pull
grant partners  project-management       triage
```

`.github-private`：原项目给 maintainers Maintain，其余团队 Read。GitHub 文档没说成员看主页要对这个仓库有读权限，但主页里相对路径引用的按钮图片需要能读到仓库，照原项目给 Read 最稳：

```bash
grant maintainers .github-private maintain
for t in googlers customer partners observers; do grant $t .github-private pull; done
```

核对授权：

```bash
for t in maintainers googlers customer training gke network partners observers; do
  gh api --paginate orgs/$ORG/teams/$t/repos --jq '.[]|"'$t' \(.name) \(.role_name)"'
done | sort
```

子团队从父团队继承来的权限会不会出现在这个列表里，GitHub 文档没写清楚。**继承的效果在第 14 步用客户测试账号实测**。

## 第 5 步 标签

```bash
bash $B/appendix/scripts/setup-labels.sh $ORG/wiki                     wiki
bash $B/appendix/scripts/setup-labels.sh $ORG/project-management       training
bash $B/appendix/scripts/setup-labels.sh $ORG/project-management-infra infra
```

脚本删掉 GitHub 的默认标签，建好第 4 章的标签表。领域不同的，先改脚本里的 `area/*`。

## 第 6 步 两条例会记录 issue（先建，让它们是 1 号）

模板里的纪要规矩写死了「例会记录 issue 是 1 号」。所以在 issue 仓里**第一个**建它们：

```bash
gh issue create -R $ORG/project-management --title "训练例会记录" --label type/docs \
  --body-file $B/appendix/templates/meeting-log-issue-training.md
gh issue create -R $ORG/project-management-infra --title "基础设施例会记录" --label type/docs \
  --body-file $B/appendix/templates/meeting-log-issue-infra.md
gh issue pin 1 -R $ORG/project-management
gh issue pin 1 -R $ORG/project-management-infra
```

两条的 URL 应该都以 `/issues/1` 结尾。不是的话，把 `meetings/README.md` 和 PR 模板里的 `#1` 改成实际号码。第 10 步建好看板后再把它们加进看板。

## 第 7 步 统一替换示例名

所有模板里的示例名要换成你的。先拷一份到工作目录，一次替换完：

```bash
W=/tmp/tpl && rm -rf $W && cp -r $B/appendix $W
git -C $W init -q 2>/dev/null; cd $W
# 文件名
mv templates/wiki/onboarding/working-in-northpeak.md templates/wiki/onboarding/working-in-$ORG.md
# 内容：org 名大小写两种都换；开发分支名按你的实际改
ORG_TITLE=<你的 org 名的首字母大写写法，如 NorthPeak>
DEVBR=<代码仓开发分支名>
MODEL=<客户模型的叫法，如 ModelY>
VENDOR=Google     # 厂商不是 Google 的，改成你的厂商名
grep -rlI . -e northpeak -e NorthPeak -e modelx -e ModelX -e Google | xargs sed -i \
  -e "s/northpeak/$ORG/g" -e "s/NorthPeak/$ORG_TITLE/g" -e "s/modelx/$DEVBR/g" -e "s/ModelX/$MODEL/g" -e "s/Google/$VENDOR/g"
grep -rliI 'northpeak\|modelx' . && echo "↑ 还有残留" || echo "替换干净"
```

然后按附录 A 改 `templates/AGENTS.md` 里要按项目重写的部分（划界、领域标签、模板枚举、固定路由、精度清单）。

## 第 8 步 填 `wiki`

```bash
gh repo clone $ORG/wiki /tmp/wiki && cd /tmp/wiki
T=$W/templates
mkdir -p docs/onboarding docs/rfc docs/best-practices scripts .github/ISSUE_TEMPLATE
cp $T/AGENTS.md $T/CLAUDE.md $T/GEMINI.md .
cp $T/wiki/README.md README.md
cp $T/wiki/onboarding/*.md docs/onboarding/
cp $T/wiki/rfc/*.md docs/rfc/
cp $T/wiki/code-review.md docs/best-practices/
cp $T/wiki/ISSUE_TEMPLATE/*.yml .github/ISSUE_TEMPLATE/
cp $T/wiki/CODEOWNERS .github/CODEOWNERS
cp $T/pull_request_template.md .github/
cp $W/scripts/{board.sh,sync-agents.sh,pr-check.py} scripts/
git add -A && git commit -m "docs: 初始规矩" && git push

# 从这里开始，wiki 的改动走 PR。先建一条「初始化」issue，后面的 PR 都关联它
INIT=$(gh issue create -R $ORG/wiki --title "初始化 org：看板、同步 AGENTS.md、代码仓约定文件" --label type/chore --body "建站手册第 9–12 步的改动都关联这一条。" | grep -o '[0-9]*$')
echo "wiki 初始化 issue：#$INIT"
```

`wiki` 的第一次提交直接推 `main`：这时还没有可以关联的 issue。`docs/best-practices/` 里如果你的项目有精度、数值类的速查，也放进来，并把 `AGENTS.md` 第 5 节最后一条指向它。

## 第 9 步 两个 issue 仓

```bash
for r in project-management project-management-infra; do
  kind=$([ $r = project-management ] && echo training || echo infra)
  S=$W/templates/issue-repo-$kind
  gh repo clone $ORG/$r /tmp/$r && cd /tmp/$r
  mkdir -p .github/ISSUE_TEMPLATE assets/issues library meetings/_template recipes repro/common repro/issues
  cp $S/ISSUE_TEMPLATE/* .github/ISSUE_TEMPLATE/
  cp $S/README.md README.md
  cp $S/pull_request_template.md $S/CODEOWNERS .github/
  for d in library meetings recipes repro; do cp $S/$d-README.md $d/README.md; done
  cp $W/templates/meetings-notes-template-$kind.md meetings/_template/notes.md
  cp $W/scripts/check_dir_list.py repro/common/
  cp /tmp/wiki/AGENTS.md /tmp/wiki/CLAUDE.md /tmp/wiki/GEMINI.md .
  touch assets/issues/.gitkeep repro/issues/.gitkeep
  python3 -c 'import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob(".github/ISSUE_TEMPLATE/*.yml")]' && echo "YAML ok"
  git add -A && git commit -m "chore: 初始结构、模板、规矩" && git push
done
```

`check_dir_list.py` 两个仓库用同一份，运行时把本仓库全名作参数：`python3 repro/common/check_dir_list.py repro $ORG/$r`。

推完后在浏览器打开两个仓库的 `issues/new/choose`，**逐个点开每个模板**——GitHub 对表单格式错误只在页面上提示，模板会静默消失。

## 第 10 步 建看板

```bash
gh project create --owner $ORG --title "<org 名>" --format json --jq '.number'   # 记下编号，通常是 1
N=1
gh project field-create $N --owner $ORG --name Size --data-type SINGLE_SELECT --single-select-options "S,L"
```

以下在网页上做：

1. Settings → Visibility：**Private**
2. Settings → README：「状态由规则自动改，别手动拖；规矩见 `<org>/wiki` 的 AGENTS.md。」
3. Settings → Fields → **Status**：把默认的三个选项改成 `Triage`、`Design Pending`、`Ready to Develop`、`In Progress`、`Blocked`、`Done`
4. Settings → Fields → New field → **Iteration**：默认长度设 4 周或 30 天，然后把每一期的起止手动对齐到自然月、标题改成月份（`2026-11`）。GitHub 会按默认长度预先排出后面几期，大小月不一样，所以每月初顺手调下一期（第 5 章 5.3、第 18 章 18.5）
5. Workflows：打开 Item added to project（设 Triage）、Item closed（Done）、Item reopened、Pull request linked to issue（In Progress）、Pull request merged（Done）、Auto-close issue、Auto-add sub-issues to project
6. 视图：默认视图之外加「训练与推理」（筛选 `repo:<org>/project-management -repo:<org>/project-management-infra`）、「基础设施」（筛选 `repo:<org>/project-management-infra`）

查 id：

```bash
gh api graphql -f query="{organization(login:\"$ORG\"){projectV2(number:$N){id}}}" --jq .data.organization.projectV2.id
gh project field-list $N --owner $ORG --format json --jq '.fields[]|select(.options)|{name,id,options:[.options[]|{name,id}]}'
```

把 id 填进 `wiki/scripts/board.sh`，**走 PR**：

```bash
cd /tmp/wiki && git switch -c chore/$INIT-board-ids
# 编辑 scripts/board.sh 顶部的 PROJECT、F_STATUS、F_SIZE、STATUS、SIZE
git commit -am "chore: board.sh 填入看板 id" && git push -u origin HEAD
gh pr create --fill --body "## 做了什么

board.sh 填入本 org 看板的 project / 字段 / 选项 id。

## 关联

Refs #$INIT

## 怎么验证的

用例会记录 issue 跑 add，看板上出现且 Status=Triage。

## 和原计划的偏差

无"
gh pr merge --squash --delete-branch
```

把两条例会记录 issue 加进看板，顺便验证脚本：

```bash
board() { bash /tmp/wiki/scripts/board.sh "$@"; }
board add https://github.com/$ORG/project-management/issues/1 S
board add https://github.com/$ORG/project-management-infra/issues/1 S
```

## 第 11 步 org 主页

```bash
gh repo clone $ORG/.github-private /tmp/ghp && cd /tmp/ghp && mkdir -p profile
cp $W/templates/org-profile/* profile/
# 按你的项目改：org 名来历、两个仓库的划界、模板表、「正在做」、仓库表
git add -A && git commit -m "docs: org 主页" && git push
```

`.github-private` 是例外：它不放 `AGENTS.md`，也不在 `sync-agents.sh` 的同步目标里——没有人在这个仓库里写代码。

## 第 12 步 代码仓的约定文件

每个代码仓放这几样：

| 文件 | 来源 |
|---|---|
| `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` | `AGENTS.md` 由同步脚本放；另外两个一行 `@AGENTS.md` |
| `README.md` | `templates/code-repo/README.md`（上游副本：在上游 README 顶部加一段，或者另起 `FORK.md` 并在 README 第一行指过去） |
| `.github/pull_request_template.md` | `templates/code-repo/pull_request_template.md`（不涉及数值的删掉「数值影响」栏） |
| `.github/CODEOWNERS` | `templates/code-repo/CODEOWNERS` |
| `FORK.md` | 上游副本才有，照 `templates/FORK.md` 改 |

```bash
for r in <代码仓...>; do
  gh repo clone $ORG/$r /tmp/$r && cd /tmp/$r
  git switch -c chore/$INIT-org-conventions
  mkdir -p .github
  cp $W/templates/code-repo/pull_request_template.md $W/templates/code-repo/CODEOWNERS .github/   # 覆盖上游自带的
  cp /tmp/wiki/CLAUDE.md /tmp/wiki/GEMINI.md .
  # 上游副本：写 FORK.md；删掉或停用上游自带的 .github/workflows（第 9 章 9.3）
  git add -A && git commit -m "chore: 本 org 的约定文件" && git push -u origin HEAD
  gh pr create --fill --body "## 做了什么

加本 org 的约定文件。

## 关联

Refs $ORG/wiki#$INIT

## 怎么验证的

文件齐全。

## 和原计划的偏差

无"
done
```

上游副本**会自带上游的 `CODEOWNERS`、`AGENTS.md`**，里面写的是上游的团队和规矩，一定要覆盖掉。

然后改 `/tmp/wiki/scripts/sync-agents.sh` 顶部的 `ORG`、`TARGETS`（每个代码仓和它要同步的分支，包括开发分支）、`DIRECT`，走 PR 合并，再跑：

```bash
cd /tmp/wiki && git pull
bash scripts/sync-agents.sh $ORG/wiki#$INIT
# 合并开出来的同步 PR，再跑一次，所有目标都应输出「已一致」
```

## 第 13 步 邀请成员

先 Owner，再厂商工程师，最后客户。准备**客户测试账号**：最简单的是请客户 GKE 组和训练组各先派一个人第一批加入，第 14 步请他们帮忙点几个链接；或者厂商同事用一个私人 GitHub 账号临时加进 `gke` 测完再移出。

```bash
invite() {  # 账号 团队slug [admin]
  local uid tid
  uid=$(gh api users/$1 --jq .id); tid=$(gh api orgs/$ORG/teams/$2 --jq .id)
  gh api -X POST orgs/$ORG/invitations -F invitee_id=$uid -F "team_ids[]=$tid" -f role=${3:-direct_member} \
    --jq '"已邀请 \(.login) → '$2' (\(.role))"'
}
invite <厂商 Owner 账号> maintainers admin    # Owner：邀请时直接给 admin，不用等接受后再升
invite <厂商工程师账号> googlers
invite <客户训练组账号> training
invite <客户 GKE 组账号> gke
# ⚠ 书里的 alice-g、bob-g 这些示例名在 GitHub 上可能是真实的陌生人，别照抄
```

查还没接受的邀请：`gh api orgs/$ORG/invitations --jq '.[]|"\(.login // .email) \(.created_at)"'`。邀请 7 天过期。

同时建好厂商内部的账号对照表（第 3 章 3.10）。

## 第 14 步 冒烟测试：走一遍全流程

邀请接受之后，用一个真实的小任务（或一个测试 issue）走一遍：

| 步骤 | 确认 |
|---|---|
| 网页上用「功能与开发任务」模板建 issue | 自动打了 `type/feat` |
| `board add <URL> S` | 看板上出现，Status = Triage，Size = S |
| 在代码仓开分支、提 PR，正文 `Closes $ORG/project-management#<号>` | 看板 Status 变 In Progress |
| `python3 /tmp/wiki/scripts/pr-check.py` 检查 PR 正文 | 通过 |
| 合并 PR（合进默认分支） | issue 自动关闭，看板 Status = Done |
| 对另一个 issue `board status <URL> Blocked` | 看板 Status = Blocked |
| 让一个 AI 助手「先读 AGENTS.md，再提一个 issue」 | 模板字段、标签、看板都对 |
| 客户 GKE 组的账号打开 `project-management` | 404 |
| 客户训练组的账号打开 `wiki`、代码仓、两个 issue 仓 | 都能打开，能提 issue、能推分支（验证子团队继承） |
| 客户账号打开 `https://github.com/$ORG` | 看到成员版主页，四个按钮都能点 |

测试 issue 用完删掉：`gh issue delete <URL> --yes`（需要 Admin）。

## 第 15 步 收尾检查

```bash
# 所有仓库里不应再有示例名
for r in $(gh repo list $ORG --json name --jq '.[].name'); do
  gh api "search/code?q=org:$ORG+repo:$ORG/$r+northpeak" --jq '.total_count' 2>/dev/null | grep -qv '^0$' && echo "$r 里还有 northpeak"
done
```

（代码搜索对新仓库有索引延迟，更可靠的是在本地 clone 里 `grep -rli 'northpeak\|modelx'`。）

再对照附录 D.1 逐条打勾。特别核一条：**`AGENTS.md` 第 4 节写的 CI 状态和第 1 步对 Actions 的决定一致**。

## 第 16 步 告诉客户

在聊天群里发一段话（样例）：

> 我们为这个项目建了一个 GitHub org：https://github.com/<org> （邀请已发到各位的 GitHub 账号，请在邮箱或 GitHub 通知里接受）。
>
> 以后的技术问题请在这里提 issue：训练、推理、框架、精度、性能 → project-management；GKE、切片、节点池、网络 → project-management-infra。
> 拿不准就提到现象出现的那一边，我们会处理，不用重提。每个模板只有「问题描述」必填。
>
> 用 AI 助手的话，跟它说一句「先读 AGENTS.md，再按里面的规矩来」就行。
>
> 还没有 GitHub 账号或者没收到邀请的，把 GitHub 用户名发给我。

**消息要短。** 原项目给客户写的说明改了好几轮，每轮都在删：删掉分支名、目录说明这些客户点进主页自然会看到的东西，只留「去哪提、拿不准怎么办」。

## 之后的第一周

见第 18 章。最重要的一件事：**第一批 issue 由厂商工程师亲自分诊，严格照规矩来**——它们会成为客户和 AI 助手模仿的样板。
