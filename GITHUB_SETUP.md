# GitHub Setup Guide

Your repository is initialized locally. Follow these steps to create the GitHub repository:

## Option 1: Using GitHub CLI (Recommended)

If you have GitHub CLI installed:

```bash
# Create repository on GitHub
gh repo create stuchai-voice-os --public --source=. --remote=origin --push

# Or if you want it private:
gh repo create stuchai-voice-os --private --source=. --remote=origin --push
```

## Option 2: Manual Setup

1. **Create repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `stuchai-voice-os`
   - Description: "Voice Operating System for AI-driven property management + automation"
   - Choose Public or Private
   - **Don't** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Connect and push:**
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/stuchai-voice-os.git
   git branch -M main
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` with your GitHub username.

## Option 3: Using SSH

If you prefer SSH:

```bash
git remote add origin git@github.com:YOUR-USERNAME/stuchai-voice-os.git
git branch -M main
git push -u origin main
```

## After Setup

Once pushed, you can:
- View your repo at: `https://github.com/YOUR-USERNAME/stuchai-voice-os`
- CI/CD will run automatically (GitHub Actions workflow is included)
- Connect Railway to GitHub for automatic deployments

## Connect Railway to GitHub (Optional)

1. Go to your Railway project dashboard
2. Navigate to Settings → GitHub
3. Connect your GitHub account
4. Enable automatic deployments from GitHub

