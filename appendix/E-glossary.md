# 附录 E 术语表

| 术语 | 本书里的意思 |
|---|---|
| org | GitHub 组织。一个客户项目一个 org |
| 厂商 / 客户 | 提供技术支持的一方 / 接受支持的一方。原项目的厂商是 Google，规则原文里写作「Google 同事」 |
| 规则仓 | `wiki` 仓库：`AGENTS.md`、守则、RFC、脚本；规矩类 issue |
| issue 仓 | `project-management`、`project-management-infra`：项目 issue 和本方向的交付物目录 |
| 代码仓 | 只收 PR、不开 issue 的仓库：自研工具、上游私有副本 |
| 私有副本 | 上游开源项目在 org 里的私有拷贝（不是 GitHub fork），见 `FORK.md` |
| 长期分叉 / 跟随副本 | 私有副本跟上游的两种方式：主线在我们这边定期同步 / 只留副本、自动跟上游 |
| 兜底仓 | 两个 issue 仓里，收「不属于另一边的其他项目事务」的那一个 |
| 记录类改动 | issue 模板、截图、`AGENTS.md` 同步、客户放进 `repro/` 的材料。在 issue 仓里直接推 `main`，不走 PR |
| 分诊（triage） | 处理新 issue：确认仓库、类型、负责人、大小、优先级，补运行条件 |
| 固定路由 | 某类 issue 固定分给某人，写在 `AGENTS.md` 第 2 节 |
| 总表（tracker） | 打 `tracker` 标签、下挂 sub-issue 的 issue。默认不开 |
| 偏差栏 | PR 模板和 RFC 里的「和原计划的偏差」：原计划 A → 实际 B → 原因；没有写「无」 |
| 数值影响栏 | 代码仓 PR 模板里的一栏：数学不变 / 会改数值 / 升级依赖 |
| RFC | 设计文档，`wiki/docs/rfc/NNNN-*.md`。大任务和规则变更必须写 |
| 非目标 | RFC 里必填的一节：这次明确不做什么 |
| run-ID | 一次固定配置运行的名字，也是产物目录。每个写出去的数字都要附 |
| `card.yaml` | 验证过的复现目录里的运行清单：镜像 digest、代码 commit/sha256、命令、预期输出 |
| permalink | 带 commit 的文件链接（`/blob/<commit>/...`），永远指向那一刻的内容 |
| 例会记录 issue | 每个方向一条，置顶、永不关闭；纪要 PR `Refs` 它，形成会议时间线 |
| 可见性矩阵 | 每个客户组 × 每个仓库，看不看得到 |
| 不对称可见性 | 训练组两边都能看，GKE / 网络组只看 infra 仓 |
| 对账 | 每季度把看板和仓库数据拉一遍，删掉没人用的字段和规矩 |
| `northpeak` / `modelx` | 本书的示例 org 名和示例开发分支名 |
