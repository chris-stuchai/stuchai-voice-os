# Add GitHub Actions Workflow

The CI workflow file was temporarily excluded from the push due to GitHub token permissions.

## Option 1: Add via GitHub UI (Easiest)

1. Go to your repository: https://github.com/chris-stuchai/stuchai-voice-os
2. Click "Add file" → "Create new file"
3. Path: `.github/workflows/ci.yml`
4. Copy the content from `.github/workflows/ci.yml` in your local repo
5. Click "Commit new file"

## Option 2: Update GitHub Token Permissions

Re-authenticate GitHub CLI with workflow scope:

```bash
gh auth refresh -s workflow
```

Then push the workflow file:

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow"
git push origin main
```

## Option 3: Manual Push Later

The workflow file exists locally. Once you have workflow permissions, you can push it:

```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow"
git push origin main
```

---

**Note:** The CI workflow is optional - your repository works fine without it. It just provides automated testing on pushes.

