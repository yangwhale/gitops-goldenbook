# 第 18 章 运营节奏

建好 org 只是开始。日常要做的事按频率排：每天、每周、每月、每季度，外加人进出和项目结束。

> 原项目里有些节奏是写死的（每两周同步上游、每季度对账），有些是自然形成的（谁分诊）。下文分别标出。

## 18.1 第一周：立样板

建完 org 的第一周决定了以后的风气。

- **第一批 issue 由厂商工程师亲自分诊，严格照规矩来**：标签、assignee、第一条评论补运行条件、结论写全。客户和 AI 助手会模仿它们
- 挑两三条写得最好的，放进入职文档的「例子」表（`working-in-<org>.md`），标出「看点」：

  | issue | 看点 |
  |---|---|
  | `<org>/project-management#12` | 客户原话 + 3 张截图；第一条评论是厂商侧结论：表格、7 张图、推荐配置、要客户补的东西 |
  | `<org>/project-management#17` | 原问题没写完：按上下文写出理解，**请客户确认**，不替客户编问题 |
  | `<org>/project-management#21` | 修复已给出，但「客户验证」没完成，所以不关，设 `Blocked` |

- 客户在聊天群里问问题时，**替他建成 issue**，把链接回到群里：「建成 issue 了：<链接>，后续在那里跟进」。几次之后客户会自己去提
- 规则哪里不顺手，当场改（原项目第一天改了二十多次，第 16 章）

## 18.2 每天

| 做什么 | 谁 | 原项目 |
|---|---|---|
| 分诊 Triage 列：仓库对不对、type 对不对、加看板、assignee、size、优先级、补运行条件 | 技术负责人或轮值 | 技术负责人兼 |
| 聊天里得出的结论回写到 issue | 得出结论的人 | 写死（「当天」） |
| 处理加人请求 | Owner | 按需，当天处理 |
| 跟随副本的上游同步 PR | 厂商侧定时任务；不满足自动合并条件的人工看 | 定时任务每天一次 |

## 18.3 每周

| 做什么 | 谁 |
|---|---|
| 例会，会后当天写纪要、结论回写 issue、新问题建 issue（只建重要的） | 厂商 |
| 看一遍 Blocked 列：每条都有评论说清在等什么吗？等的东西到了吗？ | 技术负责人 |
| 看一遍 In Progress 列：有没有 PR 合进了非默认分支、issue 还开着的？ | 技术负责人 |

## 18.4 每两周

| 做什么 | 谁 | 原项目 |
|---|---|---|
| 长期分叉的代码仓同步上游，跑冒烟，记同步记录 | `FORK.md` 里写的负责人 | 写死 |

## 18.5 每月

| 做什么 |
|---|
| 看板 Iteration 圈定本月要做的 Task |
| 把 Iteration 的下一期起止对齐到下个自然月（GitHub 按默认长度预排后面几期，大小月要手调） |
| 检查 Actions 分钟数（如果开着） |

## 18.6 每季度：对账

**把看板和仓库的数据拉一遍：哪些字段没人填、哪些规矩没人守、哪些自动化在空转。没人用的字段和规矩，删掉，别让它们继续产出假记录。**

对账清单：

```bash
ORG=<org>
# 1. 没进看板的 issue
for r in project-management project-management-infra; do
  gh issue list -R $ORG/$r -s open -L 1000 --json url --jq '.[].url'
done | sort > /tmp/issues.txt
gh project item-list 1 --owner $ORG -L 5000 --format json --jq '.items[].content.url' | sort > /tmp/board.txt
comm -23 /tmp/issues.txt /tmp/board.txt        # 开着但不在看板上的

# 2. 没有 type 标签、或有多个 type 标签的 issue
for r in project-management project-management-infra; do
  gh issue list -R $ORG/$r -s all -L 1000 --json number,labels \
    --jq '.[]|select(([.labels[].name|select(startswith("type/"))]|length)!=1)|"'$r'#\(.number)"'
done

# 3. Blocked 但最近 14 天没有评论的
# 4. 合进了非默认分支、issue 还开着的（看 PR 列表里 base 不是默认分支的已合并 PR）
# 5. 团队成员：每个人还在项目上吗？对照账号对照表（第 3 章 3.10）
for t in googlers training gke network partners observers; do
  gh api orgs/$ORG/teams/$t/members --paginate --jq '.[].login' | sed "s/^/$t /"
done
# 6. 有没有误建的公开仓库
gh api orgs/$ORG/repos --paginate --jq '.[]|select(.private==false)|.name'
# 7. sync-agents.sh 还是全部「已一致」吗
```

对账发现的问题，在 `wiki` 开一个 issue 记下来，改规矩的走 RFC。

## 18.7 人进出

**进**：第 3 章 3.9。要确认的只有一件事：属于哪个团队。

**出**：

1. 从团队移除：`gh api -X DELETE orgs/<org>/teams/<团队>/memberships/<账号>`
2. 从 org 移除：`gh api -X DELETE orgs/<org>/members/<账号>`
3. 他是 assignee 的开着的 issue，转给别人（改 assignee，**不评论「已转给某某」**）
4. 他在 `FORK.md`、固定路由里是负责人的，改掉
5. 更新账号对照表

**换岗**（客户的人从训练组转到 GKE 组）：从旧子团队移除、加进新子团队。一人只进一个团队。

## 18.8 新方向加入

客户新增一个组（比如推理组），或者 org 要纳管一个新领域：

1. 按第 2 章 2.3 的三个问题判断：要不要新的 issue 仓？
   - 不要：在现有 issue 仓的模板「跟哪块有关」加选项、加 `area/*` 标签（走 `wiki` issue）
   - 要：写 RFC，照 RFC-0001 的结构（第 16 章 16.1）
2. 要不要新的子团队？可见性矩阵怎么变？
3. 改 `AGENTS.md`、守则、入职文档、org 主页，同步

原项目纳管 GKE 和网络时，先走了「不要新仓库」，四天后发现不行，又写了 RFC 拆仓库。**如果新方向的人数和问题量都不小，直接拆。**

## 18.9 项目结束

- 所有开着的 issue：关掉或明确转给后续项目，评论写清状态
- 看板：最后一次对账，导出（`gh project item-list ... --format json`）存档
- 客户团队：按合同约定保留只读或移除。降成只读：从子团队移到 `observers`
- 仓库：**归档，不删除**。归档后一切链接照常能打开
- 厂商一侧：定时任务（上游同步）停掉；账号对照表存档
- 把这个项目改过的规则、踩过的坑，回写到下一个项目要用的模板里（也就是这本书）

## 18.10 节奏表

| 频率 | 事 |
|---|---|
| 每天 | 分诊、结论回写、加人、上游同步 PR |
| 每周 | 例会 + 纪要、看 Blocked、看 In Progress |
| 每两周 | 长期分叉同步上游 |
| 每月 | Iteration 排期 |
| 每季度 | 对账：字段、规矩、自动化、成员、公开仓库 |
| 按需 | 人进出、新方向、规则变更（RFC） |
