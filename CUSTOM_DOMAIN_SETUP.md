# Custom Domain Setup Guide

This guide covers setting up custom domains for GeoServer documentation on GitHub Pages.

## Overview

Two custom domains are needed:
1. **docs.geoserver.org** → GitHub Pages (new versions: 2.28.x, 3.0.x, 3.1.x, etc.)
2. **docs-archive.geoserver.org** → OSGeo server (archive versions: 2.27.x and earlier)

---

## Part 1: GitHub Pages Custom Domain (docs.geoserver.org)

### Step 1: CNAME File in gh-pages Branch

The GitHub Actions workflow automatically creates the CNAME file. Check the workflow file:

```yaml
# .github/workflows/docs-deploy.yml
- name: Configure custom domain
  if: github.ref == 'refs/heads/main'
  run: |
    git fetch origin gh-pages
    git checkout gh-pages
    echo "docs.geoserver.org" > CNAME
    git add CNAME
    git commit -m "Add CNAME for custom domain" || echo "CNAME exists"
    git push origin gh-pages
```

**Verify CNAME file exists:**
```bash
# Check if CNAME file exists in gh-pages branch
gh api repos/geoserver/geoserver/contents/CNAME?ref=gh-pages
```

Or visit: https://github.com/geoserver/geoserver/blob/gh-pages/CNAME

### Step 2: Configure DNS Records

**Contact:** OSGeo infrastructure team or DNS administrator

**DNS Record to Add:**
```
Type: CNAME
Name: docs.geoserver.org
Value: geoserver.github.io
TTL: 3600 (or default)
```

**Alternative (if CNAME not supported at apex):**
```
Type: A
Name: docs.geoserver.org
Values: 
  185.199.108.153
  185.199.109.153
  185.199.110.153
  185.199.111.153
```

### Step 3: Configure Custom Domain in GitHub

**For geoserver/geoserver repository:**

1. Go to: https://github.com/geoserver/geoserver/settings/pages
2. Under **Custom domain**, enter: `docs.geoserver.org`
3. Click **Save**
4. Wait for DNS check to complete (green checkmark)
5. Enable **Enforce HTTPS** (after DNS propagates)

**For testing on petersmythe/geoserver:**

1. Go to: https://github.com/petersmythe/geoserver/settings/pages
2. Under **Custom domain**, enter: `docs-test.geoserver.org`
3. Click **Save**
4. Configure DNS for `docs-test.geoserver.org` → `petersmythe.github.io`

### Step 4: Wait for DNS Propagation

**Timeline:** 24-48 hours (can be faster)

**Check DNS propagation:**
```bash
# Check if DNS is resolving
nslookup docs.geoserver.org

# Or use online tool
# https://www.whatsmydns.net/#CNAME/docs.geoserver.org
```

### Step 5: Verify Deployment

**Before custom domain (immediate):**
```
https://geoserver.github.io/geoserver/3.0.x/en/user/
```

**After custom domain (after DNS propagation):**
```
https://docs.geoserver.org/3.0.x/en/user/
```

---

## Part 2: Archive Domain (docs-archive.geoserver.org)

### Step 1: Configure DNS for Archive Domain

**Contact:** OSGeo infrastructure team

**DNS Record to Add:**
```
Type: CNAME (or A record)
Name: docs-archive.geoserver.org
Value: [OSGeo server hostname or IP]
```

**Example (if using A record):**
```
Type: A
Name: docs-archive.geoserver.org
Value: [OSGeo server IP address]
```

### Step 2: Configure Web Server on OSGeo

**Apache/Nginx configuration needed on OSGeo server:**

