# webkubor 的 Git 个人兜底规则

> 适用范围：**没有公司/项目专属 Git 规则时的默认口径**。公司仓（ModelGo 等）有 `cs rule repo-ownership` §2 等更具体的规则，那些优先；本文件是个人仓和通用场景的兜底，由 gitflow / pr-contributor 两个 skill 在执行时加载。
> 真源就是本文件；CS 侧的 `commit_convention`、`git-branch-policy`、`git-attribution` 规则与此同步，不分叉。

## 1. 分支

| 场景 | 分支 | 从哪切 |
|---|---|---|
| 新功能 | `feature/<描述>`（个人仓可省 issue 号） | `main`（或团队默认主干） |
| 修 bug | `fix/<描述>` 或 `fix/<iid>-<描述>`（有单时） | `main` 或发现 bug 的分支 |
| 线上急修 | `hotfix/<描述>` | **生产分支**（通常 `main`），绝不从 `test`/`develop` 切 |
| 发版隔离 | `release/vX.Y.Z` | `main` |

- **禁止从集成分支（`test`/`develop`）切任何开发分支**：它们压着多版本未验收内容，基底带脏历史。
- 一个分支只做一件事；两件事不重叠时可以合并同类项一个分支收工，但发版/上线各走各的腿。
- 并发冲突用隔离 worktree 防，不靠“记得别切分支”。

## 2. 提交信息

格式（Conventional Commits，中文 subject）：

```
<type>(<scope>): <一句话说清做了什么>

<为什么这么改；可选，说不清就空着，不硬凑>

Refs <完整单号或 issue 链接，可选>

Agent: <agent-id>
Co-Authored-By: <协作者，可选>
```

- **type**：`feat` / `fix` / `docs` / `refactor` / `chore` / `test` / `perf`；发版用 `chore(release)`。
- **subject**：中文、动词开头、说结果不说过程（“加登录页手机号验证”，不是“修改了几个文件”）；不超过 50 字。
- **Refs**：有任务单就写全（`Refs owner/repo#123`），没单不编造。
- **禁止**：`update`、`修改bug`、`wip` 这类零信息 subject；一个提交塞多件不相关的事。

## 3. 身份与署名（红线）

- **author = 谁要这件事**（你本人）；**Agent trailer = 哪个工具动的手**。AI 执行的提交 author 写你，不是 AI。
- 🔴 **禁止 `git -c user.email=...` 或 `--author` 临时改身份**——推送用你的凭据，签别人的名等于凭据与署名脱钩。
- 身份由 `~/.gitconfig` 的 `includeIf` 按目录自动解析；提交前不放心就核一次：

```bash
git log -1 --format='%ae %an'
```

- amend 前先 `git log -1` 确认改的是**自己的**提交；改写别人的公共历史 = 绝对禁止。

## 4. 合并与推送

- **先验证再推送**：测试/类型检查/构建过不了，不推。
- **PR/MR 描述固定骨架**：结论 / 改动面 / 验证 / 风险与回滚 / Refs。
- **多腿分支不删源**：一条分支要合两次（先 test 后 main）时，先合的那次绝不勾“删除源分支”。
- **别人未提交的改动不碰**：动手前 `git status`，有别人的现场就换 worktree。
- push 前后 `git fetch`，避免把别人的新提交顶掉。

## 5. 不可逆动作先确认

`reset --hard`、`clean -fd`、`push --force`、`filter-branch`、删远端分支——除非是自己刚推的且明确要回退，否则先确认再动。误删用 reflog 找回：`git reflog` → `git branch <名> <SHA>`。

## 6. 收尾

- 上线腿走完（合 main + tag + 部署验证）才删本地分支和 worktree；中途不清理。
- 本地分支合入远端主干后即可删（`git branch -d`，删不掉说明还有没合的，先查再 `-D`）。

---
来源：本机 CS 规则 `commit_convention` / `git-branch-policy` / `git-attribution` 收敛（2026-11-27），实例均来自实际踩坑。
