# dev-skills

webkubor 的「交付 → 发版」链路 Agent skills 集合仓。一个仓库，两个独立 skill：各自有 `SKILL.md`、版本、触发词和 CI，互不耦合。

| Skill | 解决什么 | 目录 |
|---|---|---|
| **pr-contributor** | 代码怎么真正落地：个人仓验收到主干并留回执；外部仓从真实信号挖出该改的点，提一个维护者愿意合的 PR | [`skills/pr-contributor/`](./skills/pr-contributor/) |
| **release-sync** | 版本号怎么跟着代码落地：发版时把 `package.json` 的 version 同步进分类台账和 `SKILL.md` frontmatter，不同步就拦下发布 | [`skills/release-sync/`](./skills/release-sync/) |

## 安装

从仓库根用统一入口：

```bash
bash install.sh pr-contributor          # 装进本机各 Agent 的 skills 目录
bash install.sh release-sync
bash install.sh pr-contributor --list   # 只看会装到哪，不改文件
bash install.sh release-sync --uninstall
```

也可以进各 skill 目录用它们自己的安装脚本：

```bash
cd skills/pr-contributor && bash install.sh
cd skills/release-sync && bash install-skill.sh
```

底层安装器是同一份规范源（`skills/pr-contributor/scripts/install_skill.py`），各 skill 目录保留自己的副本，由 CI 校验摘要一致。

**注意**：`skills/release-sync/install-version-gate.sh` 不是 skill 安装器——它把发版门禁接进你的 Node 包（`prepublishOnly`）。用法见 [release-sync README](./skills/release-sync/README.md#给-node-包接发版门禁)。

## 结构

```
dev-skills/
├── install.sh                       # 统一安装入口
├── skills/
│   ├── pr-contributor/              { SKILL.md, references, scripts, templates, evals, tests }
│   └── release-sync/                { SKILL.md, scripts, README(.en).md, install-version-gate.sh }
└── .github/workflows/               # 两份 CI + 两份 publish，按 skill 分名
```

## 发布

两个 skill 独立版本、独立 tag，避免互相触发 publish：

```
pr-contributor-vX.Y.Z    → 校验 skills/pr-contributor/SKILL.md 的 version
release-sync-vX.Y.Z      → 校验 skills/release-sync/SKILL.md 的 version
```

## 来源

由 `webkubor/pr-contributor-skill` 与 `webkubor/release-sync-skill` 合并而来（2026-11-27），旧仓已删除。CHANGELOG 与版本历史保留在各 skill 目录内：

- [`skills/pr-contributor/CHANGELOG.md`](./skills/pr-contributor/CHANGELOG.md)
- [`skills/release-sync/CHANGELOG.md`](./skills/release-sync/CHANGELOG.md)

MIT — 见 [LICENSE](./LICENSE)。
