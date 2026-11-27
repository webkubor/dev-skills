# dev-skills

webkubor 的「交付 → 发版」链路 Agent skills 集合仓。一个仓库，三个独立 skill：各自有 `SKILL.md`、版本、触发词和 CI，互不耦合。

> **Git 个人兜底规则真源**：[skills/gitflow/references/git-personal-rules.md](./skills/gitflow/references/git-personal-rules.md)——分支、提交、署名、合并、清理的个人默认口径。公司/项目仓有自己的 Git 规则时以那边优先；没有时走这份兜底，gitflow 与 pr-contributor 执行时都会加载。

| Skill | 解决什么 | 目录 |
|---|---|---|
| **gitflow** | 面向不懂代码的异地团队，把 GitFlow 分支协作包装成中文触发词：开分支、冲突、合并、发版、急修、代码把关，说人话就能用 | [`skills/gitflow/`](./skills/gitflow/) |
| **pr-contributor** | 代码怎么真正落地：个人仓验收到主干并留回执；外部仓从真实信号挖出该改的点，提一个维护者愿意合的 PR | [`skills/pr-contributor/`](./skills/pr-contributor/) |
| **release-sync** | 版本号怎么跟着代码落地：发版时把 `package.json` 的 version 同步进分类台账和 `SKILL.md` frontmatter，不同步就拦下发布 | [`skills/release-sync/`](./skills/release-sync/) |

> `gitflow` 是小白面对的前台；`pr-contributor` 和 `release-sync` 是 Agent 在后台调用的机制，不用使用者操心。

## 安装

从仓库根用统一入口：

```bash
bash install.sh gitflow                 # 小白入口：中文触发词走 GitFlow
bash install.sh pr-contributor          # 后台：交付 / PR 核验
bash install.sh release-sync            # 后台：发版版本号同步
bash install.sh gitflow --list          # 只看会装到哪，不改文件
bash install.sh gitflow --uninstall
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
│   ├── gitflow/                     { SKILL.md, references, scripts/gitflow.py, tests }  ← 小白前台
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

## 文字规范：和 writing-standard-skills 打通

gitflow 产出的 commit 信息、PR 描述和给小白的反馈，都是「写给别人看的文字」，所以不另造一套写法，复用本机另一组写作 skill：

- [`how-to-write`](../writing-standard-skills/skills/how-to-write/SKILL.md) → subject 结论先行、说人话、主动语态、沿用用户原话；反馈自包含，不靠「上文」
- [`ticket-copy`](../writing-standard-skills/skills/ticket-copy/SKILL.md) → PR 描述固定「结论 / 改动面 / 验证 / 风险与回滚 / Refs」骨架，验收写成可执行判据
- [`task-reporting`](../writing-standard-skills/skills/task-reporting/SKILL.md) → 提交、合并、部署、业务验收分开陈述

完整落点在 [`skills/gitflow/references/commit-convention.md`](./skills/gitflow/references/commit-convention.md)。`writing-standard-skills` 是独立仓，这里只引用规范、不复制源码。

## 来源

由 `webkubor/pr-contributor-skill` 与 `webkubor/release-sync-skill` 合并而来（2026-11-27），旧仓已删除。CHANGELOG 与版本历史保留在各 skill 目录内：

- [`skills/pr-contributor/CHANGELOG.md`](./skills/pr-contributor/CHANGELOG.md)
- [`skills/release-sync/CHANGELOG.md`](./skills/release-sync/CHANGELOG.md)

MIT — 见 [LICENSE](./LICENSE)。
