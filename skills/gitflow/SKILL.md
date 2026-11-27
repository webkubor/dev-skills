---
name: gitflow
description: "不会写代码、不会 git，怎么和异地团队用 AI 一起做项目？说中文就能开分支、解冲突、提交合并、发版和线上急修，不用记任何 git 命令。用 Cursor / Claude Code vibecoding 时：说『开个新功能』从 develop 切分支；『冲突了』处理多人改同一份；『做完了』提交并转成团队能审的 PR；『发版』/『线上急修』走 release/hotfix；『检查改动』让 AI 跑测试并用大白话解释改了什么。不可逆操作先确认。触发词：开个新功能、新建分支、冲突了、合并冲突、做完了、提交代码、提个 PR、发版、上线、线上出问题了、紧急修复、检查改动、看看改了啥、我在哪个分支。"
version: 0.1.0
license: MIT
author: webkubor
category: devops
scope: personal
platforms: [linux, macos, windows]
url: https://github.com/webkubor/dev-skills
trigger:
  - 开个新功能
  - 我要改个东西
  - 新建分支
  - 开个分支
  - 建分支
  - 冲突了
  - 合并冲突
  - 别人也改了
  - 做完了
  - 提交代码
  - 推上去
  - 合进去
  - 提个 PR
  - 提 PR
  - 发版
  - 上线
  - 打个 tag
  - 线上出问题了
  - 线上急修
  - 紧急修复
  - 检查改动
  - 看看改了啥
  - 代码没问题吧
  - 我在哪个分支
  - 当前分支
metadata:
  openclaw:
    tags: [gitflow, 小白, 异地协作, 分支, 冲突, 发版, 急修, vibecoding]
    requires:
      bins: [git, python3]
---

# GitFlow · 小白版

> 给不懂代码的人用。你只管说人话，分支、提交、冲突、发版这些事我来做，做完用大白话告诉你结果。
> 团队异地用 AI 写代码最怕三件事：所有人都改 main、改完不知道怎么合、合出冲突不知道怎么办。这套流程就是防这个的。

## 谁该用

- 不懂 git、不想记命令，用 AI 编辑器（Cursor / Claude Code 等）写代码的人
- 团队异地协作，各自用 AI 改代码，需要一套不乱的分支规矩
- 看不懂 diff、不知道 AI 改得对不对就合了的人

**公司仓有自己流程的，按公司流程走**，这里不替代组织授权和发布门禁。

## 触发词 → 我做什么

| 你说 | 我做 | 底层命令 |
|---|---|---|
| 「开个新功能 登录页」「新建分支 改支付」 | 从 develop 切一条 `feature/日期-名字` 分支，你直接开改 | `gitflow start "<描述>"` |
| 「冲突了」「别人也改了」 | 列出冲突文件，问你保留谁的，然后解决 | `gitflow conflict [--resolve mine\|theirs]` |
| 「用我的」「用对方的」 | 按你选的解决冲突并暂存 | `gitflow conflict --resolve mine\|theirs` |
| 「做完了」「提交代码」 | 提交 + 推送，然后告诉你下一步提 PR | `gitflow finish` |
| 「提个 PR」 | 调用 pr-contributor 把改动写成团队能审的合并请求；描述骨架读 `ticket-copy`（结论/改动面/验证/风险/Refs） | 见 pr-contributor |
| 「发版 1.2.0」「上线」 | 从 develop 开 release 分支，准备检查 | `gitflow release 1.2.0` |
| 「发版确认」 | 合回 main 和 develop、打 tag（先跟你确认） | `gitflow publish --yes` |
| 「线上出问题了 支付按钮点不动」 | 从 main 开 hotfix 分支 | `gitflow hotfix "<问题>"` |
| 「检查改动」「看看改了啥」 | 列改动文件、跑项目检查、用大白话解释 diff | `gitflow review` |
| 「我在哪个分支」 | 告诉你当前分支、有没有没提交的、有没有落后同事 | `gitflow status` |

## 执行规则（Agent 必须遵守）

