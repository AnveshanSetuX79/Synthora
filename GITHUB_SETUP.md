# Push to GitHub - Quick Guide

## Prerequisites
- Git installed on your machine
- GitHub account created

## Step-by-Step Instructions

### Step 1: Initialize Git Repository (if not already done)

```bash
# Check if git is already initialized
git status

# If not initialized, run:
git init
```

### Step 2: Create Repository on GitHub

1. Go to [github.com](https://github.com)
2. Click the "+" icon (top right) → "New repository"
3. Fill in:
   - **Repository name:** `localai-leads-platform` (or your preferred name)
   - **Description:** "A marketplace connecting freelancers with local businesses"
   - **Visibility:** Choose Private or Public
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

### Step 3: Add All Files to Git

```bash
# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status

# Commit with a message
git commit -m "Initial commit: LocalAI Leads Platform"
```

### Step 4: Connect to GitHub Repository

```bash
# Replace YOUR_USERNAME and YOUR_REPO with your actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Verify remote was added
git remote -v
```

### Step 5: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# If you get an error about 'master' branch, try:
git branch -M main
git push -u origin main
```

### Step 6: Verify on GitHub

1. Go to your repository URL: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Refresh the page
3. You should see all your files!

---

## Alternative: Using GitHub Desktop (Easier)

### Step 1: Download GitHub Desktop
- Go to [desktop.github.com](https://desktop.github.com)
- Download and install

### Step 2: Add Your Repository
1. Open GitHub Desktop
2. Click "File" → "Add Local Repository"
3. Browse to your project folder
4. Click "Add Repository"

### Step 3: Create Repository on GitHub
1. Click "Publish repository" button
2. Choose name and visibility
3. Click "Publish repository"

Done! Much easier with GitHub Desktop.

---

## Important: Verify .env Files Are NOT Committed

After pushing, check on GitHub that these files are NOT visible:
- ❌ `backend/.env`
- ❌ `frontend/.env`
- ✅ `backend/.env.example` (should be visible)
- ✅ `frontend/.env.example` (should be visible)

If you accidentally committed `.env` files:

```bash
# Remove from git (keeps local file)
git rm --cached backend/.env
git rm --cached frontend/.env

# Commit the removal
git commit -m "Remove .env files from git"

# Push changes
git push
```

---

## Common Issues & Solutions

### Issue: "fatal: not a git repository"
**Solution:**
```bash
git init
```

### Issue: "remote origin already exists"
**Solution:**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Issue: "failed to push some refs"
**Solution:**
```bash
# Pull first, then push
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Issue: Authentication failed
**Solution:**
Use Personal Access Token instead of password:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control)
4. Copy token
5. Use token as password when pushing

Or use SSH:
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Copy your public key:
cat ~/.ssh/id_ed25519.pub

# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

---

## After Pushing to GitHub

### Option 1: Continue with FREE Deployment (No GitHub needed)
Follow `FREE_DEPLOYMENT.md` - upload files directly to Render/Vercel

### Option 2: Deploy from GitHub (Easier updates)

**Render.com with GitHub:**
1. Go to Render.com
2. Click "New +" → "Web Service"
3. Connect GitHub account
4. Select your repository
5. Configure and deploy

**Vercel with GitHub:**
1. Go to Vercel.com
2. Click "Add New..." → "Project"
3. Import from GitHub
4. Select your repository
5. Configure and deploy

**Benefits of GitHub deployment:**
- Automatic deployments on push
- Easy rollbacks
- Better collaboration
- Version control

---

## Quick Commands Reference

```bash
# Check status
git status

# Add files
git add .
git add specific-file.txt

# Commit
git commit -m "Your message"

# Push
git push

# Pull latest changes
git pull

# View commit history
git log

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# View remotes
git remote -v
```

---

## Next Steps

After pushing to GitHub:

1. ✅ Verify all files are on GitHub
2. ✅ Verify .env files are NOT visible
3. ✅ Add repository description
4. ✅ Add topics/tags for discoverability
5. ✅ Consider adding a LICENSE file
6. ✅ Proceed with deployment (FREE_DEPLOYMENT.md)

---

## Repository Settings (Recommended)

On GitHub, go to Settings:

1. **General:**
   - Add description
   - Add website URL (after deployment)
   - Add topics: `fastapi`, `react`, `marketplace`, `leads`

2. **Branches:**
   - Set `main` as default branch
   - Add branch protection rules (optional)

3. **Secrets** (for GitHub Actions):
   - Add environment variables as secrets
   - Use for automated deployments

---

Ready to push! 🚀
