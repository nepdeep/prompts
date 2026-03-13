import subprocess
import sys
from pathlib import Path

ADD_TARGET = "."  # "." = all changed files, or set a specific file/folder


def run_git(args, cwd, allow_fail=False):
    result = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        shell=False
    )

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

    if result.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Git command failed: git {' '.join(args)}")

    return result


def find_repo_path(start_path=None):
    current = Path(start_path).resolve() if start_path else Path.cwd().resolve()

    if current.is_file():
        current = current.parent

    for p in [current] + list(current.parents):
        if (p / ".git").exists():
            return p

    raise FileNotFoundError(
        f"No Git repository found in: {current} or its parent folders."
    )


def has_staged_changes(repo):
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(repo),
        shell=False
    )
    return result.returncode == 1


def has_untracked_or_modified_changes(repo):
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(repo),
        text=True,
        capture_output=True,
        shell=False
    )
    return bool(result.stdout.strip())


def main():
    start_path = sys.argv[1] if len(sys.argv) > 1 else None
    repo = find_repo_path(start_path)

    print(f"Using repo: {repo}")

    if not has_untracked_or_modified_changes(repo):
        print("Nothing to commit.")
        return

    commit_message = input("Enter commit message: ").strip()
    if not commit_message:
        print("Commit cancelled: empty message.")
        return

    run_git(["add", ADD_TARGET], repo)

    if not has_staged_changes(repo):
        print("No staged changes to commit.")
        return

    run_git(["commit", "-m", commit_message], repo)
    run_git(["push"], repo)

    print("Done.")


if __name__ == "__main__":
    main()