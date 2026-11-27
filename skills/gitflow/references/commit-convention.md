# 提交怎么写（小白版）

> 取自本机 CS 真源规则：`commit_convention`、`git-branch-policy`、`git-attribution`。
> 你不用背这些，Agent 会按这份规范自动写。这里只是让你知道它为什么这么写。

## 一句话

提交信息长这样：

```
feat: 加登录页手机号验证

Agent: opencode/webkubor
```

第一行说「做了什么类型、什么事」，空一行，最后一行说「是谁/哪个工具动的手」。

## 第一部分：类型（第一行冒号前）

| 类型 | 什么时候用 |
|---|---|
| `feat` | 加了新功能（开新分支做的基本都是这个） |
| `fix` | 修 bug（冲突修复、线上急修归这里） |
| `docs` | 只改文档 |
| `refactor` | 代码改了但功能没变 |
| `chore` | 杂项：配置、依赖、版本号同步 |

Agent 会根据分支名自动推断：
- `feature/*` → `feat`
- `bugfix/*` / `hotfix/*` → `fix`
- `release/*` → `chore(release)`
- 其他 → `chore`

你说「做完了」，Agent 会结合你做的改动写出具体的 subject，不会只写「update」。

## 第二部分：谁交的（最后一行）

Git 里有两个位置，含义完全不同：

- **author（提交人）**：**谁要这件事**。你让 AI 改代码，author 就是你，不是 AI。
- **Agent trailer（执行人）**：**哪个工具动的手**，写在正文末尾 `Agent: opencode/webkubor`。

为什么 author 不能写 AI：推送用的是你的账号凭据，写 AI 的名字等于用你的钥匙、签别人的名，平台会把这条提交显示成无法关联的陌生人，@ 不了也追不了责。

## 三件绝不能做的事（Agent 必须遵守）

1. **不用 `git -c user.email=...` 或 `git commit --author=...` 临时改身份。**
   身份由 `~/.gitconfig` 的 `includeIf` 按目录自动解析，脚本只能读、不能改。
   临时覆盖会让提交关联不到账号——这是实际发生过的事故。

2. **提交后、推送前核对一次**：

   ```bash
   git log -1 --format='%ae' | diff -q - <(git config user.email) >/dev/null \
     && echo "✅ 身份一致" || echo "❌ 身份被覆盖"
   ```

3. **不合没确认的改动。** AI 改完不等于对，先说「检查改动」，看完再提 PR。

## 和 writing-standard-skills 的关系

commit 信息和 PR 描述都是「写给别人看的文字」，所以不另造一套写法，直接复用本机另一组 skill：

| 写作 skill | 用在哪 | 拿什么规范 |
|---|---|---|
| `how-to-write` | commit subject、给小白的反馈 | 结论先行：`feat: 加了什么` 第一行就是结论，不铺过程；说人话、主动语态、沿用用户原话，不另造同义词；最终答案自包含，不依赖「上文」 |
| `ticket-copy` | PR / MR 描述 | 骨架固定为「结论 / 改动面 / 验证 / 风险与回滚 / Refs」，验收写成可执行判据（命令+结果+退出码），不写「看着对」 |
| `task-reporting` | 做完后的回执 | 提交、合并、部署、业务验收分开陈述，不混成一团 |

具体落到 commit 上：

- subject 要能判断终点——「修一下图床」不合格，「fix: 图床路由表漂移，清理错路径恢复 11→7 条映射」合格
- 删掉「显然 / 明显 / 当然」这类空话，不用感叹号和全大写强调
- Agent 写 PR 描述前先读 `ticket-copy` 的 MR/PR 骨架，不要凭印象写

> 这组 skill 在 `~/dev/agent-skills/writing-standard-skills`，是独立仓，不复制源码到这里；本文件只引用它的规范。

## 分支的收尾（合并之后）

改动合进主干后，旧分支要删掉，免得攒一堆僵尸分支：

```bash
git branch --merged origin/main        # 确认真的合进去了
git push origin --delete <branch>      # 删远端
git branch -d <branch>                 # 删本地
```

分支上挂了 worktree 的，先 `git worktree remove <路径>` 再删分支。

## 接手别人的分支前先查一件事

```bash
git fetch origin
git log origin/main -- <改动文件>
```

改动已经在 main 里 → 关掉这个分支别再合，那是重复劳动。
不在 main → 才继续。这条检查放在动手前，能省掉「写完→测完→开 PR→撞冲突→回退」整轮返工。
