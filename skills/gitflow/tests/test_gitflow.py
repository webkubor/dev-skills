#!/usr/bin/env python3
"""gitflow 行为测试：用临时 git 仓库跑真实命令，不复刻被测逻辑。"""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "gitflow.py"


class GitflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "tester")
        (self.root / "app.txt").write_text("v1\n")
        self.git("add", "-A")
        self.git("commit", "-m", "init")
        self.git("branch", "develop")

    def git(self, *args):
        p = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"git {' '.join(args)}: {p.stderr}")
        return p.stdout.strip()

    def py(self, *args):
        return subprocess.run(
            ["python3", str(SCRIPT), *args], cwd=self.root, capture_output=True, text=True
        )

    def branch(self):
        return self.git("branch", "--show-current")

    def test_status_reports_branch_in_plain_language(self):
        p = self.py("status")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("当前分支", p.stdout)
        self.assertIn("main", p.stdout)

    def test_start_creates_feature_branch_from_develop(self):
        p = self.py("start", "登录页", "--kind", "feature")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(self.branch().startswith("feature/"), self.branch())
        self.assertIn("feature", p.stdout + self.branch())
        self.assertIn("develop", p.stdout)

    def test_start_hotfix_comes_from_main(self):
        p = self.py("hotfix", "支付按钮点不动")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(self.branch().startswith("hotfix/"), self.branch())
        self.assertIn("main", p.stdout)

    def test_start_refuses_with_uncommitted_changes(self):
        (self.root / "app.txt").write_text("v2\n")
        p = self.py("start", "新功能")
        self.assertEqual(p.returncode, 1)
        self.assertIn("没提交", p.stdout)

    def test_conflict_with_no_conflicts_says_so(self):
        p = self.py("conflict")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("没有冲突", p.stdout)

    def test_finish_commits_and_reports_next_step(self):
        self.py("start", "改东西")
        (self.root / "app.txt").write_text("v2\n")
        p = self.py("finish", "--message", "改了登录页", "--type", "feat")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("提交", p.stdout)
        self.assertIn("提个 PR", p.stdout)
        subject = self.git("log", "-1", "--pretty=%s")
        body = self.git("log", "-1", "--pretty=%b")
        self.assertEqual(subject, "feat: 改了登录页", subject)
        self.assertIn("Agent: opencode/webkubor", body, body)

    def test_commit_author_is_not_overridden(self):
        self.py("start", "改东西")
        (self.root / "app.txt").write_text("v3\n")
        self.py("finish", "--message", "改了一处")
        resolved = subprocess.run(
            ["git", "config", "user.email"], cwd=self.root, capture_output=True, text=True
        ).stdout.strip()
        actual = self.git("log", "-1", "--format=%ae")
        self.assertEqual(actual, resolved, f"author {actual} != 解析身份 {resolved}")

    def test_review_lists_changed_files(self):
        self.py("start", "改东西")
        (self.root / "new.txt").write_text("new\n")
        self.git("add", "-A")
        self.git("commit", "-m", "add new")
        p = self.py("review")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("new.txt", p.stdout)

    def test_release_requires_version(self):
        p = self.py("release")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("版本号", p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