1. **先听懂场景，再动手。** 触发词只决定走哪条流程；版本号、改了什么、保留谁的这些决定必须来自用户，不要替他编。缺信息就问一句，不要猜。

2. **不可逆操作要先确认。** push、合并到 main、打 tag 会影响整个团队。`publish` 默认会问；Agent 在调它之前**必须先跟用户用大白话确认一次**（「这会让所有人看到新版本，确定吗？」），得到明确同意后才加 `--yes`。

3. **失败要说实话。** 网络断、没权限、冲突没解掉，就说「没做成，卡在哪」，不要说「已完成」。脚本返回非零时把原因翻成大白话告诉用户。

4. **结果要用人话反馈。** 不要贴 git 原始输出或路径流水账。说清楚：做了什么、现在在哪、下一步说什么。

5. **不替用户做决定。** 不自动提交别人的 WIP、不强推、不删别人的分支、不绕过团队评审直接合 main。

## 与后台 skill 的关系

```
gitflow（你面对的）  ── 触发词路由 ──>  分支/提交/冲突/发版动作
        │
        ├── 要提 PR 或核验交付 ──> pr-contributor（后台执行）
        └── 发版要同步版本号 ──> release-sync（后台执行）
```

小白只需要认得 `gitflow` 的触发词；`pr-contributor` 和 `release-sync` 由 Agent 在合适的时候调用，不用你操心。

## 提交信息格式（Agent 自动写，你不用背）

`finish` 生成的提交信息复用本机 CS 真源规范（`commit_convention` / `git-branch-policy` / `git-attribution`）：

```
feat: 加登录页手机号验证

Agent: opencode/webkubor
```

- 第一行是 Conventional Commits 的 `type: subject`，type 从分支名推断（feature→feat、hotfix→fix、release→chore(release)）
- 末行 `Agent:` 标执行工具；**author 由 `~/.gitconfig` 的 `includeIf` 解析，脚本绝不用 `-c` / `--author` 临时覆盖身份**
- 提交后、推送前核对一次 author 与解析身份一致

完整规范见 [references/commit-convention.md](./references/commit-convention.md)，含「接手别人分支前先查改动是否已在 main」等分支纪律。

## 个人 Git 兜底规则（公司规则缺位时生效）

没有公司/项目专属 Git 规则时，分支、提交、身份、合并、清理一律按 [references/git-personal-rules.md](./references/git-personal-rules.md) 执行——这是 webkubor 的个人默认口径，覆盖：分支命名与合法基底、Conventional Commits 中文 subject、author/Agent 署名红线（禁 `-c`/`--author` 临时改身份）、多腿分支不删源、不可逆动作先确认、上线腿收完才清理。**有公司规则的仓（如 ModelGo）以公司规则优先，本兜底不覆盖它们。**

## 快速开始

```bash
# 装进本机各 AI 编辑器（仓库根执行）
bash install.sh gitflow

# 只看会装到哪
bash install.sh gitflow --list

# Agent 实际调用示例（在目标项目目录里）
python3 <本skill目录>/scripts/gitflow.py status
python3 <本skill目录>/scripts/gitflow.py start "登录页" --kind feature
python3 <本skill目录>/scripts/gitflow.py conflict
python3 <本skill目录>/scripts/gitflow.py finish
python3 <本skill目录>/scripts/gitflow.py review
```

## 边界与已知限制

- 需要项目已经有 `main` 和 `develop` 两条主干；没有的话先让团队建好，或让 Agent 帮你初始化。
- `release` / `publish` 走的是标准 GitFlow（main + develop + feature/release/hotfix）。团队用 GitHub Flow（只有 main）时，把「发版」理解为打 tag，不走 release 分支。
- 「帮我合并这些冲突」需要 Agent 读懂两边改动后决定，脚本只负责检测和按选择应用；Agent 判断不了时要如实说，不要瞎合。
- 所有分支名用日期 + 简短英文 slug，中文描述会转成 `task`；这不是缺陷，是为了让 git 分支名在各平台都可用。
