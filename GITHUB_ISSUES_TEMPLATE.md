# GitHub Issues Template - SpeakLine Growth Initiatives

Copy these issues to your GitHub repo to guide community contributions and your own roadmap.

---

## 🔴 PRODUCTION READY (Priority 1)

### Issue: Add Security Test Suite
**Labels:** `bug`, `security`, `test`
**Effort:** 3-4 hours

We've fixed critical security vulnerabilities. Now we need comprehensive tests to prevent regression.

**Acceptance Criteria:**
- [ ] Test path traversal attacks (e.g., `../../etc/passwd`)
- [ ] Test null byte injection
- [ ] Test unsafe line number inputs (negative, float, string)
- [ ] Test file encoding handling (binary, latin-1, mixed)
- [ ] Test temp file cleanup on error
- [ ] Test API key masking in logs
- [ ] 90%+ code coverage on security paths

**Tasks:**
```python
# tests/test_security.py
def test_path_traversal_blocked()
def test_null_byte_rejected()
def test_invalid_line_number_types()
def test_file_encoding_fallback()
def test_temp_file_cleanup()
def test_api_key_not_logged()
```

---

### Issue: Add `--preview` / `--dry-run` Mode
**Labels:** `enhancement`, `ux`
**Effort:** 2 hours

Users should be able to see what will be inserted before modifying their file.

**Acceptance Criteria:**
- [ ] `speakline record file.py 42 --preview` shows the result without writing
- [ ] `speakline insert file.py 42 "comment" --dry-run` shows diff
- [ ] Works with all backends (whisper, openai, mock)
- [ ] Documentation updated with examples

**Implementation:**
```bash
speakline record myfile.py 42 --preview
# Output:
# File: myfile.py
# Target line 42:
#
# -------- PREVIEW (not written) --------
# // This is a comment
# result = calculate()
# -------- END PREVIEW --------
```

---

### Issue: Add Completion Rate & Error Metrics
**Labels:** `documentation`, `observability`
**Effort:** 2 hours

Document realistic success rates and common failure modes.

**Tasks:**
- [ ] Add "Reliability" section to README with metrics
- [ ] Document common errors & solutions
- [ ] Add troubleshooting guide
- [ ] Include PortAudio setup guide for all platforms

---

## 🟡 IDE INTEGRATION (Priority 2)

### Issue: Build VS Code Extension
**Labels:** `feature`, `enhancement`
**Effort:** 20-30 hours (2-3 weeks)
**Complexity:** High

Create a native VS Code extension for seamless voice commenting.

**Features:**
- [ ] Right-click context menu: "Insert voice comment here"
- [ ] Keyboard shortcut: Ctrl+Shift+V (customizable)
- [ ] Visual recording indicator
- [ ] Real-time transcription preview
- [ ] Language auto-detection
- [ ] Backend selection (whisper, openai)
- [ ] Settings panel for silence detection tuning

**Deliverables:**
- TypeScript/Node.js extension
- Published on VS Code Marketplace
- README with installation & usage
- 4.5+ star rating target

**Repo Structure:**
```
vscode-speakline/
├── src/
│   ├── extension.ts
│   ├── commands.ts
│   ├── python-integration.ts
│   └── ui.ts
├── package.json
└── README.md
```

---

### Issue: Build Vim/Neovim Plugin
**Labels:** `feature`, `enhancement`
**Effort:** 10-15 hours (1 week)
**Complexity:** Medium

Native Neovim plugin for voice comments.

**Features:**
- [ ] `:VoiceComment` command
- [ ] `:VoiceCommentPreview` for preview mode
- [ ] Keybinding support
- [ ] Integration with vim-commentary (optional)
- [ ] Status line feedback

**Implementation:**
- Lua plugin (Neovim 0.7+)
- Python fallback for Vim 9

---

## 🟢 CONTENT & COMMUNITY (Priority 3)

### Issue: Create YouTube Tutorial Series
**Labels:** `documentation`, `marketing`
**Effort:** 8-10 hours

Short, engaging videos to drive adoption.

**Videos (3-5 min each):**
1. [ ] "Voice Coding in 2 Minutes" - Quick demo
2. [ ] "Setup Guide: VS Code + SpeakLine"
3. [ ] "Hands-Free Development for RSI"
4. [ ] "Integration with Your Favorite IDE"
5. [ ] "Performance Comparison: Voice vs Typing"

**Metrics:**
- Target 1,000+ views per video
- Include links to docs/GitHub
- Optimize for search: "voice code", "hands-free coding", etc.

---

### Issue: Write Blog Post Series
**Labels:** `documentation`, `marketing`
**Effort:** 6-8 hours

High-quality blog content for SEO & thought leadership.

