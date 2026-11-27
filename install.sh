#!/usr/bin/env bash
# dev-skills 统一安装入口：把一个 skill 挂进本机各 Agent 的 skills 目录。
# 底层仍用各 skill 自带的安装器（两者共用同一份规范源），本脚本只做转发。
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "${1:-}" in
  gitflow)
    exec bash "$HERE/skills/gitflow/install.sh" "${@:2}"
    ;;
  pr-contributor)
    exec bash "$HERE/skills/pr-contributor/install.sh" "${@:2}"
    ;;
  release-sync)
    exec bash "$HERE/skills/release-sync/install-skill.sh" "${@:2}"
    ;;
  -h|--help|"")
    echo "用法: ./install.sh <skill> [安装器参数...]" >&2
    echo "" >&2
    echo "  gitflow         小白前台：中文触发词走 GitFlow 分支流程" >&2
    echo "  pr-contributor  后台：个人仓交付 / 上游 PR 贡献" >&2
    echo "  release-sync    后台：发版版本号同步（skill 本体）" >&2
    echo "" >&2
    echo "安装器参数见各 skill 的 README，例如 --list / --copy / --uninstall / --target。" >&2
    echo "" >&2
    echo "注意：给 Node 包接发版门禁是另一件事，用 skills/release-sync/install-version-gate.sh。" >&2
    exit 0
    ;;
  *)
    echo "未知 skill: $1（可选: pr-contributor | release-sync）" >&2
    exit 1
    ;;
esac
