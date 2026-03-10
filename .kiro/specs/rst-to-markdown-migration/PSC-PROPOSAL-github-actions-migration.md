---
**GSIP 240 - GitHub Actions for Documentation Deployment**

---

## Overview

Migrate GeoServer documentation builds from Jenkins to GitHub Actions following the approved GSIP 221 (MkDocs Migration). Jenkins can continue building after RST removal with additional reconfiguration work, but GitHub Actions provides superior maintainability through version-controlled configuration and eliminates SSH credential management.

**Key Benefits:**
- **Version-controlled configuration:** YAML in Git (reviewable, auditable) vs Jenkins UI (manual)
- **No credential management:** GitHub tokens (automatic) vs SSH keys (manual rotation)
- **Faster deployment:** Immediate trigger (<10s) vs polling (0-5 min delay)
- **Better maintenance:** Git-tracked changes vs manual Jenkins UI edits

---

## Proposed By

Peter Smythe  
**Date:** 2026-03-10

---

## Assigned to Release

This proposal applies to:
- **GeoServer 3.0** (main branch) - New MkDocs documentation
- **GeoServer 2.28.x** - New MkDocs documentation
- **Archive versions (2.27.x and earlier)** - Remain on OSGeo server (frozen, no updates)

---

## State

- [x] Under Discussion
- ☐ In Progress
- ☐ Completed
- ☐ Rejected
- ☐ Deferred

---

## Motivation

Following [GSIP 221](GSIP-221)'s approval to migrate from RST/Sphinx to Markdown/MkDocs, we must update our documentation build infrastructure. GitHub Actions provides version-controlled configuration, eliminates SSH credential management, and offers immediate deployment triggers compared to Jenkins' manual UI configuration and polling-based builds.

---

## Proposal

Migrate documentation builds from Jenkins to GitHub Actions with the following changes:

### Build Infrastructure

| Component | Current (Jenkins) | Proposed (GitHub Actions) |
|-----------|-------------------|---------------------------|
| **Configuration** | Jenkins UI (manual) | YAML in Git (version-controlled) |
| **Credentials** | SSH keys (manual rotation) | GitHub tokens (automatic) |
| **Trigger** | SCM polling (5 min) | Push events (immediate) |
| **Hosting (new versions)** | OSGeo server | GitHub Pages |
| **Hosting (archives)** | OSGeo server | OSGeo server (unchanged) |

### Key Benefits

1. **Version-controlled configuration:** YAML in Git (reviewable, auditable) vs Jenkins UI (manual, no history)
2. **No credential management:** GitHub tokens (automatic) vs SSH keys (manual rotation)
3. **Immediate deployment:** Push events (<10s) vs polling (0-5 min delay)
4. **Easier maintenance:** Git-tracked changes vs manual Jenkins UI edits

---

## Current State

**Jenkins builds** poll GitHub every 5 minutes, build with Maven/Ant/Sphinx, and deploy via SSH to OSGeo server. Jenkins can continue after RST removal with reconfiguration, but requires manual UI changes and continued SSH credential management.

**Current URLs:** `https://docs.geoserver.org/{latest,stable,2.28.x}/en/user/`

---

## Proposed State

**GitHub Actions** triggers immediately on push, builds with MkDocs, and deploys to GitHub Pages using mike for version management.

**Hosting strategy:**
- **GitHub Pages:** 2.28.x (stable), main (latest), all future releases
- **OSGeo Archive:** 2.27.x and earlier (frozen, no updates)

**URLs remain unchanged:** `docs.geoserver.org` (CNAME to GitHub Pages), `docs-archive.geoserver.org` (CNAME to OSGeo)

---

## GitHub Pages Capacity

GitHub Pages has a 1 GB limit, but Git deduplicates identical files across versions. First version: 416 MB, each additional version: ~26 MB (Material theme assets, tutorial data, and 95% of HTML are shared). Can host 20+ versions (910 MB for 20 versions = 91% of limit).

**Hosting plan:**
- GitHub Pages: All versions from 2.28.x onward (2-10 versions = 442-650 MB)
- OSGeo Archive: 2.27.x and earlier (unlimited space, frozen)

---

## Backwards Compatibility

All existing URLs continue to work:
- `docs.geoserver.org/{latest,stable,3.0}/en/user/` → GitHub Pages
- `docs-archive.geoserver.org/2.27.x/en/user/` → OSGeo server

Archive versions (2.27.x and earlier) remain on OSGeo unchanged. No broken links.

---

## Implementation Plan

**Timeline: 1 week**

1. **Days 1-2:** Create GitHub Actions workflow, configure GitHub Pages, test deployment
2. **Days 3-4:** Coordinate DNS changes with infrastructure team (wait for propagation)
3. **Days 5-7:** Merge workflow, disable Jenkins jobs, verify production

**Rollback:** Revert DNS, re-enable Jenkins jobs if issues arise.

---

## Feedback

**Q: Why not keep everything on OSGeo?**  
A: GitHub Actions provides version-controlled configuration, no SSH credential management, faster deployments, and global CDN.

**Q: What happens to old versions?**  
A: Archive versions (2.27.x and earlier) remain on OSGeo server, accessible via `docs-archive.geoserver.org`.

**Q: Will this break existing links?**  
A: No. All URLs remain the same with CNAME redirects.

**Q: What about the 1 GB GitHub Pages limit?**  
A: Git deduplication allows 20+ versions (910 MB for 20 versions). All new versions stay on GitHub Pages permanently.

**Q: Can Jenkins continue after RST removal?**  
A: Yes, but requires manual reconfiguration and continued SSH credential management. GitHub Actions is recommended for version-controlled configuration and easier maintenance.

---

## Voting

**Project Steering Committee:**

- Alessio Fabiani:
- Andrea Aime:
- Ian Turton:
- Jody Garnett:
- Jukka Rahkonen:
- Kevin Smith:
- Simone Giannecchini:
- Torben Barsballe:
- Nuno Oliveira:
- Peter Smythe: +1 (proposing)

**Community Support:**

- 

---

## Links

- **GSIP 221 (MkDocs Migration):** https://github.com/geoserver/geoserver/wiki/GSIP-221


---

**Status:** Awaiting PSC approval  
**Last Updated:** March 10, 2026
