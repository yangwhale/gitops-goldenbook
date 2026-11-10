# 第 11 章 例会与纪要

会议是结论产生得最多、也丢得最多的地方。下面的规则只有一个目标：**会上说的每一句结论，第二天都能在 issue 里找到。**

## 11.1 纪要放在哪

| 会议 | 放哪 |
|---|---|
| 训练方向的例会 | `project-management/meetings/` |
| GKE、网络方向的例会，以及**全体例会** | `project-management-infra/meetings/` |

全体例会放 infra 仓，因为它是两组客户都能看到的那个仓库（第 2 章 2.4）。

**为什么不放 `wiki`**：`wiki` 是规矩和设计文档，周会的 PR 会淹掉规矩的 PR；纪要和 slides 分在两处要靠链接互找。

## 11.2 目录和文件

**每次会议一个目录：`YYYY-MM-DD-<方向>-<主题>/`**，方向用 `training`、`gke`、`network`，几个方向一起开的用 `all`；主题用英文短横线。

```
meetings/
├── README.md
├── _template/
│   └── notes.md
├── 2026-04-07-training-issue-review-and-precision/
│   ├── notes.md
│   └── slides.pdf
└── 2026-04-14-all-monthly-sync/
    ├── notes.md
    ├── slides-training.pdf
    └── slides-gke.pdf
```

- **目录名排序就是时间顺序，不另外维护索引表**
- `notes.md`：纪要，**必须有**，照模板写。文件名就叫 `notes.md`（不是 `note.md`、`纪要.md`）
- `slides.pdf`：会上**实际讲过、可以给客户的版本**，没有就不放；一次会议有几份就按 `slides-<主题>.pdf` 命名
- 单个文件不超过 20 MB，超过先压缩。PDF 直接提交，不用 LFS（第 10 章）

## 11.3 纪要模板

```markdown
# 训练例会 YYYY-MM-DD：<主题>

- 参会：厂商 <GitHub 账号…>；客户 <GitHub 账号…>
- slides：[slides.pdf](slides.pdf)
<!-- 没有 slides 删掉上一行；有几份就逐个列出 slides-<主题>.pdf -->

## 结论

<!-- 一条一行，每条链到 issue；同一条结论当天也写成该 issue 的评论 -->
- <结论>（northpeak/<project-management 或 project-management-infra>#N）

## 待办

<!-- 有 issue 的写 issue 号，负责人看 issue 的 assignee，这里不重复写；没有 issue 的写负责方和时间，不强制建 issue -->
- [ ] <要做的事> — northpeak/<project-management 或 project-management-infra>#N
- [ ] <要做的事>：<负责方>，<时间>

## 讨论要点

<!-- 可选：没有形成结论、但以后可能要查的内容 -->
```

参会人写 **GitHub 账号**，不写真名：账号能 @，真名不行；客户员工的真名属于客户数据，不该到处出现。不知道就写「未确认」，不要猜。

## 11.4 规矩

**纪要只做索引，事情在 issue 里。**

- **每条结论写回对应 issue 的评论（当天）。** 纪要里的结论是索引，issue 里的评论才是记录
- **结论写全，不只贴链接**：不是每位读者都打得开所有链接
- **待办有对应 issue 的写上 issue 号**；不强制每条待办都建 issue，没有 issue 的写明负责方和时间
- 待办的负责人**看 issue 的 assignee，纪要里不重复写**——重复写的两处迟早不一致

**为什么纪要只是索引**：纪要是按时间组织的，issue 是按问题组织的。三个月后有人查「cp 的 loss 偏差最后怎么定的」，
他会去翻 issue，不会去翻十份纪要。结论只在纪要里，就等于找不到。

## 11.5 提交：走 PR，`Refs` 例会记录 issue

每个方向有一条**例会记录 issue**，置顶：

| 仓库 | issue | 标签 |
|---|---|---|
| `project-management` | 「训练例会记录」 | `type/docs`，置顶 |
| `project-management-infra` | 「基础设施例会记录」 | `type/docs`，置顶 |

例会记录 issue 的正文：

```markdown
### 目标

记录训练与推理方向的例会。每次会议的纪要与 slides 放本仓库的 `meetings/YYYY-MM-DD-training-<主题>/`；
纪要 PR 正文 `Refs` 本 issue，合并后本 issue 的时间线上就留下每次会议的链接。

会上的结论写回对应 issue，待办各自有 issue；本 issue 不讨论具体问题。对纪要的更正可以评论在这里。
```

