---
name: updatePublishKYPage
description: Automatically commit updates and publish the Karma Yoga Questions, Discussion Manager, and Transcripts website to GitLab and GitLab Pages.
---

# Karma Yoga GitLab Publisher Skill (`updatePublishKYPage`)

This skill automates the deployment of the Karma Yoga Questions, Answers, and Transcripts website to GitLab and GitLab Pages.

## Project Specifications
* **Workspace Path**: `/home/sabrisatharamanathan/my-project/KarmaYoga`
* **Primary HTML App**: `index.html``Karmayoga-Questions-Discussion.html`
* **Backend Database**: `questions_data.json`
* **CI/CD Config**: `.gitlab-ci.yml` (Configured for GitLab Pages)

---

## Skill Execution Workflow

When the user invokes `/updatePublishKYPage` or asks to publish updates to GitLab:

### Step 1: Run Automated GitLab Publisher Script

Run the automated Python script provided in the skill `scripts/` directory:

```bash
python3 /home/sabrisatharamanathan/.gemini/antigravity-cli/skills/updatePublishKYPage/scripts/publish_gitlab.py --remote "gitlab"
```

Optional arguments:
* `--remote <remote_name>`: Specify custom git remote name (default: `gitlab`).
* `--url <gitlab_url>`: Specify GitLab repository SSH/HTTPS URL if remote is not set yet.
* `--message "<commit_message>"`: Custom commit message.

---

### Step 2: Manual Terminal Commands (Alternative)

If executing git commands manually:

```bash
cd /home/sabrisatharamanathan/my-project/KarmaYoga

# 1. Stage updated files
git add .

# 2. Commit changes
git commit -m "Publish updates to GitLab Pages"

# 3. Add gitlab remote if not present (example)
# git remote add gitlab git@gitlab.com:<username>/KarmaYogaQuestionsDiscussions.git

# 4. Push to GitLab
git push gitlab main
```

---

## DeliverablesVerification Checklist
- Verify `.gitlab-ci.yml` is present in the workspace.
- Confirm `git push gitlab main` completes with exit code 0.
- Output the live GitLab Pages link to the user.
