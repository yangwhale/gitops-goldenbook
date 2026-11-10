# 附录 B 模板文件清单

所有文件在 [`templates/`](templates/) 下，已去标识（示例 org `northpeak`、开发分支 `modelx`）。拷贝后统一替换：

```bash
grep -rl northpeak <目标目录> | xargs sed -i 's/northpeak/<你的 org>/g'
```

## 规则仓 `wiki`

| 模板文件 | 放到 | 说明 | 见 |
|---|---|---|---|
| `AGENTS.md` | `wiki/AGENTS.md`（再同步到各仓库） | 给 AI 助手的规则 | 附录 A、第 13 章 |
| `CLAUDE.md`、`GEMINI.md` | 每个仓库根目录（`.github-private` 除外） | 各一行 `@AGENTS.md` | 第 2 章 2.8、第 13 章 13.2 |
| `wiki/README.md` | `wiki/README.md` | org 管什么、去哪读什么、命名 | 第 2 章 2.5 |
| `wiki/onboarding/project-management.md` | `wiki/docs/onboarding/` | 项目管理守则：每条规矩为什么（给人） | 第 1 章 |
| `wiki/onboarding/working-in-northpeak.md` | `wiki/docs/onboarding/` | 各仓库管什么、客户问题怎么记、怎么改代码；**例子表换成你的样板 issue** | 第 18 章 18.1 |
| `wiki/onboarding/permissions.md` | `wiki/docs/onboarding/` | 四层权限、团队授权表、加人流程 | 第 3 章 |
| `wiki/rfc/template.md`、`wiki/rfc/index.md` | `wiki/docs/rfc/` | RFC 模板和空索引 | 第 8 章 |
| `wiki/code-review.md` | `wiki/docs/best-practices/` | 评审规矩 | 第 7 章 7.7 |
| `wiki/ISSUE_TEMPLATE/*.yml` | `wiki/.github/ISSUE_TEMPLATE/` | 加人／撤人、任务、Bug；`config.yml` 关空白 issue | 第 3 章 3.9 |
| `wiki/CODEOWNERS` | `wiki/.github/CODEOWNERS` | RFC 目录对客户开放评审 | 第 8 章 8.5 |
| `pull_request_template.md` | `wiki/.github/` | 四栏，`Closes #`（同仓库） | 第 7 章 |

## issue 仓（`project-management` 用 `issue-repo-training/`，`project-management-infra` 用 `issue-repo-infra/`）

| 模板文件 | 放到 | 说明 |
|---|---|---|
| `ISSUE_TEMPLATE/*.yml` | `.github/ISSUE_TEMPLATE/` | 训练 7 类、infra 6 类 + `config.yml`（第 4 章） |
| `README.md` | 根目录 | 这里提什么、四个目录、给 AI 助手的一句话 |
| `pull_request_template.md` | `.github/` | 关联行写死本仓库全名；纪要 PR 保持 `Refs` 的提醒 |
| `library-README.md` | `library/README.md` | 索引表（第 10 章 10.1） |
| `meetings-README.md` | `meetings/README.md` | 纪要规矩；**把例会记录 issue 号换成你的**（第 11 章） |
| `recipes-README.md` | `recipes/README.md` | 配方规矩、索引表 |
| `repro-README.md` | `repro/README.md` | 两种材料、`card.yaml` 字段、目录清单（第 10 章 10.3） |
| `../meetings-notes-template-training.md`（训练）／`../meetings-notes-template-infra.md`（infra） | `meetings/_template/notes.md` | 纪要模板 |
| `../meeting-log-issue-training.md`／`../meeting-log-issue-infra.md` | 例会记录 issue 的正文 | 建站时第一个建，所以是 1 号；置顶（第 11 章 11.5） |
| `CODEOWNERS` | `.github/CODEOWNERS` | `recipes/`、`repro/` 加客户子团队（不能写父团队 `customer`，它对 issue 仓没有授权） |

## 代码仓

| 模板文件 | 放到 | 说明 |
|---|---|---|
| `code-repo/README.md` | 根目录 | 不开 issue、去哪提、给 AI 助手的一句话 |
| `code-repo/pull_request_template.md` | `.github/` | 四栏 + 「数值影响」（不涉及数值的项目删掉那一栏，第 7 章 7.8） |
| `code-repo/CODEOWNERS` | `.github/` | 默认 maintainers；客户共同维护的目录加客户团队 |
| `FORK.md` | 上游私有副本的根目录 | 长期分叉的完整样例：分支表、同步规矩、冒烟、同步记录（第 9 章） |

## org 主页

| 模板文件 | 放到 | 说明 |
|---|---|---|
| `org-profile/README.md` | `.github-private/profile/README.md` | 按钮组、划界、模板表、为什么用 issue、正在做、仓库表（第 2 章 2.6） |
| `org-profile/submit-issue.svg`、`view-issues.svg` | 同目录 | 两个按钮图；要改文字直接改 SVG 里的 `<text>` |

## 不再使用但留作参考

| 模板文件 | 说明 |
|---|---|
| `pr-check.yml` | 原来的 GitHub Actions 工作流。org 停用 Actions 后改用 `scripts/pr-check.py`；升级 Team 档、想强制检查时可以恢复（第 14 章 14.3） |
