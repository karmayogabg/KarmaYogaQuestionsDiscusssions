---
name: publishKarmaYogaQuestions
description: Automatically publish and deploy updates to the KarmaYogaQuestionsDiscussions website on GitHub Pages whenever index.html or other assets are updated.
---

# Karma Yoga Questions Publisher Skill (`publishKarmaYogaQuestions`)

This skill automates the deployment of the Karma Yoga Questions & Discussions website to GitHub Pages when local changes are committed.

## Project Details
* **Local Path:** `/home/sabrisatharamanathan/my-project/KarmaYoga`
* **Entry File:** `index.html` & `Karmayoga-Questions-Discussion.html`
* **GitHub Repository:** `git@github.com:karmayogabg/KarmaYogaQuestionsDiscusssions.git`
* **Deploy Target:** GitHub Pages (`main` branch)

## Deploy Workflow

When the user asks to publish or deploy the page, execute the following commands in `/home/sabrisatharamanathan/my-project/KarmaYoga`:

1. **Verify git status & stage changes:**
   ```bash
   git status
   git add .
   ```

2. **Commit changes:**
   ```bash
   git commit -m "Update website content & questions data"
   ```

3. **Push to GitHub:**
   ```bash
   git push -u origin main
   ```

4. **Confirm deployment:**
   * Verify that push completed successfully.
   * Remind user that the site will be live at: `https://karmayogabg.github.io/KarmaYogaQuestionsDiscusssions/`
