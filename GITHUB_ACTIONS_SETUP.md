# GitHub Actions Setup Guide

This guide will help you set up the complete CI/CD pipeline for your IT Support Chatbot project.

## Prerequisites

1. GitHub repository: `https://github.com/Baglaiev/it-support-chatbot-claude`
2. Anthropic API key
3. Google Drive account (for DVC remote storage)
4. Deployment server (optional, for production deployment)

## Step 1: Repository Setup

1. **Initialize Git repository** (if not already done)
```bash
cd it-support-chatbot-claude
git init
git add .
git commit -m "Initial commit with CI/CD pipeline"
git branch -M main
git remote add origin https://github.com/Baglaiev/it-support-chatbot-claude.git
git push -u origin main
```

## Step 2: Configure GitHub Secrets

Go to your repository settings: `Settings` → `Secrets and variables` → `Actions`

Add the following secrets:

### Required Secrets

1. **ANTHROPIC_API_KEY**
   - Description: Your Anthropic API key for Claude
   - How to get: https://console.anthropic.com/settings/keys
   - Example: `sk-ant-api03-...`

2. **GDRIVE_CREDENTIALS_DATA**
   - Description: Google Drive service account JSON for DVC
   - How to get:
     1. Go to https://console.cloud.google.com
     2. Create a new project or select existing
     3. Enable Google Drive API
     4. Create service account
     5. Download JSON key
     6. Copy entire JSON content as secret value

### Optional Secrets (for deployment)

3. **DEPLOY_SSH_KEY**
   - Description: Private SSH key for deployment server
   - How to generate:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions"
   # Copy content of private key
   cat ~/.ssh/id_ed25519
   ```

4. **DEPLOY_HOST**
   - Example: `example.com` or `192.168.1.100`

5. **DEPLOY_USER**
   - Example: `ubuntu` or `deploy`

6. **DEPLOY_URL**
   - Example: `https://chatbot.example.com`

## Step 3: Setup DVC Remote (Google Drive)

1. **Create Google Drive folder for DVC**
   - Create a folder in Google Drive
   - Share it with the service account email (from step 2)
   - Note the folder ID from URL

2. **Initialize DVC in your repository**
```bash
dvc init
dvc remote add -d origin gdrive://YOUR_FOLDER_ID
git add .dvc .dvcignore
git commit -m "Initialize DVC"
git push
```

3. **Configure DVC credentials locally**
```bash
dvc remote modify origin gdrive_use_service_account true
dvc remote modify origin --local gdrive_service_account_json_file_path service_account.json
```

## Step 4: Prepare Initial Data

1. **Add your IT support documentation**
```bash
# Place PDF files in data/raw/
cp /path/to/your/docs/*.pdf data/raw/

# Process data
python scripts/prepare_data.py
python scripts/create_embeddings.py

# Track with DVC
dvc add data/raw data/processed index_faiss
git add data/*.dvc index_faiss.dvc .gitignore
git commit -m "Add initial data"
dvc push
git push
```

## Step 5: Enable GitHub Actions

1. Go to `Actions` tab in your repository
2. Enable workflows if prompted
3. Workflows should now run automatically on push/PR

## Step 6: Test the Pipeline

### Test CI Workflow

1. Make a small change to code
```bash
echo "# Test" >> README.md
git add README.md
git commit -m "Test CI pipeline"
git push
```

2. Check Actions tab for running workflow
3. Verify all checks pass

### Test Docker Build

1. Push to main branch
```bash
git checkout main
git pull
# Make changes
git push
```

2. Check Actions tab for Docker build
3. Verify image is pushed to GitHub Container Registry

### Test CML Pipeline

1. Update data or model
```bash
# Add new document
cp new_doc.pdf data/raw/
git add data/raw/
git commit -m "Add new documentation"
git push
```

2. Check Actions tab for CML workflow
3. Verify metrics are reported in commit/PR

## Step 7: Setup Monitoring

1. **Enable scheduled monitoring**
   - Monitoring workflow runs daily automatically
   - Check Actions tab for scheduled runs

2. **Manual monitoring trigger**
```bash
# Via GitHub CLI
gh workflow run monitoring.yml

# Or via GitHub UI: Actions → Model Monitoring → Run workflow
```

## Step 8: Production Deployment

### Setup Deployment Server

1. **Prepare server**
```bash
# On your deployment server
sudo apt-get update
sudo apt-get install docker docker-compose git

# Add deploy user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Add SSH key
sudo -u deploy mkdir -p /home/deploy/.ssh
sudo -u deploy echo "YOUR_PUBLIC_KEY" > /home/deploy/.ssh/authorized_keys
```

2. **Clone repository on server**
```bash
sudo -u deploy git clone https://github.com/Baglaiev/it-support-chatbot-claude.git /opt/it-support-chatbot
cd /opt/it-support-chatbot
```

3. **Create environment file**
```bash
sudo -u deploy cp .env.example .env
sudo -u deploy nano .env  # Add ANTHROPIC_API_KEY
```

### Trigger Deployment

1. **Create a release tag**
```bash
git tag -a v1.0.0 -m "First production release"
git push origin v1.0.0
```

2. **Monitor deployment**
   - Go to Actions tab
   - Watch Deploy workflow
   - Check deployment status

## Troubleshooting

### Common Issues

1. **Workflow permissions error**
   - Go to Settings → Actions → General
   - Under "Workflow permissions", select "Read and write permissions"
   - Enable "Allow GitHub Actions to create and approve pull requests"

2. **DVC authentication fails**
   - Verify service account JSON is correct
   - Check folder is shared with service account
   - Test locally: `dvc pull`

3. **Docker build fails**
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Test locally: `docker build -t test .`

4. **Deployment fails**
   - Verify SSH key is correctly configured
   - Check server is accessible
   - Test SSH connection manually

### Getting Help

1. Check workflow logs in Actions tab
2. Review error messages carefully
3. Test commands locally first
4. Create GitHub issue if needed

## Maintenance

### Regular Tasks

1. **Update dependencies**
```bash
pip list --outdated
# Update requirements.txt
git commit -am "Update dependencies"
git push
```

2. **Review monitoring reports**
   - Check daily monitoring runs
   - Review drift alerts
   - Update model if needed

3. **Backup data**
```bash
# DVC automatically backs up to Google Drive
dvc push
```

4. **Update documentation**
   - Keep README.md current
   - Document new features
   - Update deployment guide

## Next Steps

1. Customize workflows for your needs
2. Add more tests
3. Implement additional monitoring
4. Setup alerting (Slack, email, etc.)
5. Add more deployment environments (staging, QA)

---

For more information, see:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DVC Documentation](https://dvc.org/doc)
- [Docker Documentation](https://docs.docker.com/)
