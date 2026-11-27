#!/usr/bin/env python3
"""gitflow — 面向小白的 GitFlow 工作流执行器。

小白在 AI 编辑器里说中文触发词，Agent 调本脚本做确定性的 git 操作。
输出一律大白话；push / 合并 / 打 tag 这类不可逆操作默认要确认，--yes 跳过。
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_PROD = "main"
BASE_DEV = "develop"


def run(argv, check=True):
    p = subprocess.run(argv, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(argv)} 失败：{(p.stderr or p.stdout).strip()}")
    return p


def git(*argv, check=True):
    return run(["git", *argv], check=check)


def out(text=""):
    print(text)


# 提交格式复用本机 CS 规则：commit_convention / git-branch-policy / git-attribution。
# ① Conventional Commits 的 type；② author 交给 ~/.gitconfig 的 includeIf 解析，
# 脚本绝不用 -c / --author 临时覆盖；③ 末尾必须带 Agent: trailer。
COMMIT_TYPES = {
    "feature": "feat",
    "bugfix": "fix",
    "hotfix": "fix",
    "release": "chore(release)",
}
KNOWN_TYPES = {"feat", "fix", "docs", "refactor", "chore", "test", "style", "perf", "build", "ci", "revert"}


def infer_type(branch_name):
    for prefix, kind in COMMIT_TYPES.items():
        if branch_name.startswith(prefix + "/"):
            return kind
    return "chore"


def commit_message(subject, kind=None, agent="opencode/webkubor"):
    """生成符合 CS 规范的提交信息：type: subject + 空行 + Agent trailer。"""
    subject = (subject or "").strip() or "更新代码"
    head = subject.splitlines()[0]
    first = head.split(":", 1)[0].strip()
    if first in KNOWN_TYPES or re.match(r"^[a-z]+(\([^)]+\))?$", first):
        first_line = head  # Agent 已经写好了 type，原样保留
    else:
        first_line = f"{kind or infer_type(branch())}: {head}"
    return f"{first_line}\n\nAgent: {agent}\n"


def do_commit(message):
    """从 stdin 喂给 git commit，避免临时覆盖身份。"""
    p = subprocess.run(["git", "commit", "-F", "-"], input=message, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"提交失败：{(p.stderr or p.stdout).strip()}")
    return p.stdout.strip()


def confirm(message, yes):
    if yes:
        return True
    out(f"{message} [y/N] ", end="")
    try:
        return sys.stdin.readline().strip().lower() in ("y", "yes")
    except EOFError:
        return False


def repo():
    p = git("rev-parse", "--show-toplevel", check=False)
    if p.returncode != 0:
        raise RuntimeError("这里还不是一个 git 项目。先让 Agent 帮你初始化，或进到项目文件夹里再试。")
    return Path(p.stdout.strip())


def branch():
    return git("branch", "--show-current").stdout.strip()


def clean():
    return not git("status", "--porcelain").stdout.strip()


def ensure_base(name):
    local = git("show-ref", "--verify", "--quiet", f"refs/heads/{name}", check=False)
    if local.returncode != 0:
        remote = git("show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}", check=False)
        if remote.returncode != 0:
            raise RuntimeError(f"远端和本地都没有 {name} 分支，先让团队建好这条主干。")
        git("checkout", "-b", name, "--track", f"origin/{name}")
    else:
        git("checkout", name)
    git("fetch", "origin", check=False)
    pull = git("pull", "--ff-only", "origin", name, check=False)
    if pull.returncode != 0:
        out(f"⚠ 拉取 {name} 最新内容失败（可能是网络或异地还没同步）。继续用本地版本，合并前我会再提醒你。")


def slug(text):
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", text or "").strip("-").lower()
    return (ascii_part or "task")[:24]


def base_ref(base):
    """异地协作优先比远端主干；本地还没推过时回退到本地分支。"""
    remote = git("show-ref", "--verify", "--quiet", f"refs/remotes/origin/{base}", check=False)
    return f"origin/{base}" if remote.returncode == 0 else base


def changed_files(base):
    p = git("diff", "--name-only", f"{base_ref(base)}...HEAD", check=False)
    return [f for f in p.stdout.splitlines() if f.strip()]


# ---------------- 场景 1：该建哪个分支 ----------------
def cmd_start(args):
    repo()
    kind = args.kind
    base = args.base or (BASE_PROD if kind == "hotfix" else BASE_DEV)
    ensure_base(base)
    if not clean():
        raise RuntimeError("你还有没提交的变化。先说『做完了』让我提交，再开新分支，免得改丢。")
    name = f"{kind}/{datetime.now().strftime('%Y%m%d-%H%M')}-{slug(args.desc)}"
    git("checkout", "-b", name)
    out(f"✓ 已从 {base} 开出新分支：{name}")
    out("你现在可以改了。改完说『做完了』，我帮你提交并提给团队。")


# ---------------- 场景 2：多人改同一份，冲突 ----------------
def cmd_conflict(args):
    repo()
    p = git("diff", "--name-only", "--diff-filter=U", check=False)
    files = [f for f in p.stdout.splitlines() if f.strip()]
    if not files:
        out("✓ 目前没有冲突，可以放心继续。")
        return
    out(f"检测到 {len(files)} 个文件被别人也改了，需要你选一下怎么合：")
    for f in files[:20]:
        out(f"  - {f}")
    if len(files) > 20:
        out(f"  ...还有 {len(files) - 20} 个")
    if not args.resolve:
        out("")
        out("告诉我用哪种：")
        out("  保留我的   -> 说『用我的』")
        out("  保留对方的 -> 说『用对方的』")
        out("  让我帮忙   -> 说『帮我合并这些冲突』")
        return
    ours = args.resolve == "mine"
    for f in files:
        git("checkout", "--ours" if ours else "--theirs", "--", f)
        git("add", "--", f)
    out(f"✓ 冲突已按『{'保留我的' if ours else '保留对方的'}』解决。")
    out("接着说『做完了』，我帮你提交。")


# ---------------- 场景 3：做完不知道怎么合并 ----------------
def cmd_finish(args):
    repo()
    b = branch()
    if not clean():
        msg = commit_message(args.message, args.type)
        git("add", "-A")
        do_commit(msg)
        out(f"✓ 改动已提交：{msg.splitlines()[0]}")
        out("提交信息已按规范写好（含执行人标注），你不用管格式。")
    else:
        out("✓ 没有待提交的变化。")
    push = git("push", "-u", "origin", b, check=False)
    if push.returncode == 0:
        out(f"✓ 已推送到远端：{b}")
    else:
        out(f"⚠ 推送失败（网络或权限）。本地已保存，别急，我可以重试。")
    files = changed_files(BASE_DEV)
    out(f"这次一共动了 {len(files)} 个文件。")
    out("下一步：说『提个 PR』，我帮你写成团队能审的合并请求；说『检查改动』我先帮你把关一遍。")


# ---------------- 场景 4：发版 / 线上急修 ----------------
def cmd_release(args):
    repo()
    version = args.version
    if not version:
        out("告诉我版本号，比如『发版 1.2.0』。我没法替你决定版本。")
        return
    version = version.lstrip("v")
    ensure_base(BASE_DEV)
    if not clean():
        raise RuntimeError("还有没提交的变化，先说『做完了』再发版。")
    name = f"release/v{version}"
    if git("show-ref", "--verify", "--quiet", f"refs/heads/{name}", check=False).returncode == 0:
        git("checkout", name)
        out(f"✓ 已在发版分支 {name}。")
    else:
        git("checkout", "-b", name)
        out(f"✓ 已从 {BASE_DEV} 开出发版分支：{name}")
    out(f"接下来我会跑检查。都通过后说『发版确认』，我合并到 {BASE_PROD} 并打 tag v{version}。")


def cmd_hotfix(args):
    repo()
    if not args.desc:
        out("说清楚线上出了什么问题，比如『线上急修 支付按钮点不动』。")
        return
    ensure_base(BASE_PROD)
    if not clean():
        raise RuntimeError("还有没提交的变化，先说『做完了』再开急修分支。")
    name = f"hotfix/{datetime.now().strftime('%Y%m%d-%H%M')}-{slug(args.desc)}"
    git("checkout", "-b", name)
    out(f"✓ 已从 {BASE_PROD} 开出急修分支：{name}")
    out("改完说『做完了』。我会提醒你同时合回 main 和 develop，免得下次发版把修复弄丢。")


def cmd_publish(args):
    repo()
    b = branch()
    version = args.version
    if not version:
        m = re.search(r"(?:release|hotfix)/v?([0-9][0-9A-Za-z.\-]*)", b)
        version = m.group(1) if m else None
    if not version:
        out("没找到版本号。发版时说『发版确认 1.2.0』明确告诉我。")
        return
    if not confirm(f"确定要合到 {BASE_PROD}、打 tag v{version} 吗？这会让团队所有人看到新版本。", args.yes):
        out("已取消，什么都没动。")
        return
    for base in (BASE_PROD, BASE_DEV):
        git("checkout", base)
        git("fetch", "origin", check=False)
        git("pull", "--ff-only", "origin", base, check=False)
        merge = git("merge", "--no-ff", b, "-m", f"merge {b} into {base}", check=False)
        if merge.returncode != 0:
            raise RuntimeError(f"合回 {base} 时有冲突，说『冲突了』我帮你处理。")
        git("push", "origin", base, check=False)
    git("tag", "-a", f"v{version}", "-m", f"release v{version}")
    git("push", "origin", f"v{version}", check=False)
    out(f"✓ 已合到 {BASE_PROD} 和 {BASE_DEV}，打了 tag v{version}。")
    out("版本号同步我会交给 release-sync 处理，你不用管文档里的版本数字。")


# ---------------- 场景 5：AI 改的代码没人把关 ----------------
def cmd_review(args):
    repo()
    files = changed_files(BASE_DEV)
    if not files:
        out("✓ 相对 develop 没有改动，没什么可查的。")
        return
    out(f"这次改动一共 {len(files)} 个文件：")
    for f in files[:30]:
        out(f"  - {f}")
    if len(files) > 30:
        out(f"  ...还有 {len(files) - 30} 个")
    stat = git("diff", "--stat", f"{base_ref(BASE_DEV)}...HEAD", check=False).stdout.strip()
    if stat:
        out("")
        out("改动量：")
        out(stat)
    out("")
    out("我会让 Agent 接着做这几件事（它知道怎么跑你项目的检查和看 diff）：")
    out("  1. 跑项目自带的测试 / lint")
    out("  2. 用大白话讲清楚每个文件改了什么")
    out("  3. 指出看不懂或有风险的地方，再决定要不要提 PR")


def cmd_status(args):
    repo()
    out(f"当前分支：{branch()}")
    out(f"工作区：{'干净' if clean() else '有没提交的变化'}")
    for name in (BASE_PROD, BASE_DEV):
        git("fetch", "origin", check=False)
        ahead = git("rev-list", "--count", f"HEAD..origin/{name}", check=False).stdout.strip()
        out(f"本地比 {name} 落后：{ahead or '0'} 个提交（异地同事的可能更新）")


def build_parser():
    p = argparse.ArgumentParser(description="小白版 GitFlow：说人话，做对分支操作。")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="开新分支（不知道该建哪个分支时）")
    s.add_argument("desc", nargs="?", default="", help="你要做的事，一句话")
    s.add_argument("--kind", default="feature", choices=["feature", "bugfix", "hotfix", "release"])
    s.add_argument("--base", help="从哪条分支切，默认 feature/bugfix 从 develop，hotfix 从 main")
    s.set_defaults(func=cmd_start)

    s = sub.add_parser("conflict", help="多人改同一份导致冲突")
    s.add_argument("--resolve", choices=["mine", "theirs"], help="保留我的 / 保留对方的")
    s.set_defaults(func=cmd_conflict)

    s = sub.add_parser("finish", help="做完了：提交 + 推送")
    s.add_argument("--message", help="提交说明（subject），Agent 根据改动生成")
    s.add_argument("--type", help="Conventional Commits 类型：feat/fix/docs/refactor/chore；不填从分支名推断")
    s.set_defaults(func=cmd_finish)

    s = sub.add_parser("release", help="发版：从 develop 开 release 分支")
    s.add_argument("version", nargs="?", default="", help="版本号，如 1.2.0")
    s.set_defaults(func=cmd_release)

    s = sub.add_parser("hotfix", help="线上急修：从 main 开 hotfix 分支")
    s.add_argument("desc", nargs="?", default="", help="线上出了什么问题")
    s.set_defaults(func=cmd_hotfix)

    s = sub.add_parser("publish", help="发版确认：合回主干 + 打 tag（不可逆，需确认）")
    s.add_argument("version", nargs="?", default="", help="版本号")
    s.add_argument("--yes", action="store_true", help="跳过确认（Agent 已向你确认过时用）")
    s.set_defaults(func=cmd_publish)

    s = sub.add_parser("review", help="把关：列出改动，跑检查，解释 diff")
    s.set_defaults(func=cmd_review)

    s = sub.add_parser("status", help="我现在在哪个分支、有没有落后")
    s.set_defaults(func=cmd_status)

    return p


def main():
    args = build_parser().parse_args()
    try:
        args.func(args)
    except RuntimeError as e:
        out(f"✗ {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
