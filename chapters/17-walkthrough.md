# 第 17 章 端到端演练

三个虚构的故事，把前面的规则串起来。每一步都给出实际的命令、issue 正文、评论、PR 正文和看板状态。
示例 org 是 `northpeak`，人物：

| 账号 | 谁 | 团队 |
|---|---|---|
| `alice-g` | 厂商，account team，Owner | `maintainers` |
| `bob-g` | 厂商，训练方向工程师 | `googlers` |
| `erin-g` | 厂商，GKE 方向工程师 | `googlers` |
| `carol-c` | 客户训练组 | `training` |
| `dave-c` | 客户 GKE 组 | `gke` |
| `frank-c` | 客户训练组新人 | （待加入） |

---

## 故事一：一个跨两边的 bug

### 第 1 天 09:40 客户在训练仓报问题

`carol-c` 在 org 主页点「提交训练与推理的 issue」，选「报错与故障」模板，只填了第一栏：

```markdown
### 问题描述

64 机的作业跑了 3 个多小时突然全部退出，日志最后是
`RuntimeError: Slice health check failed: 1 of 64 hosts unreachable`。
昨天也挂过一次，也是 3 小时左右。

### 跟哪块有关

不知道 / 都不是
```

模板自动打上 `type/bug`。标题：`64 机作业约 3 小时后全部退出`。这是 `northpeak/project-management#52`。

> 网页上建的 issue 不会自动进看板（第 5 章 5.4），需要分诊的人加。

### 第 1 天 10:15 分诊

`bob-g` 分诊：

```bash
gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- add https://github.com/northpeak/project-management/issues/52 S
gh issue edit 52 -R northpeak/project-management --add-assignee bob-g --add-label size/S,P1
```

看板：**Triage**，Size = S。

他**不评论**「我来看一下」（assignee 已经说明了）。

### 第 1 天 11:30 补运行条件

`bob-g` 查了客户的作业日志，把运行条件补成第一条评论（不要求客户补填）：

```markdown
运行条件（从作业日志查到）：

- 代码：northpeak/maxtext @ modelx @ 9a1c2e0；jax 0.11.1 / libtpu 0.0.46
- 硬件：v5p-256（4x8x8），64 主机，节点池 np-v5p-256-a
- 作业：JobSet `modelx-pt-0412`、`modelx-pt-0411`（昨天那次）
- 两次退出时间：运行 3h12m、3h07m；退出前 2 分钟，节点 gke-np-v5p-256-a-7f3c 的 kubelet 有 `NodeNotReady` 事件

初步判断不是训练代码的问题：两次都是同一个节点先失联。
```

### 第 1 天 14:00 根因在 infra，开一条 infra issue

查下来是集群层面的事。这条 issue 有客户参与、而且是从训练仓往 infra 仓——**可以转移**（训练组两边都能看，第 6 章 6.6）。
但 `bob-g` 判断训练仓这条还要继续跟踪作业的恢复配置（checkpoint 间隔），两边都有事，于是**不转移**，在 infra 另开一条，排查过程只记在 infra：

```bash
cat > /tmp/body.md <<'MD'
### 问题描述

训练作业两次在约 3 小时后因节点 gke-np-v5p-256-a-7f3c 失联而退出，
来源：northpeak/project-management#52。需要查这个节点为什么周期性 NotReady。

### 跟哪块有关

维修与健康（含芯片、主机故障）

### 集群与版本

<项目> / <集群> / <区域>，GKE 1.33.5-gke.1080000

### 节点池

np-v5p-256-a，v5p，4x8x8，64 节点，预留

### kubectl 输出与事件

（kubectl describe node 和 events 的关键几行）
MD
gh issue create -R northpeak/project-management-infra --title "排查节点周期性 NotReady 导致训练作业退出" --label type/bug --body-file /tmp/body.md
# → northpeak/project-management-infra#18
gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- add https://github.com/northpeak/project-management-infra/issues/18 S
gh issue edit 18 -R northpeak/project-management-infra --add-assignee erin-g --add-label size/S,P1
```

注意：

- 建 issue 时**不打 `area/*`**，「跟哪块有关」照实填
- 标题动词开头，不带句号
- 正文按 infra 仓「报错与故障」模板的 `### 字段名` 顺序写

然后 `bob-g` 在训练仓那条评论：

```markdown
节点失联的根因在 northpeak/project-management-infra#18 排查，那边有结论会同步到这里。
这边继续跟作业侧的恢复：当前 checkpoint 间隔 2 小时，节点失联最多丢 2 小时进度。
```

**跨仓库引用写全名**（`northpeak/project-management-infra#18`，不是 `#18`）。

### 第 2 天 GKE 组参与

`erin-g` 在 infra#18 下排查，`dave-c`（客户 GKE 组）补充了节点的维修记录。`dave-c` **看不到**训练仓的 #52，但他不需要——infra#18 的正文已经写清了现象，不依赖那个链接。

`erin-g` 的结论评论：

