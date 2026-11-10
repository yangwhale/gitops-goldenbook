# repro

本仓库 issue 的复现：issue 里放不下的测试脚本、复现代码、日志。由 Google 和客户共同维护。

- 一个 issue 一个目录：`issues/<issue号>-<英文短横线简述>/`，issue 号就是本仓库的号；issue 里能写清楚的就不建目录
- 目录里的 `README.md` 写清怎么跑、看到了什么；跑出来的产物放 `gs://<POC 桶>/issues/infra-<issue号>/<运行名>/`，不进仓库（`infra-` 前缀不能省：同一个桶里还有别的 issue 按 `issues/<号>/` 存的产物，不加会撞号）
- 在 issue 里引用这里的内容时用 commit permalink（`https://github.com/northpeak/project-management-infra/blob/<commit>/repro/...`），不用分支链接
- 不放客户模型的权重、数据、未授权公开的代码；不放任何一方公司内部的链接、主机名
- 改动走 PR；客户在 issue 里放不下的材料（测试脚本、复现代码、日志）可以直接推到 `issues/<issue号>-<简述>/`，不要求 README
