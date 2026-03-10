# Test Deployment Guide for Consolidated MkDocs

## Overview

This guide walks through deploying the consolidated MkDocs configuration to a test GitHub Pages site to verify the deployment works correctly before production.

## Current Status

- **Branch**: `3.0.x`
- **Repository**: `petersmythe/geoserver` (fork)
- **Uncommitted changes**: Yes (consolidated MkDocs changes)

## Deployment Strategy

We have two workflow options for test deployment:

### Option 1: Use Existing Test Workflow (mkdocs.yml)

The `.github/workflows/mkdocs.yml` workflow already supports test deployments:
- Triggers on push to branches: `3.0`, `2.28.x`, `migration/**`
- Deploys to GitHub Pages under `{branch-name}/` directory
- Uses `peaceiris/actions-gh-pages@v3` action

### Option 2: Use Main Deployment Workflow (docs-deploy.yml)

The `.github/workflows/docs-deploy.yml` workflow is the production workflow:
- Triggers on push to branches: `main`, `2.28.x`, `3.0.x`
- Uses `mike` for version management
- Deploys to `gh-pages` branch with version directories

## Recommended Approach: Create Test Branch

To avoid interfering with production deployments, create a test branch that triggers the test workflow:

```bash
# Create a test branch from current state
git checkout -b migration/consolidated-mkdocs-test

# Stage all changes
git add -A

# Commit changes
git commit -m "Test deployment: Consolidated MkDocs with navigation tabs

- Unified mkdocs.yml at workspace root
- Removed doc_switcher component
- Enabled Material navigation tabs
- Updated deployment workflows
- Added validation scripts

This is a test deployment to verify the consolidated configuration works correctly."

# Push to origin (your fork)
git push origin migration/consolidated-mkdocs-test
```

## Monitoring the Deployment

1. **Check GitHub Actions**:
   - Go to: https://github.com/petersmythe/geoserver/actions
   - Look for "MkDocs Documentation" workflow run
   - Monitor the build and deployment steps

2. **Expected Workflow Steps**:
   - ✅ Checkout code
   - ✅ Setup Python
   - ✅ Install MkDocs dependencies
   - ✅ Build unified documentation
   - ✅ Prepare GitHub Pages output
   - ✅ Deploy to GitHub Pages (under `migration/consolidated-mkdocs-test/`)

3. **Verify Deployment Success**:
   - Check that all steps complete without errors
   - Verify the `gh-pages` branch is updated
   - Check deployment logs for any warnings

## Accessing the Test Site

Once deployed, the test site will be available at:

```
https://petersmythe.github.io/geoserver/migration/consolidated-mkdocs-test/
```

The structure should be:
```
https://petersmythe.github.io/geoserver/migration/consolidated-mkdocs-test/en/user/
https://petersmythe.github.io/geoserver/migration/consolidated-mkdocs-test/en/developer/
https://petersmythe.github.io/geoserver/migration/consolidated-mkdocs-test/en/docguide/
https://petersmythe.github.io/geoserver/migration/consolidated-mkdocs-test/en/api/
```

## Verification Checklist

After deployment completes, verify:

- [ ] **Deployment Success**: GitHub Actions workflow completed successfully
- [ ] **Site Accessibility**: Test site URL loads without errors
- [ ] **Navigation Tabs**: All four tabs (User Manual, Developer Guide, Documentation Guide, API Reference) are visible
- [ ] **Tab Functionality**: Clicking tabs navigates to correct manuals
- [ ] **URL Structure**: URLs contain `/en/` path component (e.g., `.../en/user/`)
- [ ] **Content Rendering**: Pages render correctly with proper styling
- [ ] **Internal Links**: Navigation within each manual works
- [ ] **Search**: Search functionality works across all manuals
- [ ] **Responsive Design**: Site works on mobile/tablet viewports

## Troubleshooting

### Workflow Doesn't Trigger

**Problem**: Push doesn't trigger the workflow

**Solutions**:
1. Check branch name matches workflow trigger pattern (`migration/**`)
2. Verify changes include files in `doc/**` or `.github/workflows/mkdocs.yml`
3. Check GitHub Actions is enabled for your fork

### Build Fails

**Problem**: MkDocs build step fails

**Solutions**:
1. Check workflow logs for specific error
2. Test build locally: `mkdocs build`
3. Verify all nav paths in mkdocs.yml exist
4. Run validation scripts: `python validate_mkdocs_config.py`

### Deployment Fails

**Problem**: GitHub Pages deployment step fails

**Solutions**:
1. Check GitHub Pages is enabled in repository settings
2. Verify `gh-pages` branch exists
3. Check repository permissions (needs write access)
4. Review deployment action logs

### Site Not Accessible

**Problem**: Deployed site returns 404

**Solutions**:
1. Wait 2-5 minutes for GitHub Pages to update
2. Check GitHub Pages settings: Settings → Pages
3. Verify `gh-pages` branch has content
4. Check deployment directory matches URL path

### Navigation Tabs Missing

**Problem**: Tabs don't appear on deployed site

**Solutions**:
1. Verify `navigation.tabs` is enabled in mkdocs.yml theme features
2. Check browser console for JavaScript errors
3. Verify Material theme version is compatible
4. Test locally with `mkdocs serve`

## Alternative: Local Test with Mike

To test the mike deployment workflow locally without pushing:

```bash
# Install mike if not already installed
pip install mike

# Configure git for local testing
git config user.name "Test User"
git config user.email "test@example.com"

# Create a local gh-pages branch
git checkout --orphan gh-pages-test
git rm -rf .
git commit --allow-empty -m "Initialize test gh-pages"
git checkout 3.0.x

# Deploy with mike to test branch
mike deploy 3.0.x-test --branch gh-pages-test --push

# View locally
mike serve --branch gh-pages-test
```

Then access: http://localhost:8000/3.0.x-test/en/user/

## Next Steps After Successful Test

1. Document any issues found during testing
2. Update task 9.2 with validation results
3. If successful, prepare for production deployment
4. If issues found, fix and re-test

## Rollback Plan

If the test deployment reveals issues:

```bash
# Switch back to 3.0.x branch
git checkout 3.0.x

# Delete test branch locally
git branch -D migration/consolidated-mkdocs-test

# Delete test branch remotely
git push origin --delete migration/consolidated-mkdocs-test

# Clean up gh-pages test deployment (if needed)
# This requires manual cleanup via GitHub web interface or git commands
```

## Notes

- This is a test deployment to a fork, not production
- The test branch name `migration/consolidated-mkdocs-test` triggers the test workflow
- Production deployment to `geoserver/geoserver` should only happen after successful testing
- Keep the test branch for reference until production deployment is complete