```markdown
结论：节点 gke-np-v5p-256-a-7f3c 的一块芯片 ICI 链路间歇性降级，健康检查每约 3 小时
触发一次重新探测，探测期间节点上报 NotReady，切片控制器把整个切片判为不健康。

| 时间 | 事件 |
|---|---|
| 04-11 13:07 | ICI link degraded（chip 2, port 3） |
| 04-11 13:09 | NodeNotReady |
| 04-12 15:12 | ICI link degraded（chip 2, port 3） |
| 04-12 15:14 | NodeNotReady |

处理：该节点已提维修，换下后节点池恢复 64/64。维修单号已记在厂商侧。
```

打上 `area/gke`（查清了根因，现在打）。

### 第 2 天 结论同步回训练仓

`bob-g` 在训练仓 #52 评论**结论本身**，不只贴链接（训练仓的合作方看不到 infra）：

```markdown
节点失联的根因（详见 northpeak/project-management-infra#18）：一个节点的芯片 ICI 链路间歇性降级，
健康检查每约 3 小时重新探测一次，期间整个切片被判为不健康，作业退出。该节点已换下，节点池恢复 64/64。

作业侧：checkpoint 间隔从 2 小时改为 30 分钟，见 northpeak/maxtext#71。
```

### 第 3 天 作业侧的 PR

```bash
git switch modelx && git pull
git switch -c fix/52-ckpt-interval
# ……改配置……
git commit -F /tmp/msg.txt        # 第一行：fix: checkpoint 间隔改为 30 分钟
git push -u origin fix/52-ckpt-interval
```

PR 正文：

```markdown
## 做了什么

ModelX 预训练配置的 checkpoint 间隔从 2 小时改为 30 分钟。

## 关联

Closes northpeak/project-management#52

## 怎么验证的

v5p-256 上跑 1 小时：两次 checkpoint 各耗时 41 s、39 s，步时无变化（run-ID ckpt30-r1）。

## 数值影响

数学不变

## 和原计划的偏差

无
```

提 PR 前本地自查：

```bash
python3 pr-check.py < /tmp/pr-body.md     # ✓ 通过
```

PR 关联到 issue → 看板：**In Progress**（规则自动）。

### 第 3 天 合并，手动关

PR 合进 `modelx`——**不是默认分支**，GitHub 不会按 `Closes` 关 issue。手动关：

```bash
gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- status https://github.com/northpeak/project-management/issues/52 "Blocked"
```

修复给出了，但客户还没在自己的作业上验证，所以**先不关**，设 Blocked，评论写清在等什么：

```markdown
northpeak/maxtext#71 已合进 modelx @ 3c4d5e6。等 @carol-c 下一次 64 机作业确认 checkpoint 间隔是 30 分钟。
```

### 第 5 天 客户确认，关闭

`carol-c` 评论「新作业 checkpoint 每 30 分钟一次，节点池恢复后跑了 9 小时没再退出」。`bob-g` 关闭：

```bash
gh issue close https://github.com/northpeak/project-management/issues/52 --comment "由 northpeak/maxtext#71 完成"
```

看板：**Done**（规则自动，issue 关闭触发）。infra#18 由 `erin-g` 在节点恢复后关闭。

---

## 故事二：一个大任务

### 提出

`carol-c` 用「功能与开发任务」模板：

```markdown
### 目标

ModelX 第二代要加一个视觉编码器（ViT，约 6 亿参数），和语言模型联合训练。希望下个月能在 v5p 上跑起来。

### 跟哪块有关

MaxText

### 哪类

新模型接入

### 验收标准

（空）
```

→ `northpeak/project-management#60`，自动打 `type/feat`。

### 分诊：这是 L

会改数据管道、模型定义、分片规则三个模块，需要客户先认可方案 → `size/L`。

下文的 `board.sh` 是这个函数的简写：

```bash
board.sh() { gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- "$@"; }
board.sh add https://github.com/northpeak/project-management/issues/60 L
gh issue edit 60 -R northpeak/project-management --add-assignee bob-g --add-label size/L,P1
```

### 写 RFC

`bob-g` 认领，开始写 RFC：

```bash
board.sh status https://github.com/northpeak/project-management/issues/60 "Design Pending"
```

在 `wiki` 里：

```bash
ls docs/rfc/          # 现有最大编号 0006（0004 被撤回，留了空缺）
cp docs/rfc/template.md docs/rfc/0007-modelx-vision-encoder.md
# 写 RFC：目标可验证、非目标必填……
# index.md 末尾加一行，状态 draft
git switch -c docs/60-rfc-vision-encoder
git commit -F /tmp/msg.txt && git push -u origin docs/60-rfc-vision-encoder
```

编号是 **0007**（最大值 + 1），不是 0006（文件个数 + 1）。

RFC 的非目标（节选）：

```markdown
### 非目标（必填）

- **不做视频输入**：第二代只有图像。视频要改数据格式，另开 issue
- **不做推理侧的视觉编码器**：本 RFC 只管训练
- **不追求和参考实现逐位一致**：参考实现在 GPU 上，按噪声带判对齐（门槛见「测试与验证」）
```

PR 正文 `Refs northpeak/project-management#60`（不是 `Closes`：RFC 合并只是方案定了）。请 `carol-c` 评审（RFC 目录对客户开放，第 8 章 8.5）：

