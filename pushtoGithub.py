import subprocess
from pathlib import Path

ADD_TARGET = "."  # "." = all changed files, or use "index.html"

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

def find_repo_path():
    current = Path(__file__).resolve().parent
    for p in [current] + list(current.parents):
        if (p / ".git").exists():
            return p
    raise FileNotFoundError("No Git repository found in this folder or parent folders.")

def has_staged_changes(repo):
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(repo),
        shell=False
    )
    return result.returncode == 1

def main():
    repo = find_repo_path()
    print(f"Using repo: {repo}")

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