**纪要 PR 的关联行写 `Refs <org>/<仓库>#<例会记录 issue 号>`，不要写 `Closes`**——写了合并时会把例会记录 issue 关掉。
PR 一开，记录 issue 的时间线上就有这次会议的链接。几个方向一起开的会，`Refs` 两条都写。

PR 模板里在关联行下面加一句注释提醒：「纪要 PR 关联例会记录 issue，保持 Refs，写 Closes 会在合并时把它关掉。」

**例会记录 issue 建议一直开着**（本书的建议）：它不是待办，是时间线，关了以后纪要 PR 的 `Refs` 照样会挂上去，但在 issue 列表里就找不到它了。原项目在交付物目录迁移那天把两条都关了，之后的纪要 PR 仍然 `Refs` 它们。

## 11.6 更正

- 客户要更正：在例会记录 issue 或对应 issue 下评论
- 厂商改好后**另提一个 PR**，不改写已合并的历史

**slides 按会上展示的版本存档，原文件不改。** slides 里有错的，在 `notes.md` 里加一节「勘误」：

```markdown
## 勘误

slides 按会上展示的版本存档，原文件不改：

- 第 1 页议程 02 的「Overlay」应为「Overlap」。
- 第 2 页写「6 个问题」，表里列了 7 个。
- 第 9 页：解决方案标题照抄了第 8 页的分支和提交，应为 `fix/19-zero1-multihost-reshard`；
  这个分支已由 northpeak/maxtext#40 合入后删除，修复看该 PR。
```

为什么不改 slides：会上大家看到的就是那一版。改了之后，「会上说的第 9 页」就对不上了。

## 11.7 不写什么

- **商务、价格和排期**（排期属于交付治理，不进工程 org；会上讲过的技术里程碑可以留）
- **厂商内部材料**
- **没给客户看过的 slides**

会上讲过的技术里程碑（如 POC 各阶段的时间窗）可以留。

## 11.7.1 几个写法细节（来自原项目的纪要）

- **时间写明时区**。双方不在一个时区时尤其要写
- 自动转写分不清人时，**发言人至少分到公司**（「厂商：」「客户：」），比张冠李戴好
- 双方母语不同的，可以另附一份英文版 `notes_en.md`，以中文版为准写在开头

## 11.8 会议录音转写的纪要

很多会议有自动转写或 AI 纪要。可以用，但：

- **必须人工校对**，纪要开头写「记录：自动转写，已人工校对」
- **核对说话人**。自动转写的说话人标注经常错（把 A 的话记成 B 说的），涉及结论和承诺的段落逐句核对
- 转写原文不放进 `meetings/`（太长、有大量口语和误识别），整理成模板格式后放
- 转写里的**专有名词**（组件名、参数名）最容易错，按代码里的写法改
- 会上没形成结论的，「结论」一节写「未确认（会上没有记录结论）」，不要从讨论里推一个结论出来

## 11.9 会后：从纪要到 issue

会后当天要做的：

1. 写 `notes.md`，提 PR，`Refs` 例会记录 issue
2. 每条结论写成对应 issue 的评论
3. 会上产生的新问题：**只为讨论过的、重要的建 issue**（第 6 章 6.5「不要建太多 issue」）。会上一份清单五十条，不等于要建五十条 issue
4. 新建的 issue 可以先统一分给一个熟悉全局的人，由他再路由
5. 在聊天群里发一句话：纪要和 issue 在哪

一份会后发给客户的消息样例：

> 今天会上讨论的问题已经建成 issue，训练方向在 https://github.com/northpeak/project-management/issues ，
> GKE 和网络方向在 https://github.com/northpeak/project-management-infra/issues 。
> 纪要在 project-management-infra 的 `meetings/2026-04-14-all-monthly-sync/`。有补充直接在对应 issue 下评论。

## 11.10 复刻清单

- [ ] 两个 issue 仓各建 `meetings/README.md`、`meetings/_template/notes.md`
- [ ] 建两条例会记录 issue，置顶（`gh issue pin`）
- [ ] PR 模板的关联行下加「纪要 PR 保持 Refs」的注释
- [ ] 第一次例会后照流程走一遍，作为后面的样板
