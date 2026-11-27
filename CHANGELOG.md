# 集合仓变更记录

各 skill 的功能变更记录在各自目录内：`skills/pr-contributor/CHANGELOG.md`、`skills/release-sync/CHANGELOG.md`。本文件只记集合仓层面的结构性变更。

## [1.0.0] - 2026-11-27

- 新建 `webkubor/dev-skills` 集合仓，收纳 `pr-contributor`（v0.2.0）与 `release-sync`（v0.1.1）两个独立 skill。
- 根层新增统一安装入口 `install.sh <skill>`，底层转发到各 skill 自有安装器，安装器规范源与副本结构不变。
- release-sync 的发版门禁接线脚本 `install.sh` 改名为 `install-version-gate.sh`，与 skill 安装入口区分。
- GitHub Actions 上移到根层 `.github/workflows/`，两份 publish 改用 `pr-contributor-v*` / `release-sync-v*` 独立 tag 前缀。
- 所有指向旧仓库的链接更新为 `webkubor/dev-skills`；旧仓 `pr-contributor-skill`、`release-sync-skill` 删除。
