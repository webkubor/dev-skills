---
name: repo-governance
description: "端到端仓库治理与价值梳理工作流：把「GitHub vs GitLab 归属分流、WT/分支安全清理、cs repo status 价值四维打标、开源成熟度体检」串成一条闭环。触发词：仓库治理、项目梳理、价值梳理、开源还是私有、放 GitHub 还是 GitLab、清理分支和WT、repo governance、repo audit。"
version: 0.1.0
license: MIT
author: webkubor
category: devops
scope: personal
platforms: [linux, macos, windows]
url: https://github.com/webkubor/dev-skills
trigger:
  - 仓库治理
  - 项目梳理
  - 价值梳理
  - 开源还是私有
  - 放 GitHub 还是 GitLab
  - 清理分支和WT
  - repo governance
metadata:
  openclaw:
    tags: [repo-governance, gitflow, opensource, portfolio, cs-repo]
    requires:
      bins: [git, cs]
---

# Repo Governance · 仓库治理与价值梳理

> 不只清技术债务（分支 / WT / 同步），更把每个项目的**价值定位**和 **GitHub / GitLab 归属**一次盘清楚。

## 执行原则（红线）

- **公司仓一律不动**（按真实 `git remote` 判定）：走公司班车制与内网规则（`cs rule repo-ownership` §1-2）。
- **绝不删未落地提交或他人改动**：清理前只以 `origin/<base>` 为基线（`merge-base` + `git cherry`），有 dirty 或未落地提交只记录不强清。
- **`cs repo status` 价值判断不越权乱写**：先依据代码、远端状态、活跃度与商业形态给出证据化建议，确认后再写入 `cs repo status`。

## 五步闭环流程

### 1. 归属分流（先判身份，再动仓库）

读取每个仓库的真实 `git remote get-url origin`：

| 归属类别 | 默认托管平台 | 工作流 |
| :--- | :--- | :--- |
| **个人开源 / 影响力工具** | **GitHub** | `cs flow opensource` + PR/`release` 标签发版闭环 |
| **个人私有 / 商业化 / 内部基建** | **GitLab 私有** | `cs land` 直合 `main` |
| **第三方开源 fork / 上游仓** | 原托管平台 | 标 `blocked-third-party`，只同步不改上游主干 |
| **公司业务仓（ModelGo / Paylinker）** | 公司 GitLab | 仅内网 + 班车制，本流程跳过技术清理 |

### 2. 技术面盘点与安全清理

1. **全量扫描**：排查 `DETACHED HEAD`、无 remote、无 upstream、`dirty` 工作区、`behind`、`ahead`、`[gone]` 分支。
2. **拉齐干净个人主干**：对工作区干净且在 `main` 的 `behind` 个人仓执行 `git pull --ff-only`。
3. **回收已落地分支与 WT**：
   - 独立 worktree 完成后用 `cs land` 合入并自动回收。
   - 存量残留分支用 `cs repo tidy`（内置 `merge-base` + `git cherry` 双判据，自动跳过公司仓/dirty/worktree）。
4. **刷新仓库台账**：执行 `cs repo scan` 更新本地与 GitHub/GitLab 映射（修复改名/迁组织导致的路径漂移）。

### 3. 价值四维梳理（`cs repo status`）

检查 `cs repo status` 中 `commercial` 或 `evidence` 为空（`—`）的仓库，按 4 个维度补齐定位：

- **`rights`**（权属）：`personal` | `own-business` | `blocked-employer` | `blocked-client` | `blocked-third-party` | `unknown-needs-owner-review`
- **`form`**（商业形态）：`paid-service` | `open-source-influence` | `owned-traffic-ip` | `infrastructure` | `own-business`
- **`commercial`**（去留决策）：`commercializing`（继续投入/变现）| `parked`（暂停封存）| `dropped`（归档/下线）
- **`evidence`**（外部验证）：`has-users`（已有真实用户/反馈）| `tried-no-signal`（试过无信号）

### 4. GitHub ↔ GitLab 迁库与开源门禁

- **适合迁入 / 留在 GitHub（公开开源）**：
  - `rights` 为 `personal` 或 `own-business`，无敏感配置/雇主代码；
  - `form` 为 `open-source-influence` 或可独立复用的 `infrastructure`；
  - 上线前过一遍 `project-maturity-audit`（9 维度体检）与 `cs rule open_source_project_baseline`（README 金字塔、品牌资产、LICENSE、CHANGELOG）。
- **适合迁回 / 留在 GitLab（私有）**：
  - `commercializing` 的闭源业务后端、商业变现服务、含私有工作流/个人基建的配置仓；
  - 尚未脱敏或未达开源门禁的实验仓、`parked` / `dropped` 准备归档的仓库。
- **迁库后必做联动**：更新 `cs repo scan`、`~/dev/README.md` 及个人主页 `webkubor/data/projects.json`（避免 404 断链）。

### 5. 收尾输出

按三段式汇报：
1. 本轮已拉齐/清理的仓库与 `cs repo scan` 结果；
2. 价值四维（`cs repo status`）待确认/已更新清单；
3. `GitHub ↔ GitLab` 迁库建议与需人工处理的 `dirty` / `DETACHED` / `dropped` 仓库。
