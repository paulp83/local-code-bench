"""Shared scoring helpers for the club-3090 agent tasks: tree export, offline test runs, check counting."""
import os, re, subprocess
from pathlib import Path

REPO = Path(os.environ.get("CLUB3090_REPO", "club-3090")).expanduser().resolve()  # a clone of noonghunna/club-3090
IMAGE = "club-tasks-env:1"
UID = f"{os.getuid()}:{os.getgid()}"
TEST_TIMEOUT = 300

# One line = one check. Summary lines ("PASS: 10   FAIL: 5", "FAIL: test-x", "== FAIL ==", "test-x: FAIL") are not checks.
PASS_RE = re.compile(r"^\s*(ok\b|✓|✔|PASS\b(?!:\s*\d)|\[ok\])", re.I)
FAIL_RE = re.compile(r"^\s*(not ok\b|✗|✘|FAIL\b|\[fail\])", re.I)
SUMMARY_RE = re.compile(r"^\s*(PASS:\s*\d+|FAIL:\s*test-|==\s*FAIL\s*==|==\s*PASS\s*==|\S+:\s*(PASS|FAIL)\s*$)", re.I)


def git(*a) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), *a], check=True, capture_output=True).stdout


def export(commit: str, dst: Path, as_repo: bool = False):
    dst.mkdir(parents=True)
    subprocess.run(["tar", "-x", "-C", str(dst)], input=git("archive", commit), check=True)
    if as_repo:
        for c in (["init", "-q"], ["add", "-A"], ["-c", "user.email=a@l", "-c", "user.name=a", "commit", "-qm", "base"]):
            subprocess.run(["git", "-C", str(dst), *c], check=True, capture_output=True)


def put_tests(tree: Path, merge: str, tests: list[str]):
    for t in tests:
        dst = tree / t
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(git("show", f"{merge}:{t}"))


def run_tests(tree: Path, tests: list[str], timeout: int = TEST_TIMEOUT) -> dict:
    """Run test files offline; return {test: {"rc": int, "out": str}} with each test's full output."""
    if not tests:
        return {}
    script = ("set +e; cd /testbed; for t in \"$@\"; do echo \"@@BEGIN $t\"; case $t in *.py) timeout %d python3 $t ;; "
              "*) timeout %d bash $t ;; esac 2>&1 | head -c 200000; echo \"@@RC ${PIPESTATUS[0]} $t\"; done") % (timeout, timeout)
    p = subprocess.run(["docker", "run", "--rm", "--network", "none", "--user", UID, "-e", "HOME=/tmp",
                        "-v", f"{tree}:/testbed", IMAGE, "bash", "-c", script, "_", *tests],
                       capture_output=True, text=True, timeout=timeout * len(tests) + 120)
    res, cur, buf = {}, None, []
    for line in p.stdout.splitlines():
        if line.startswith("@@BEGIN "):
            cur, buf = line[8:], []
        elif line.startswith("@@RC ") and cur:
            _, rc, t = line.split(" ", 2)
            res[t] = dict(rc=int(rc), out="\n".join(buf))
            cur = None
        elif cur:
            buf.append(line)
    for t in tests:
        res.setdefault(t, dict(rc=-1, out=p.stderr[-2000:]))
    return res


TOTALS_RE = re.compile(r"PASS:\s*(\d+)\s+FAIL:\s*(\d+)", re.I)


def count_checks(out: str) -> tuple[int, int]:
    """(passed, failed) checks. A summary line like 'PASS: 12   FAIL: 3' wins when present (some tests print only
    their failures plus the totals); otherwise count one check per ok/✓/PASS or FAIL/✗ line."""
    m = TOTALS_RE.findall(out)
    if m:
        return int(m[-1][0]), int(m[-1][1])
    p = f = 0
    for line in out.splitlines():
        if SUMMARY_RE.match(line):
            continue
        if PASS_RE.match(line):
            p += 1
        elif FAIL_RE.match(line):
            f += 1
    return p, f


def changed_files(patch: str) -> set[str]:
    return set(re.findall(r"^diff --git a/(\S+) b/", patch, re.M))
