# 附录 D 检查清单

打印出来用。每张表对应一个时刻。

## D.1 建站完成（第 15 章做完后逐条核）

- [ ] org 默认权限 None；禁止 fork 私有仓库
- [ ] 团队：maintainers、googlers、customer（子团队 training、gke、network，名字不带前缀）、partners、observers
- [ ] 所有仓库 Private；代码仓 Issues 关；所有仓库 Wiki 关
- [ ] 授权表核对命令的输出与第 3 章 3.3 一致
- [ ] 三个仓库的标签与第 4 章一致，没有 GitHub 默认标签
- [ ] 两个 issue 仓的新建页能打开每一个模板；没有「Open a blank issue」
- [ ] infra 仓的 `config.yml` 没有指向训练仓的链接
- [ ] 看板：Private、6 个 Status、Size、Iteration、7 条 Workflows 打开、两个视图
- [ ] `board.sh` 的 id 已替换，用测试 issue 跑通 add / status
- [ ] 除 `.github-private` 外，每个仓库有 `AGENTS.md`（与 wiki 逐字节相同）、`CLAUDE.md`、`GEMINI.md`、`README.md`
- [ ] 建团队的人只留在 `maintainers`
- [ ] 两个 issue 仓有 `CODEOWNERS`、`repro/common/check_dir_list.py`、`repro/issues/`
- [ ] 上游副本里上游自带的 `CODEOWNERS`、`AGENTS.md`、workflows 已覆盖或停用
- [ ] `sync-agents.sh` 全部输出「已一致」
- [ ] 代码仓有 PR 模板、`CODEOWNERS`；上游副本有 `FORK.md`
- [ ] 两条例会记录 issue 已建、已置顶；号码填进了 `meetings/README.md` 和 PR 模板
- [ ] org 主页（`.github-private`）四个按钮能点
- [ ] 邀请接受后：GKE 组账号打开训练仓是 404；训练组账号能打开 wiki 和代码仓（继承生效）
- [ ] 走完第 15 章第 14 步的全流程
- [ ] Actions 的决定已执行，`AGENTS.md` 第 4 节与之一致
- [ ] 每个仓库的本地 clone 里 `grep -rli 'northpeak\|modelx'` 为空（大小写都查）

## D.2 分诊一条 issue

- [ ] 在对的仓库（不对就按第 6 章 6.6 的表转移或另开）
- [ ] 恰好一个 `type/*`
- [ ] 在看板上
- [ ] 有 assignee（固定路由的按路由）
- [ ] 有 `size/*`
- [ ] 优先级：P0 只给阻塞的 bug；拿不准不打
- [ ] 运行条件缺的，查清后写第一条评论（不要求客户补）
- [ ] 客户原话有歧义的，写出理解、请客户确认
- [ ] **没有**写「我来看」「已分给某某」

## D.3 提一个 PR

- [ ] 有关联 issue
- [ ] 分支名 `<type>/<issue号>-<简述>`，推在本仓库
- [ ] 提交信息第一行 `<type>: <简述>`，正文用 `-F`，没有 AI 署名
- [ ] 正文 `Closes <org>/<repo>#<号>`（全名）
- [ ] 四栏都在；偏差栏写了内容或「无」
- [ ] 代码仓：数值影响栏
- [ ] assignee 是人
- [ ] 本地测试跑过；`pr-check.py` 通过
- [ ] 合进非默认分支的，合并后手动关 issue

## D.4 关一条 issue

- [ ] 验收标准逐条验证，证据（命令输出 / run-ID）在评论里
- [ ] PR 已合并，偏差已记录
- [ ] 文档已同步
- [ ] 客户验证过（需要的话）；没验证的设 Blocked 不关
- [ ] 是你负责的 issue（不是的话有人类明确要求，并在评论里注明）
- [ ] 另一边有关联 issue 的，结论已同步过去，一起关

## D.5 改一条规则

- [ ] 在 `wiki` 开了 issue
- [ ] 大改动写了 RFC（目标可验证、非目标、实施计划带权限和回退）
- [ ] `AGENTS.md` 改了，合并后跑了 `sync-agents.sh`
- [ ] 守则、入职文档、org 主页一起改了
- [ ] 被推翻的旧 RFC 内容用删除线 + 指针标出
- [ ] 需要的话例会上通知客户

## D.6 例会之后（当天）

- [ ] `notes.md` 照模板写，参会写 GitHub 账号
- [ ] PR `Refs` 例会记录 issue，不写 `Closes`
- [ ] 每条结论在对应 issue 里评论
- [ ] 新问题只建重要的
- [ ] slides 原样存档，错误写进「勘误」
- [ ] 群里发一句纪要和 issue 在哪

## D.7 季度对账

见第 18 章 18.6 的命令：没进看板的 issue、type 标签不是恰好一个的、Blocked 久无评论的、合进非默认分支未关的、团队成员、公开仓库、`AGENTS.md` 同步状态。