```bash
gh api -X POST repos/northpeak/wiki/pulls/112/requested_reviewers -f 'reviewers[]=carol-c'
```

### RFC 合并

`index.md` 状态改 `accepted`，issue 设：

```bash
board.sh status https://github.com/northpeak/project-management/issues/60 "Ready to Develop"
```

### 拆子任务

按 RFC 的实施计划拆成三个 SubTask，挂在 #60 下（#60 本身成为总表——「一个大任务要拆给不同的人」，第 6 章 6.11）：

```bash
for t in "接入 ViT 编码器的模型定义" "数据管道支持图文交错样本" "视觉编码器的分片规则"; do
  url=$(gh issue create -R northpeak/project-management --title "$t" --label type/feat,size/S --body "属于 northpeak/project-management#60，设计见 wiki docs/rfc/0007-modelx-vision-encoder.md")
  # 挂成 sub-issue（父 issue 在看板上时，子 issue 自动进看板）
  sub_id=$(gh api "repos/northpeak/project-management/issues/${url##*/}" --jq .id)
  gh api -X POST repos/northpeak/project-management/issues/60/sub_issues -F sub_issue_id=$sub_id
done
gh issue edit 60 -R northpeak/project-management --add-label tracker
```

三个子任务分给三个人，各自走「小任务」路径。全部关闭后关 #60。

### 实施中方案变了

数据管道那个子任务做到一半发现，RFC 里写的「在线拼接图文样本」太慢，改成离线预处理。PR 的偏差栏：

```markdown
## 和原计划的偏差

RFC-0007 写的在线拼接 → 实际离线预处理成 ArrayRecord → 在线拼接让每步数据等待 0.8 s（run-ID vl-data-r3），
离线后降到 0.02 s。已在 RFC-0007 的「和原计划的偏差」一节回填。
```

**同时回 RFC 里更新原文**。

---

## 故事三：新人加入和一次例会

### 加人

`carol-c` 在聊天群里说：「我们组新来的 frank-c 也需要权限，GitHub 是 frank-c。」

`alice-g`（Owner）：

```bash
gh api users/frank-c --jq '.login, .name'           # 确认账号存在
invite frank-c training                              # 第 15 章第 13 步的函数
```

只需要问清一件事：**属于哪个组**。carol-c 说是训练组，那就进 `training`。

### 例会

周四的训练例会讨论了 #52、#60 和客户新提的一份 12 条问题清单。

会后 `bob-g`：

1. 写纪要 `project-management/meetings/2026-04-16-training-weekly/notes.md`：

   ```markdown
   # 训练例会 2026-04-16：周会

   - 参会：厂商 bob-g、alice-g；客户 carol-c、frank-c

   ## 结论

   - checkpoint 间隔改为 30 分钟，已合并（northpeak/project-management#52）
   - 视觉编码器 RFC 客户无异议，本周合并（northpeak/project-management#60）
   - 问题清单 12 条里，第 3、7 条建 issue，其余是使用问询，会上已答，不建

   ## 待办

   - [ ] 视觉编码器 RFC 合并 — northpeak/project-management#60
   - [ ] 清单第 3 条：bf16 下 RMSNorm 和 GPU 对不齐 — northpeak/project-management#63
   - [ ] 清单第 7 条：长序列 OOM — northpeak/project-management#64
   - [ ] 下次例会改到周三：carol-c，下周
   ```

2. 提 PR，关联行 `Refs northpeak/project-management#1`（训练例会记录 issue，建站时第一个建的），**不写 Closes**
3. 每条结论在对应 issue 里评论（#60 下评论「04-16 例会：客户对 RFC-0007 无异议」）
4. 清单 12 条只建了 2 条 issue（**不要因为它出现在清单上就建**）
5. 群里发一句：纪要和新 issue 的链接

---

## 让 AI 助手做这些

上面每一步都可以让 AI 助手代做。人要说的话很短：

| 场景 | 对助手说 |
|---|---|
| 替客户建 issue | 「先读 AGENTS.md。把下面这段客户原话建成 issue，客户是 @carol-c：……」 |
| 分诊 | 「先读 AGENTS.md。分诊 project-management 里 Triage 状态的 issue，先给我看你打算怎么设，我确认了再改」 |
| 补运行条件 | 「看一下 #52 的作业 modelx-pt-0412 的日志，把运行条件补成第一条评论」 |
| 提 PR | 「先读 AGENTS.md。按 #52 的结论改 checkpoint 间隔，提 PR」 |
| 写纪要 | 「先读 AGENTS.md 和 meetings/README.md。把下面的会议记录整理成纪要，提 PR」 |

AI 助手照 `AGENTS.md` 做时，会：用 `### 字段名` 按模板写正文、只打一个 type 标签、不打 `area/*`、建完跑 `board.sh add`、
PR 写全四栏、不加 AI 署名、评论里不写「已分给某某」。

账号主人要**看一眼再发**的：涉及承诺和对外表态的评论、关 issue、合并 PR。第 1 章原则 4：判完成、合并这类改变事实的动作，由人决定。
