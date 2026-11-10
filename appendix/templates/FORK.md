# northpeak/maxtext

这是 [AI-Hypercomputer/maxtext](https://github.com/AI-Hypercomputer/maxtext) 在 NorthPeak 里的私有副本（不是 GitHub fork：GitHub 上公开仓库的 fork 只能是公开的）。

## 跟上游的方式：长期分叉

客户模型（ModelX 各代）的改动不一定适合进上游，所以主线在我们这边。规矩：

- **每两周把上游 main 合进本仓 `main` 一次**，然后把 `modelx` rebase 到新的 `main` 上，在 CPU 上跑一遍冒烟（见下）再推
- 每次同步后在本文件末尾的「同步记录」表加一行
- rebase 有冲突时逐文件核对，**不要整文件取一边**（<日期> 那次整文件取 ours 丢过模型名白名单，是冒烟测出来的）
- 通用的修复（和客户模型无关的）优先直接提给上游，合进上游后再随同步回来

## 分支

| 分支 | 内容 | 用途 |
|---|---|---|
| `main` | 上游 main + 本 org 的约定文件（AGENTS.md、CLAUDE.md、FORK.md、`.github` 里的模板和 pr-check） | 同步上游的落脚点，不在上面直接开发 |
| `modelx` | `main` + ModelX模型接入（ModelX 第一代 基线起步，ModelX 第二代 及以后各代也在这条线上） | **日常开发从这里拉分支**，PR 合回这里 |
| `modelx-gen1` | ModelX 第一代 基线快照，冻结在 `5d6e7f8` | 只读，不再合 PR。`modelx` 就是从这个提交拉出来的 |
| `modelx-poc` | 原始 POC 代码，提交 `7a7a7a7`（基于 <日期> 的上游） | 只读。v5p POC 手册（`northpeak/project-management` 的 `recipes/modelx-poc/`）里的代码包、sha256 都对应这个提交，复现 POC 结果用它 |

`modelx-gen1` 是 <日期> 从 `modelx-poc` rebase 到当时上游 main 得到的。rebase 记录写在那个提交的说明里：原来 3 个提交，第 1 个上游已自行解决（丢弃），第 3 个并入第 2 个。

## 冒烟（CPU，约 2 分钟，不占 TPU）

```bash
JAX_PLATFORMS=cpu python -m maxtext.trainers.pre_train.train src/maxtext/configs/base.yml \
  run_name=modelx-cpu-smoke base_output_directory=/tmp/out model_name=modelx-smoke override_model_config=True \
  hardware=cpu skip_jax_distributed_system=True dataset_type=synthetic steps=4 per_device_batch_size=1 \
  max_target_length=128 base_emb_dim=256 base_mlp_dim=512 base_moe_mlp_dim=128 num_experts=8 num_experts_per_tok=2 \
  base_num_query_heads=4 base_num_kv_heads=2 head_dim=64 vocab_size=1024 enable_checkpointing=False \
  attention=dot_product sparse_matmul=False megablox=False log_period=1 log_step_diagnostics=True
```

通过标准：4 步都完成、loss 下降、`mtp_loss` 非零、`moe_bias_update_nonzero` 非零（路由偏置在更新）。
<日期> rebase 后的结果：loss 8.4 → 8.2，`mtp_loss` 非零，`moe_bias_update_nonzero` 非零。

**这只证明代码路径能跑通，不证明数值和 POC 一致**。上 TPU 前先跑手册里的 4 层冒烟模型，再和 `modelx-poc` 的结果对比。

## CI

上游的工作流需要上游自己的 runner，在本仓全部停用；只启用 `pr-check`（检查 PR 关联 issue 和偏差栏；动了 `src/` 或依赖的 PR 另核「数值影响」一栏，规矩见 PR 模板与 `northpeak/numerics-kit` 的 `docs/reference/regression.md` 第三节）。

## 同步记录

| 日期 | 上游 commit | `modelx-gen1` | CPU 冒烟 |
|---|---|---|---|
| <日期> | `0f1e2d3c4` | `9e8d7c6b5` | loss 8.4 → 8.2，`mtp_loss` 非零，`moe_bias_update_nonzero` 非零 |
