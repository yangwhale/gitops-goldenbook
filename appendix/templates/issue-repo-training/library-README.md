# library

训练方向给客户的成品文档：手册、讲义、课件、技术报告。由 Google 维护。

每份材料一个目录，目录名用英文短横线，里面放正文（HTML / PDF / Markdown）和它用到的图。新材料放进来后在下表加一行。

| 材料 | 目录 | 版本 |
|---|---|---|
| <材料名> | [`<目录>/`](<目录>/)（有在线版的给链接；有简洁版的写「新读者先看简洁版」） | <版本或日期> |
| ModelX 第一代在 TPU v5p 256 芯上预训练 — POC 实施手册 | 在本仓库的 [`recipes/modelx-poc/`](../recipes/modelx-poc/)，这里不重复放 | — |

网页版材料下载仓库后用浏览器打开 `library/<目录>/index.html` 即可离线阅读。

GKE on TPU 与网络方向的材料（集群交付手册、切片调度器、v7x 监控）在 [`project-management-infra/library/`](https://github.com/northpeak/project-management-infra/tree/main/library)。

