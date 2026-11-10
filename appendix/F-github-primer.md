# 附录 F GitHub 速成

正文默认你熟悉下面这些 GitHub 概念。不熟的先花十分钟读完这一页。每一节只讲本书用到的部分。

## F.1 org、团队、权限档位

- **org**（organization）：一组仓库和成员的容器。org 本身对外公开可搜，里面的仓库可以是私有的
- **团队**（team）：org 里的一组成员。团队可以有**父团队**，子团队自动继承父团队对仓库的权限
- **Owner**：org 的管理员，能改一切设置；免费档里只有 Owner 能邀请新成员
- **仓库权限五档**，从低到高：

| 档位 | 能做什么 |
|---|---|
| Read | 看代码、看 issue、评论、提 issue |
| Triage | Read + 管 issue：改标签、assignee、关闭重开 issue（不能推代码） |
| Write | Triage + 推分支、合并 PR |
| Maintain | Write + 改大部分仓库设置、管标签 |
| Admin | 一切，包括删仓库、改可见性、管仓库权限 |

本书里：厂商工程师 Maintain，客户 Write，旁观者 Read（第 3 章）。

## F.2 issue、标签、assignee

- **issue**：一条事项，有标题、正文、评论、状态（开 / 关）。每个仓库的 issue 编号各自从 1 开始
- **标签**（label）：贴在 issue 上的分类，可以按标签筛选
- **assignee**：负责人，可以设多个
- **引用**：在任何地方写 `owner/repo#12` 会链到那条 issue；只写 `#12` 指**当前仓库**的 12 号（第 2 章 2.10）

## F.3 issue 表单（issue forms）

仓库里 `.github/ISSUE_TEMPLATE/*.yml` 的每个文件是一个**表单模板**。点「New issue」时让人选模板、按栏填写，提交后：

- 自动打上模板里写的标签（本书用它自动打 `type/*`）
- 生成的正文是每栏一个 `### 栏名` 小标题加内容

同目录的 `config.yml` 控制新建页：`blank_issues_enabled: false` 关掉「空白 issue」入口；`contact_links` 加几条指向别处的链接（第 4 章）。

## F.4 sub-issue

一条 issue 可以挂若干条 **sub-issue**（子 issue），父 issue 上显示子 issue 的完成进度。本书只在「总表」里用它（第 6 章 6.11）。

## F.5 PR 和关键字关闭

- **PR**（pull request）：把一个分支的改动请求合进另一个分支
- PR 正文里写 `Closes owner/repo#12`（或 `Fixes`、`Resolves`），PR **合进默认分支**时 GitHub 自动关闭那条 issue；合进其他分支时不关（第 7 章）
- `Refs owner/repo#12` 只建立链接，不关闭
- **合并方式**三种：merge commit（保留全部提交）、squash（压成一个）、rebase（逐个摆到目标分支上）

## F.6 Projects（看板）

新版 GitHub Projects 是挂在 org 上的表格 / 看板，条目是 issue 或 PR：

- **字段**：每个条目的属性。自带的有 Status、Assignees、Labels、Repository 等；可以加自定义字段，如单选（本书的 Size）、**迭代**（Iteration，一期一期的时间段）
- **视图**：同一批条目的不同筛选和排列，如「只看某个仓库」
- **workflows**：内置的自动规则，如「issue 关闭 → Status 设为 Done」「加入看板 → Status 设为 Triage」
- **Auto-add**：按条件自动把新 issue 收进看板（免费档只能开 1 条）

看板和 issue 是两层：issue 关了，看板条目还在，只是 Status 变了（第 5 章）。

## F.7 CODEOWNERS、分支保护、Actions

- **`CODEOWNERS`**：`.github/CODEOWNERS` 里写「哪个目录归谁」，PR 改到那个目录时自动请他们评审。code owner 必须对仓库有 Write
- **分支保护**：「合并前必须有人批准」「检查不过不能合并」等。私有仓库需要 Team 档（付费）
- **GitHub Actions**：GitHub 的 CI。私有仓库按分钟计费，免费档每月有额度（第 14 章）

## F.8 几个本书常用的词

| 词 | 意思 |
|---|---|
| permalink | 带 commit 号的文件链接（`/blob/<commit>/路径`），永远指向那一刻的内容；分支链接（`/blob/main/路径`）会随分支变 |
| digest | 镜像内容的哈希（`@sha256:...`），比 tag 可靠：tag 可以被重新指向别的镜像 |
| sha256 | 文件内容的哈希，用来证明「就是这个文件」 |
| run-ID | 一次运行的名字，也是它产物的目录名（第 12 章） |
| `gh` | GitHub 官方命令行。`gh api <路径>` 直接调 REST API，本书大部分命令用它 |
