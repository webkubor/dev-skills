# 集合仓变更记录

各 skill 的功能变更记录在各自目录内：`skills/pr-contributor/CHANGELOG.md`、`skills/release-sync/CHANGELOG.md`。本文件只记集合仓层面的结构性变更。

## [1.1.0] - 2026-11-27

- 新增第三个 skill `gitflow`（v0.1.0）：面向不懂代码的异地团队，把 GitFlow 分支协作包装成中文触发词工作流。覆盖五个场景——开分支、多人冲突、做完合并、发版/急修、AI 改动把关。
- `gitflow` 的提交信息复用本机 CS 真源规范（`commit_convention` / `git-branch-policy` / `git-attribution`）：Conventional Commits + `Agent:` trailer，author 交给 `~/.gitconfig` 解析，绝不用 `-c` / `--author` 临时覆盖。
- 根安装入口新增 `gitflow`；三份安装器副本 hash 一致。

## [1.0.0] - 2026-11-27

- 新建 `webkubor/dev-skills` 集合仓，收纳 `pr-contributor`（v0.2.0）与 `release-sync`（v0.1.1）两个独立 skill。
- 根层新增统一安装入口 `install.sh <skill>`，底层转发到各 skill 自有安装器，安装器规范源与副本结构不变。
- release-sync 的发版门禁接线脚本 `install.sh` 改名为 `install-version-gate.sh`，与 skill 安装入口区分。
- GitHub Actions 上移到根层 `.github/workflows/`，两份 publish 改用 `pr-contributor-v*` / `release-sync-v*` 独立 tag 前缀。
- 所有指向旧仓库的链接更新为 `webkubor/dev-skills`；旧仓 `pr-contributor-skill`、`release-sync-skill` 删除。
