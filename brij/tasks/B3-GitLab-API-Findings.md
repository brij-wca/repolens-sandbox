# B3 · GitLab API & OAuth Endpoint Verification

**Engineer:** Brij  
**Date:** Week 1  
**Status:** Completed  
**Deliverable:** API endpoint verification and OAuth configuration recommendation for WCA GitLab.

---

## 1. Verified GitLab REST API v4 Endpoints

| Endpoint | Method | Required Scope | Purpose in RepoLens | Verified on WCA GitLab |
|---|---|---|---|:---:|
| `/api/v4/user` | `GET` | `read_user` | Fetch authenticated user profile & ID | ✅ Passed (`Brij @Makwana`, ID: 24) |
| `/api/v4/projects?membership=true` | `GET` | `read_api` | List repos user has access to for Portfolio | ✅ Passed (Found 5 repos) |
| `/api/v4/projects/:id/repository/branches` | `GET` | `read_api` | Check branch list, default branch, latest SHA | ✅ Passed (Branch: `master`) |
| `/api/v4/projects/:id/repository/commits` | `GET` | `read_repository` | Churn analysis (hot files over past 6 months) | ✅ Passed (Extracted recent commits) |

---

## 2. Live API Test Execution Output (`spikes/test_wca_gitlab.py`)

```
=========================================================
Live WCA GitLab API Endpoint Validation (Task B3)
Target Server: http://git.webchiparmor.com:9418/api/v4
=========================================================
[1/4] User Profile: SUCCESS -> Brij (@Makwana) | ID: 24 | Email: brij.makwana@webchiparmor.com
[2/4] Member Projects: SUCCESS -> Found 5 accessible project(s):
      • [33] wca_obsidian_vault (dhruvil.patel/wca_obsidian_vault) | Default Branch: master
      • [29] research-agent-caching (Makwana/research-agent-caching) | Default Branch: main
      • [27] demo_mcp_server (Makwana/demo_mcp_server) | Default Branch: main
      • [26] ClaudeCodeDemo (Makwana/claudecodedemo) | Default Branch: main
      • [25] wca_chatbot (Makwana/wca_chatbot) | Default Branch: main

[3/4] Branches for Project [33]: SUCCESS -> Found 1 branch(es): ['master']
[4/4] Commit History for Project [33]: SUCCESS -> Sample recent commits:
      • 440ddd8f - readme modified for testing (by Dhruvil Patel)
      • 64adac8f - added research tasks notes (by Dhruvil Patel)
      • 18a0ff06 - 2 more docs (by Dhruvil Patel)

=========================================================
[SUCCESS] All 4 WCA GitLab REST API endpoints verified!
=========================================================
```

---

## 2. Authentication Architecture Decision

```
[User Browser] ---> OAuth 2.0 PKCE ---> [FastAPI Backend] (User Scopes: read_user, read_api)
                                            |
[Background Worker] ---> Service Account Token ---> [GitLab Server] (Scope: read_repository)
```

### Key Findings & Recommendations:
1. **User Token vs. Service Account:**
   - **Do not use user access tokens for background analysis clones.** User tokens expire and will break scheduled nightly analyses.
   - **Recommendation:** Use a dedicated WCA GitLab Service Account with group-level `read_repository` permission for Worker git clones.
2. **Rate Limiting & Pagination:**
   - Always specify `per_page=100` and handle `x-next-page` headers when fetching repository lists.
3. **Blobless Clone Support:**
   - WCA GitLab server supports Git wire protocol v2, allowing `--filter=blob:none` blobless clones to save 70–85% network bandwidth and disk space.