**Posts:**
1. **"Why Voice Comments?" (1000 words)**
   - Problem: Code comments are often an afterthought
   - Solution: Voice lets you speak naturally while coding
   - Benefits: Better documentation, faster iteration, accessibility
   - Target: HN Front Page

2. **"Hands-Free Coding for Developers with RSI" (800 words)**
   - Audience: Developers with carpal tunnel, tendinitis
   - Statistics on RSI prevalence
   - How voice coding helps
   - Testimonials + case study
   - Target: Accessibility communities

3. **"Building Production Voice AI Tools" (1500 words)**
   - Technical deep-dive: Whisper vs OpenAI API
   - Path traversal vulnerabilities in file tools
   - Safe temporary file handling
   - Lessons learned from SpeakLine
   - Target: Technical leadership, /r/programming

**SEO Keywords:**
- voice coding
- hands-free development
- code comments
- accessibility
- RSI development
- Python CLI tools

---

### Issue: Launch on Product Hunt & HN
**Labels:** `marketing`, `growth`
**Effort:** 4 hours

One-time launch push for visibility.

**Checklist:**
- [ ] Polish README with banner image
- [ ] Prepare launch post with compelling copy
- [ ] Create GIF demo for Product Hunt
- [ ] Reach out to friends/followers for upvotes (day 1)
- [ ] Be active in comments for first 24 hours
- [ ] Post to /r/programming, /r/Python (follow rules)
- [ ] Mention in relevant dev newsletters

**Target Metrics:**
- 500+ Product Hunt upvotes
- HN Front Page (30+ points, 4+ hours)
- 5,000+ GitHub stars (week 1)
- 10,000+ PyPI downloads (week 1)

---

## 💰 MONETIZATION (Priority 4 - Phase 2)

### Issue: Design SpeakLine Cloud (Hosted API)
**Labels:** `feature`, `enhancement`, `monetization`
**Effort:** 40-60 hours (2-3 weeks, Phase 2)

Paid tier for fast, hosted transcription + analytics.

**Features:**
- [ ] Cloud-hosted Whisper inference (2-3x faster)
- [ ] Comment history & analytics
- [ ] Team collaboration
- [ ] Custom comment templates
- [ ] Integration with GitHub/GitLab
- [ ] Usage quotas

**Pricing:**
- Free: 10 comments/day
- Pro: $10/month (unlimited comments, analytics)
- Team: $50/month (team collaboration, SSO)

---

### Issue: Build Desktop App (SpeakLine Pro)
**Labels:** `feature`, `enhancement`, `monetization`
**Effort:** 60-80 hours (3-4 weeks, Phase 2)

Offline-first desktop app with rich UI.

**Tech:** Tauri + React/Svelte
**Features:**
- [ ] Offline mode (local Whisper model)
- [ ] Cloud sync
- [ ] IDE plugin manager
- [ ] Comment templates
- [ ] Analytics dashboard

**Pricing:** $20-50 one-time license

---

## 📊 METRICS & MILESTONES

### Current State (v0.1.0 → v0.2.0)
- ⭐ ~50 GitHub stars (estimate)
- 📦 ~100-500 monthly downloads
- 🐛 5+ critical security vulnerabilities (fixed ✅)
- ✅ Comprehensive test suite

### 3-Month Target (v0.3.0)
- ⭐ 1,000+ GitHub stars
- 📦 5,000+ monthly downloads
- 🔧 VS Code extension launched
- 📹 3+ YouTube videos published
- ✍️ 2+ blog posts published
- 🧪 90%+ test coverage

### 6-Month Target (v1.0.0)
- ⭐ 2,500+ GitHub stars
- 📦 50,000+ monthly downloads
- 🔧 VS Code + Vim + Neovim plugins
- 📹 5+ YouTube videos
- ✍️ 10+ blog posts (organic backlinks)
- ☁️ SpeakLine Cloud MVP launched
- 💵 $5k-10k MRR (if monetization)
- 🌟 Product Hunt #1 Product (goal)

---

## 🎯 CONTRIBUTION GUIDELINES

For community contributions, prioritize:
1. **Security & bugs** (any help appreciated)
2. **Documentation** (tutorials, guides, troubleshooting)
3. **Language support** (add new language parsers)
4. **Testing** (especially edge cases)
5. **Performance** (benchmarks, optimizations)

**NOT accepting yet:**
- Paid features (for v1.0+ only)
- Complex refactoring without discussion
- Breaking API changes

---

## 📞 Contact & Support

- **Email:** contact@speakline.org (from README)
- **GitHub Discussions:** For questions & ideas
- **Issues:** For bugs & feature requests
- **Twitter:** [@speaklinedev](https://twitter.com/speaklinedev) (if created)

---

**Last Updated:** 2026-03-17
**Maintained by:** [Your name]