```apache
# Apache VirtualHost example
<VirtualHost *:80>
    ServerName docs-archive.geoserver.org
    DocumentRoot /var/www/geoserverdocs
    
    <Directory /var/www/geoserverdocs>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>

<VirtualHost *:443>
    ServerName docs-archive.geoserver.org
    DocumentRoot /var/www/geoserverdocs
    
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    <Directory /var/www/geoserverdocs>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

### Step 3: Verify Archive URLs

**Test archive version access:**
```
https://docs-archive.geoserver.org/2.27.x/en/user/
https://docs-archive.geoserver.org/2.26.x/en/user/
```

---

## Part 3: Testing Domain (docs-test.geoserver.org)

For testing on petersmythe/geoserver fork:

### Step 1: Configure DNS

**DNS Record:**
```
Type: CNAME
Name: docs-test.geoserver.org
Value: petersmythe.github.io
```

### Step 2: Configure in GitHub

1. Go to: https://github.com/petersmythe/geoserver/settings/pages
2. Under **Custom domain**, enter: `docs-test.geoserver.org`
3. Click **Save**

### Step 3: Update CNAME in Workflow

**For testing fork, update the workflow:**

```yaml
# .github/workflows/docs-deploy.yml
- name: Configure custom domain
  if: github.ref == 'refs/heads/main'
  run: |
    git fetch origin gh-pages
    git checkout gh-pages
    echo "docs-test.geoserver.org" > CNAME  # Change this
    git add CNAME
    git commit -m "Add CNAME for test domain" || echo "CNAME exists"
    git push origin gh-pages
```

### Step 4: Verify Test URLs

```
https://docs-test.geoserver.org/3.0.x/en/user/
https://docs-test.geoserver.org/3.1.x/en/user/
```

---

## Troubleshooting

### Issue: DNS Not Resolving

**Check:**
```bash
nslookup docs.geoserver.org
dig docs.geoserver.org
```

**Solution:**
- Wait 24-48 hours for DNS propagation
- Verify DNS records are correct with DNS provider
- Clear local DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)

### Issue: HTTPS Certificate Error

**Symptoms:** "Your connection is not private" error

**Solution:**
1. Wait 10-15 minutes after DNS propagates for GitHub to issue certificate
2. Verify **Enforce HTTPS** is enabled in GitHub Pages settings
3. If still failing, remove and re-add custom domain in GitHub Pages settings

### Issue: 404 Errors on Documentation Pages

**Check:**
1. Verify gh-pages branch has content: https://github.com/geoserver/geoserver/tree/gh-pages
2. Verify versions.json exists: https://github.com/geoserver/geoserver/blob/gh-pages/versions.json
3. Check GitHub Actions deployment succeeded: https://github.com/geoserver/geoserver/actions

### Issue: Version Selector Not Showing

**Check:**
1. Verify `extra.version.provider: mike` in mkdocs.yml
2. Verify versions.json has multiple versions
3. Clear browser cache and reload

---

## Verification Checklist

### GitHub Pages Domain (docs.geoserver.org)

- [ ] CNAME file exists in gh-pages branch
- [ ] DNS CNAME record configured: docs.geoserver.org → geoserver.github.io
- [ ] Custom domain configured in GitHub Pages settings
- [ ] DNS propagation complete (nslookup resolves correctly)
- [ ] HTTPS certificate issued (green padlock in browser)
- [ ] Documentation accessible at https://docs.geoserver.org/3.0.x/
- [ ] Version selector shows multiple versions

### Archive Domain (docs-archive.geoserver.org)

- [ ] DNS record configured for docs-archive.geoserver.org
- [ ] Web server configured on OSGeo server
- [ ] HTTPS certificate configured (if using HTTPS)
- [ ] Archive versions accessible at https://docs-archive.geoserver.org/2.27.x/
- [ ] Version selector links to archive domain for old versions

### Test Domain (docs-test.geoserver.org)

- [ ] DNS CNAME record configured: docs-test.geoserver.org → petersmythe.github.io
- [ ] Custom domain configured in GitHub Pages settings (fork)
- [ ] CNAME file updated in workflow for test domain
- [ ] Test documentation accessible at https://docs-test.geoserver.org/3.0.x/

---

## DNS Configuration Summary

```
# Primary documentation (GitHub Pages)
docs.geoserver.org          CNAME   geoserver.github.io

# Archive documentation (OSGeo server)
docs-archive.geoserver.org  CNAME   [osgeo-server-hostname]
# OR
docs-archive.geoserver.org  A       [osgeo-server-ip]

# Test documentation (GitHub Pages - fork)
docs-test.geoserver.org     CNAME   petersmythe.github.io
```

---

## Contact Information

**For DNS changes:**
- OSGeo infrastructure team
- GeoServer PSC (for approval)

**For GitHub Pages configuration:**
- Repository administrators with Settings access
- GitHub Actions workflow maintainers

---

## References

- [GitHub Pages Custom Domain Documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [GitHub Pages IP Addresses](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site#configuring-an-apex-domain)
- [Mike Documentation](https://github.com/jimporter/mike)
- [Material for MkDocs Versioning](https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/)
