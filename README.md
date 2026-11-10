# GitOps 金书

**用一个 GitHub org 和一组规则，跑一个客户联合工程项目的全部协作。**
照这本书做，下一个客户的 org 可以在一天内搭起来，第一周就能正常收问题、提 PR、出交付物。

这本书来自一个跑了几个月的真实项目：Google 和一家客户在 GitHub org 里协作，内容涵盖 TPU 上的模型训练与推理、GKE on TPU 和网络。
书里的规则都在那个 org 里实际执行过，改过好几轮，每次改动都有原因。例子已经全部替换成虚构的：
示例 org 叫 `northpeak`，示例模型叫 ModelX，人名、issue 号、commit 号都是编的。

## 这本书给谁看

| 读者 | 读什么 |
|---|---|
| 要给新客户搭 org 的人（account team、项目负责人） | 先读第 1、2 章，再照第 15 章的建站手册一步步做 |
| 在 org 里干活的工程师（厂商一侧、客户一侧） | 先读第 17 章的端到端演练，再读第 6、7 章（issue 和 PR） |
| 不熟 GitHub 的项目负责人 | 先读附录 F（十分钟），再读第 1、2 章 |
| AI 编码助手（Codex、Claude Code、Gemini CLI 等） | 附录 A 的 `AGENTS.md` 模板就是写给你的；第 13 章讲它为什么这样写 |
| 要改规则的人 | 第 8 章（RFC）和第 16 章（规则怎么演进） |

## 一句话原则

> **过程记录本身就是交付物。**
> 三个月后有人问「这个数字怎么测的」「当初为什么这么改」，要能点开一条链接回答，而不是靠谁还记得。

## 目录

**第一部分 · 为什么**

- [前言：这本书解决什么问题](chapters/00-preface.md)
- [第 1 章 设计原则](chapters/01-principles.md)

**第二部分 · 结构：东西放在哪、谁能碰**

- [第 2 章 org 与仓库拓扑](chapters/02-org-and-repos.md)
- [第 3 章 人员、团队与权限](chapters/03-people-and-permissions.md)
- [第 4 章 标签与 issue 模板](chapters/04-labels-and-templates.md)
- [第 5 章 看板](chapters/05-board.md)

**第三部分 · 流程：事情怎么流转**

- [第 6 章 issue 的一辈子](chapters/06-issue-lifecycle.md)
- [第 7 章 分支、提交与 PR](chapters/07-branch-and-pr.md)
- [第 8 章 RFC：大任务和规则变更](chapters/08-rfc.md)
- [第 9 章 上游项目的私有副本](chapters/09-upstream-copies.md)
- [第 10 章 交付物目录：library、recipes、repro](chapters/10-deliverables.md)
- [第 11 章 例会与纪要](chapters/11-meetings.md)
- [第 12 章 数字与证据](chapters/12-numbers.md)（12.3 起是数值类项目的内容，其他项目可跳过）

**第四部分 · 给 AI 助手的规则**

- [第 13 章 AGENTS.md：写给 AI 助手的规则](chapters/13-agents-md.md)
- [第 14 章 脚本与自动化](chapters/14-automation.md)

**第五部分 · 落地**

- [第 15 章 建站手册：从零搭一个 org](chapters/15-bootstrap.md)
- [第 16 章 规则怎么演进：几次真实改版](chapters/16-evolution.md)
- [第 17 章 端到端演练：一个问题从提出到关闭](chapters/17-walkthrough.md)
- [第 18 章 运营节奏](chapters/18-operations.md)
- [第 19 章 踩过的坑](chapters/19-pitfalls.md)

**附录**

- [附录 A `AGENTS.md` 完整模板](appendix/A-AGENTS.md)
- [附录 B 模板文件清单](appendix/B-templates.md)（文件本身在 [`appendix/templates/`](appendix/templates/)）
- [附录 C 脚本](appendix/C-scripts.md)（文件本身在 [`appendix/scripts/`](appendix/scripts/)）
- [附录 D 检查清单](appendix/D-checklists.md)
- [附录 E 术语表](appendix/E-glossary.md)
- [附录 F GitHub 速成](appendix/F-github-primer.md)：不熟 issue 表单、Projects、sub-issue 的先读这一页

## 怎么用这本书复刻

1. 读第 1 章，确认这套原则适合你的项目（不适合的情形在第 1 章末尾）
2. 照第 15 章，把占位符（`<org>`、`<客户>`、领域划分）换成你的，逐步建 org
3. 把 [`appendix/templates/`](appendix/templates/) 和 [`appendix/scripts/`](appendix/scripts/) 整个拷进新 org 的对应仓库
4. 第一个月按第 18 章的节奏运营；规则要改时走第 8 章的 RFC

## 本书的写作状态

见 [STATE.md](STATE.md)。
