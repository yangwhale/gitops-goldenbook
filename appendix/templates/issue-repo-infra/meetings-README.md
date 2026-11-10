# 会议纪要与 slides

GKE、网络方向和全体例会的纪要，以及会上讲过的 slides。由 Google 维护。

## 目录

每次会议一个目录，名字是 `YYYY-MM-DD-<方向>-<主题>`，方向用 `gke`、`network`，几个方向一起开的用 `all`；主题用英文短横线。
按名字排序就是按时间排序，所以不另外维护索引表。

目录里放：

- `notes.md`：纪要，必须有，照 [`_template/notes.md`](_template/notes.md) 写
- `slides.pdf`：会上实际讲过、可以给客户的版本，没有就不放；一次会议有几份就按 `slides-<主题>.pdf` 命名
- 单个文件不超过 20 MB，超过先压缩

## 规矩

- **纪要只做索引，事情在 issue 里**。每条结论写回对应 issue 的评论（当天）。待办有对应 issue 的写上 issue 号；不强制每条待办都建 issue，没有 issue 的写明负责方和时间
- 结论写全，不只贴链接：不是每位读者都打得开所有链接
- 提交走 PR，PR 正文的关联行写 `Refs northpeak/project-management-infra#1`（例会记录 issue，建站时第一个建的 issue；不要写 `Closes`，否则合并时会关掉它）
- 客户要更正，在例会记录 issue 或对应 issue 下评论；Google 改好后另提一个 PR，不改写已合并的历史
- 不写：商务和价格；Google 内部材料；没给客户看过的 slides。会上讲过的技术里程碑（如 POC 各阶段的时间窗）可以留
