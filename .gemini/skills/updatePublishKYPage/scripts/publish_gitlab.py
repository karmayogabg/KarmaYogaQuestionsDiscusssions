#!/usr/bin/env python3
"""
GitLab Publisher Script for Karma Yoga Project
Automates staging, committing, setting up GitLab git remotes, and pushing to GitLab / GitLab Pages.
"""

import os
import sys
import subprocess
import argparse

WORKSPACE_DIR = "/home/sabrisatharamanathan/my-project/KarmaYoga"

def run_cmd(cmd, cwd=WORKSPACE_DIR):
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if res.stdout:
        print(res.stdout)
    if res.stderr and res.returncode != 0:
        print(f"Error: {res.stderr}")
    return res

def main():
    parser = argparse.ArgumentParser(description="Publish Karma Yoga project to GitLab")
    parser.add_argument("--remote", default="gitlab", help="Git remote name (default: gitlab)")
    parser.add_argument("--url", help="GitLab repository URL (e.g. git@gitlab.com:username/karmayoga.git)")
    parser.add_argument("--message", default="Publish updates to GitLab Pages", help="Commit message")
    args = parser.parse_args()

    os.chdir(WORKSPACE_DIR)

    # 1. Ensure .gitlab-ci.yml exists
    ci_file = os.path.join(WORKSPACE_DIR, ".gitlab-ci.yml")
    if not os.path.exists(ci_file):
        with open(ci_file, "w", encoding="utf-8") as f:
            f.write("""pages:
  stage: deploy
  script:
    - mkdir .public
    - cp -r * .public 2>/dev/null || true
    - mv .public public
  artifacts:
    paths:
      - public
  only:
    - main
""")
        print("Created .gitlab-ci.yml configuration for GitLab Pages.")

    # 2. Stage changes
    run_cmd("git add .")

    # 3. Commit if there are staged changes
    status_res = run_cmd("git status --porcelain")
    if status_res.stdout.strip():
        run_cmd(f'git commit -m "{args.message}"')
    else:
        print("No new changes to commit.")

    # 4. Handle GitLab Remote
    if args.url:
        # Check if remote exists
        remotes = run_cmd("git remote").stdout.splitlines()
        if args.remote in remotes:
            run_cmd(f"git remote set-url {args.remote} {args.url}")
        else:
            run_cmd(f"git remote add {args.remote} {args.url}")
        print(f"Configured remote '{args.remote}' -> {args.url}")

    # 5. Push to GitLab
    push_res = run_cmd(f"git push {args.remote} main")
    if push_res.returncode == 0:
        print("Successfully published to GitLab!")
    else:
        print("Push failed or remote not configured yet. Make sure to specify --url <gitlab_repo_url>.")

if __name__ == "__main__":
    main()
