# CI/CD Deep Dive — From Zero to Production

### For Android Developers Who Want to Actually Understand It

---

## Table of Contents

1. [The Problem CI/CD Solves](#1-the-problem-cicd-solves)
2. [Mental Model: The Assembly Line](#2-mental-model-the-assembly-line)
3. [CI vs CD — The Clear Distinction](#3-ci-vs-cd--the-clear-distinction)
4. [How CI Actually Works Under the Hood](#4-how-ci-actually-works-under-the-hood)
5. [GitHub Actions — The Engine](#5-github-actions--the-engine)
6. [YAML — The Language of CI](#6-yaml--the-language-of-ci)
7. [Anatomy of a Workflow File](#7-anatomy-of-a-workflow-file)
8. [Triggers — When Does CI Run?](#8-triggers--when-does-ci-run)
9. [Jobs & Steps — The Execution Units](#9-jobs--steps--the-execution-units)
10. [Runners — Where Code Actually Executes](#10-runners--where-code-actually-executes)
11. [Actions — Reusable Building Blocks](#11-actions--reusable-building-blocks)
12. [Secrets & Environment Variables](#12-secrets--environment-variables)
13. [Artifacts — Passing Data Between Jobs](#13-artifacts--passing-data-between-jobs)
14. [Caching — Speed Up Your Builds](#14-caching--speed-up-your-builds)
15. [Matrices — Test Multiple Configurations](#15-matrices--test-multiple-configurations)
16. [Conditions & Expressions](#16-conditions--expressions)
17. [Your Sticker CDN Workflow — Line by Line](#17-your-sticker-cdn-workflow--line-by-line)
18. [CI for Android Projects](#18-ci-for-android-projects)
19. [CD for Android — Automated Releases](#19-cd-for-android--automated-releases)
20. [GitHub Pages Deployment — How It Works](#20-github-pages-deployment--how-it-works)
21. [Common Patterns & Best Practices](#21-common-patterns--best-practices)
22. [Debugging Failed Workflows](#22-debugging-failed-workflows)
23. [Security Considerations](#23-security-considerations)
24. [Cost & Limits](#24-cost--limits)
25. [Mental Model Summary](#25-mental-model-summary)
26. [Glossary](#26-glossary)
27. [What to Learn Next — The CD Path](#27-what-to-learn-next--the-cd-path)

---

## 1. The Problem CI/CD Solves

### Without CI (what you've been doing)

```
You write code
  → You manually test on your device
  → You manually build the APK
  → You manually upload to Play Store
  → You forget to test on API 26
  → Bug reaches users
  → You manually hotfix
  → Repeat forever
```

### With CI

```
You write code → push to GitHub
  → Machine AUTOMATICALLY:
      ✓ Checks your code compiles
      ✓ Runs all tests
      ✓ Builds debug + release APK
      ✓ Tests on API 26, 30, 34
      ✓ Signs the APK
      ✓ Uploads to Play Store
      ✓ Notifies you if anything fails
  → You drink chai ☕
```

### The Core Insight

**CI/CD is just "run commands on someone else's computer when something happens."**

That's it. Everything else is details.

When you run `./gradlew assembleDebug` on your laptop — that's a local build.
When GitHub runs `./gradlew assembleDebug` on their server after you push — that's CI.

---

## 2. Mental Model: The Assembly Line

Think of a car factory:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CAR FACTORY (CI/CD)                          │
│                                                                     │
│  RAW MATERIALS              ASSEMBLY LINE             FINISHED CAR  │
│  (your code)                (pipeline)                (deployed app)│
│                                                                     │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐         │
│  │ Code │───→│ Lint │───→│ Test │───→│Build │───→│Deploy│         │
│  │ Push │    │Check │    │      │    │      │    │      │         │
│  └──────┘    └──────┘    └──────┘    └──────┘    └──────┘         │
│                 │            │           │           │               │
│              If fail →    If fail →   If fail →   If fail →        │
│              STOP ❌      STOP ❌     STOP ❌     STOP ❌          │
│              Alert dev    Alert dev   Alert dev   Alert dev        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key principle: If ANY station fails, the whole line stops.**

No half-built car leaves the factory. No broken code reaches production.

### Mapping to Your Brain

| Factory Concept | CI/CD Concept | Your Sticker Project |
|---|---|---|
| Factory | GitHub Actions | GitHub's servers |
| Assembly line | Workflow/Pipeline | `deploy-stickers.yml` |
| Station | Job | `build`, `deploy` |
| Task at a station | Step | `checkout`, `generate`, `upload` |
| Raw materials | Source code | `_master.json` + sticker images |
| Quality check | Validation/Tests | `generate.js` (validates packs) |
| Finished product | Deployed artifact | Live CDN on GitHub Pages |
| Factory floor | Runner | `ubuntu-latest` VM |

---

## 3. CI vs CD — The Clear Distinction

```
CI (Continuous Integration)
├── "Does my code work?"
├── Compile → Test → Validate
├── Runs on EVERY push/PR
├── Output: "Yes it works" or "No, fix this"
└── Goal: Catch bugs BEFORE they merge

CD (Continuous Delivery / Continuous Deployment)
├── "Ship my code to users"
├── Build → Sign → Upload → Deploy
├── Runs AFTER CI passes
├── Output: Production deployment
└── Goal: Get working code to users FAST
```

### The Two Flavors of CD

```
Continuous DELIVERY                    Continuous DEPLOYMENT
─────────────────                      ──────────────────────
CI passes                              CI passes
  ↓                                      ↓
Build release artifact                 Build release artifact
  ↓                                      ↓
Deploy to staging                      Deploy to PRODUCTION ← automatically!
  ↓                                    (no human approval)
Human clicks "approve"
  ↓
Deploy to production
```

**Your sticker CDN uses Continuous Deployment** — push to main → auto-deploys. No approval needed.

**Your Android app will likely use Continuous Delivery** — push to main → builds APK → you manually approve Play Store release.

---

## 4. How CI Actually Works Under the Hood

When you `git push`, here's what ACTUALLY happens:

```
YOUR MACHINE                        GITHUB SERVERS
─────────────                       ──────────────

1. git push origin main
   │
   ├──→ GitHub receives your code
   │
   │    2. GitHub checks: "Any workflow files
   │       in .github/workflows/*.yml?"
   │
   │    3. For each workflow:
   │       "Does this push match the trigger?"
   │       (branch? path? event?)
   │
   │    4. YES → GitHub CREATES a fresh VM
   │       ┌─────────────────────────────┐
   │       │  Brand new Ubuntu machine    │
   │       │  - No files                  │
   │       │  - No history                │
   │       │  - Clean slate               │
   │       │  - 7GB RAM, 2 CPU, 14GB SSD  │
   │       └─────────────────────────────┘
   │
   │    5. VM runs your steps IN ORDER:
   │       → checkout (git clone your repo)
   │       → setup tools (node, java, etc.)
   │       → run your commands
   │       → upload results
   │
   │    6. VM is DESTROYED after workflow
   │       (nothing persists)
   │
   │    7. GitHub marks commit with ✅ or ❌
   │
   └──← You see the result on GitHub
```

### Critical Understanding: Ephemeral Environments

**Every CI run starts from ZERO.** The VM has:
- No files from previous runs
- No cached dependencies (unless you explicitly cache)
- No state from last build
- No environment variables from last time

That's why every workflow starts with `actions/checkout` — the VM literally has nothing until you tell it to clone your repo.

This is a FEATURE, not a bug. It guarantees **reproducibility**:
- Same code → same result. Always.
- No "works on my machine" problems.
- No leftover state causing mystery bugs.

---

## 5. GitHub Actions — The Engine

GitHub Actions is GitHub's CI/CD platform. It's one of many:

| CI/CD Platform | Used By | Key Trait |
|---|---|---|
| **GitHub Actions** | GitHub repos | Free for public repos, integrated |
| Jenkins | Enterprise | Self-hosted, maximum control |
| CircleCI | Startups | Fast, good Docker support |
| Bitrise | Mobile teams | Android/iOS focused |
| GitLab CI | GitLab repos | Built into GitLab |
| Firebase App Distribution | Android | Google's testing pipeline |

**Why GitHub Actions for us:**
- Free for public repos (2,000 minutes/month for private)
- Directly integrated with GitHub (no external service)
- Marketplace with 20,000+ pre-built actions
- GitHub Pages deployment is native

### Core Concepts Map

```
GitHub Actions Hierarchy:

Repository
  └── .github/workflows/
        └── workflow.yml          ← WORKFLOW (the file)
              ├── name            ← Human-readable name
              ├── on              ← TRIGGER (when to run)
              └── jobs            ← JOBS (groups of tasks)
                    ├── build     ← JOB (runs on a VM)
                    │   └── steps ← STEPS (individual commands)
                    │       ├── uses: actions/checkout@v4    ← ACTION (reusable)
                    │       ├── run: npm install             ← COMMAND (raw shell)
                    │       └── run: npm test
                    │
                    └── deploy    ← JOB (different VM!)
                        └── steps
                            └── ...
```

**One repository** can have **multiple workflows**.
**One workflow** can have **multiple jobs**.
**One job** can have **multiple steps**.
**Jobs** run in **parallel** by default.
**Steps** always run **sequentially**.

---

## 6. YAML — The Language of CI

YAML (Yet Another Markup Language) is how you write CI configs. If you know JSON, YAML is just JSON made readable.

### JSON vs YAML — Same Data

```json
// JSON
{
  "name": "Hafiz",
  "age": 25,
  "skills": ["Kotlin", "Compose", "CI"],
  "address": {
    "city": "Lahore",
    "country": "PK"
  }
}
```

```yaml
# YAML (same data!)
name: Hafiz
age: 25
skills:
  - Kotlin
  - Compose
  - CI
address:
  city: Lahore
  country: PK
```

### YAML Rules You Must Know

```yaml
# 1. INDENTATION = STRUCTURE (like Python)
#    Use spaces, NEVER tabs. 2 spaces is standard.

parent:
  child: value          # ✅ 2 spaces
    grandchild: value   # ✅ 4 spaces (2 more)

# 2. KEY: VALUE (colon + space)
name: Hafiz             # ✅
name:Hafiz              # ❌ missing space after colon

# 3. LISTS use dash + space
fruits:
  - apple               # ✅
  - banana
  -cherry               # ❌ missing space after dash

# 4. INLINE LISTS (like JSON arrays)
fruits: [apple, banana, cherry]    # ✅ same as above

# 5. MULTI-LINE STRINGS
#    | = keeps line breaks (literal)
#    > = folds into one line

description: |
  This is line 1.
  This is line 2.
  # Result: "This is line 1.\nThis is line 2.\n"

description: >
  This is line 1.
  This is line 2.
  # Result: "This is line 1. This is line 2.\n"

# 6. BOOLEANS
enabled: true            # boolean true
enabled: "true"          # string "true" ← be careful!
on: true                 # GOTCHA: "on" is a boolean keyword in YAML!
"on": triggers           # That's why GitHub uses "on:" as a keyword

# 7. COMMENTS
# This is a comment
name: Hafiz  # Inline comment

# 8. NULL
value: null
value: ~                 # Same as null
value:                   # Also null (empty value)
```

### The #1 YAML Mistake

```yaml
# WRONG — tabs instead of spaces
jobs:
→ build:           # ← TAB character = YAML parse error
→ → steps:

# RIGHT — spaces only
jobs:
  build:           # ← 2 spaces
    steps:         # ← 4 spaces
```

**Pro tip**: In VS Code, enable "Render Whitespace" and "Insert Spaces" for YAML files.

---

## 7. Anatomy of a Workflow File

Every workflow file has 3 sections. Think of it as: **WHEN** + **WHERE** + **WHAT**.

```yaml
# ─── SECTION 1: METADATA ──────────────────────────────────

name: My Workflow           # Display name (shows in Actions tab)

# ─── SECTION 2: WHEN (Triggers) ───────────────────────────

on:                         # When should this workflow run?
  push:
    branches: [main]

# ─── SECTION 3: WHAT (Jobs + Steps) ───────────────────────

jobs:                       # What should happen?
  build:                    # Job ID (you name it)
    runs-on: ubuntu-latest  # WHERE does it run?
    steps:                  # WHAT commands to execute?
      - name: Step 1
        run: echo "Hello"
```

### How They Connect

```
┌─────────────────────────────────────────────────────┐
│  name: My Workflow                                   │
│                                                      │
│  WHEN?         WHERE?              WHAT?             │
│  ───────       ──────              ──────            │
│  on: push  →   runs-on: ubuntu →   steps:           │
│  to main       (a fresh VM)        - checkout repo   │
│                                     - install deps   │
│                                     - run tests      │
│                                     - deploy         │
└─────────────────────────────────────────────────────┘
```

---

## 8. Triggers — When Does CI Run?

The `on:` section is the most important part. It decides WHEN your pipeline runs.

### Common Triggers

```yaml
# ─── 1. PUSH to branch ─────────────────────────────
on:
  push:
    branches: [main]              # Only main branch
    # branches: [main, develop]   # Multiple branches
    # branches: ['release/**']    # Glob pattern

# ─── 2. PUSH with path filter ──────────────────────
on:
  push:
    branches: [main]
    paths:
      - 'sticker-cdn/**'         # Only if these files changed
      - 'scripts/**'
    paths-ignore:
      - '**.md'                   # Ignore markdown changes

# ─── 3. PULL REQUEST ───────────────────────────────
on:
  pull_request:
    branches: [main]              # PR targeting main
    types: [opened, synchronize]  # When PR is opened or updated

# ─── 4. MANUAL TRIGGER ─────────────────────────────
on:
  workflow_dispatch:              # "Run workflow" button in GitHub UI
    inputs:                       # Optional: ask for inputs
      environment:
        description: 'Deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

# ─── 5. SCHEDULE (cron) ────────────────────────────
on:
  schedule:
    - cron: '0 6 * * 1'          # Every Monday at 6:00 AM UTC
    # ┌───── minute (0-59)
    # │ ┌──── hour (0-23)
    # │ │ ┌─── day of month (1-31)
    # │ │ │ ┌── month (1-12)
    # │ │ │ │ ┌─ day of week (0-6, 0=Sunday)
    # * * * * *

# ─── 6. TAG push ───────────────────────────────────
on:
  push:
    tags:
      - 'v*'                     # When you push v1.0.0, v2.0.0, etc.

# ─── 7. RELEASE ────────────────────────────────────
on:
  release:
    types: [published]           # When you publish a GitHub Release

# ─── 8. MULTIPLE TRIGGERS ──────────────────────────
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:              # All three!
```

### Path Filters — The Game Changer

This is what YOUR sticker CDN uses:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'sticker-cdn/**'     # Only triggers when sticker files change
      - 'scripts/generate.js'
```

**Why this matters:**
- Edit `README.md` → push → **NO workflow runs** (saves CI minutes)
- Edit `_master.json` → push → **workflow triggers** ✅
- Add new sticker images → push → **workflow triggers** ✅

### Mental Model for Triggers

```
Every push to GitHub:
  ↓
GitHub checks ALL .yml files in .github/workflows/
  ↓
For EACH workflow:
  ├── Does the event match? (push? PR? tag?)
  ├── Does the branch match? (main? develop?)
  ├── Do the paths match? (sticker-cdn/*?)
  │
  ├── ALL YES → Run this workflow
  └── ANY NO  → Skip this workflow
```

---

## 9. Jobs & Steps — The Execution Units

### Jobs = Parallel Workstreams

```yaml
jobs:
  lint:                    # Job 1 ─┐
    runs-on: ubuntu-latest #         ├── These run IN PARALLEL
    steps: ...             #         │   (on separate VMs!)
                           #         │
  test:                    # Job 2 ─┘
    runs-on: ubuntu-latest
    steps: ...

  deploy:                  # Job 3 ── This WAITS for lint + test
    needs: [lint, test]    #          (runs only if both pass)
    runs-on: ubuntu-latest
    steps: ...
```

```
Timeline:
─────────────────────────────────────────────→ time

  lint   ████████████
  test   ████████████████████
  deploy                      ██████████████
                    ↑
            waits for both (needs:)
```

### Steps = Sequential Commands

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # Step 1: Use a pre-built action
      - name: Checkout code
        uses: actions/checkout@v4       # ← ACTION (reusable module)

      # Step 2: Use another action
      - name: Setup Node
        uses: actions/setup-node@v4
        with:                           # ← INPUT to the action
          node-version: 20

      # Step 3: Run a shell command
      - name: Install dependencies
        run: npm install                # ← RAW COMMAND

      # Step 4: Run multiple commands
      - name: Build and test
        run: |                          # ← MULTI-LINE commands
          npm run build
          npm test
          echo "All done!"

      # Step 5: Conditional step
      - name: Notify on failure
        if: failure()                   # ← Only runs if previous step failed
        run: echo "Something broke!"
```

### The Two Types of Steps

```
┌──────────────────────────────────────────────────┐
│  uses: actions/checkout@v4                       │
│  ─────────────────────────                       │
│  PRE-BUILT ACTION                                │
│  • Made by GitHub or community                   │
│  • Published on GitHub Marketplace               │
│  • You provide inputs via `with:`                │
│  • Like importing a library in Android           │
├──────────────────────────────────────────────────┤
│  run: npm install && npm test                    │
│  ────────────────────────────                    │
│  RAW SHELL COMMAND                               │
│  • Runs in bash (Linux) or PowerShell (Windows)  │
│  • Exactly what you'd type in terminal           │
│  • Can be multi-line with `|`                    │
│  • Like running a terminal command               │
└──────────────────────────────────────────────────┘
```

### Job Dependencies (`needs:`)

```yaml
jobs:
  # No needs → runs immediately
  a:
    steps: ...

  # Needs a → waits for a to finish
  b:
    needs: a
    steps: ...

  # Needs a → waits for a to finish
  c:
    needs: a
    steps: ...

  # Needs b AND c → waits for both
  d:
    needs: [b, c]
    steps: ...
```

```
Execution graph:

    a
   / \
  b   c       ← b and c run in parallel AFTER a
   \ /
    d         ← d runs after both b and c
```

---

## 10. Runners — Where Code Actually Executes

A **runner** is the machine that executes your workflow.

### GitHub-Hosted Runners (what you use)

```yaml
runs-on: ubuntu-latest     # Linux (most common, cheapest)
runs-on: ubuntu-22.04      # Specific Ubuntu version
runs-on: windows-latest    # Windows Server
runs-on: macos-latest      # macOS (most expensive)
runs-on: macos-14          # macOS 14 (ARM, M1)
```

| Runner | OS | CPU | RAM | Disk | Cost (private repo) |
|---|---|---|---|---|---|
| `ubuntu-latest` | Ubuntu 22.04 | 4 cores | 16 GB | 14 GB SSD | $0.008/min |
| `windows-latest` | Windows Server | 4 cores | 16 GB | 14 GB SSD | $0.016/min (2x) |
| `macos-latest` | macOS 14 | 3/4 cores | 14 GB | 14 GB SSD | $0.08/min (10x!) |

**Key insight**: `ubuntu-latest` is the default for a reason — it's the cheapest and handles 95% of CI tasks including Android builds.

### What's Pre-installed on Ubuntu Runner?

```
Already available (don't need to install):
  ✓ Git
  ✓ Node.js (multiple versions)
  ✓ Python
  ✓ Java (multiple versions via setup-java action)
  ✓ Docker
  ✓ curl, wget, jq
  ✓ Android SDK (partial — you add what you need)
  ✓ Gradle
  ✓ npm, yarn
```

### Self-Hosted Runners (advanced, not needed now)

You can run workflows on YOUR OWN machine:

```yaml
runs-on: self-hosted       # Runs on your server
```

**When to use**: Company policy, special hardware, cost savings at scale. Not relevant for you yet.

---

## 11. Actions — Reusable Building Blocks

Actions are like libraries. Instead of writing 50 lines of bash, you `uses:` a pre-built action.

### Most Common Actions

```yaml
# Clone your repository
- uses: actions/checkout@v4

# Setup programming languages
- uses: actions/setup-node@v4
  with:
    node-version: 20

- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'

# Caching
- uses: actions/cache@v4
  with:
    path: ~/.gradle/caches
    key: gradle-${{ hashFiles('**/*.gradle*') }}

# Upload/download artifacts (pass data between jobs)
- uses: actions/upload-artifact@v4
  with:
    name: my-app
    path: app/build/outputs/apk/

# GitHub Pages
- uses: actions/configure-pages@v4
- uses: actions/upload-pages-artifact@v3
- uses: actions/deploy-pages@v4
```

### Action Version Pinning

```yaml
# MAJOR version — gets bug fixes automatically (recommended)
- uses: actions/checkout@v4

# EXACT version — completely frozen (maximum security)
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

# SPECIFIC tag
- uses: actions/checkout@v4.1.1

# Branch (risky — can change anytime)
- uses: actions/checkout@main    # ❌ Don't do this in production
```

**Best practice**: Use `@v4` (major version). You get security patches but no breaking changes.

### Finding Actions

1. **GitHub Marketplace**: https://github.com/marketplace?type=actions
2. Search: "android build action", "firebase deploy action", etc.
3. Every action has a README showing inputs and usage

---

## 12. Secrets & Environment Variables

### Environment Variables

```yaml
jobs:
  build:
    runs-on: ubuntu-latest

    # Job-level env (available to all steps)
    env:
      NODE_ENV: production
      API_URL: https://api.example.com

    steps:
      - name: Use env variable
        run: echo "Environment is $NODE_ENV"

      # Step-level env (only this step)
      - name: Custom step
        env:
          SPECIAL_VAR: hello
        run: echo "$SPECIAL_VAR"
```

### Secrets (for sensitive data)

Never put passwords, API keys, or signing keys in your workflow file!

```yaml
# Set secrets in: GitHub → Settings → Secrets and variables → Actions

steps:
  - name: Sign APK
    env:
      KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
      KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
    run: ./sign-apk.sh
```

### Built-in Variables (GitHub provides these)

```yaml
steps:
  - run: |
      echo "Repository: ${{ github.repository }}"        # HafizG/ai_sticker_maker
      echo "Branch: ${{ github.ref_name }}"               # main
      echo "Commit SHA: ${{ github.sha }}"                # abc123...
      echo "Actor: ${{ github.actor }}"                   # HafizG
      echo "Event: ${{ github.event_name }}"              # push
      echo "Run number: ${{ github.run_number }}"         # 42
      echo "Workspace: ${{ github.workspace }}"           # /home/runner/work/...
```

### Android Signing Example

```yaml
# 1. Store your keystore as base64 secret:
#    base64 your-keystore.jks | pbcopy  (then paste in GitHub Secrets)
#
# 2. Use in workflow:

steps:
  - name: Decode keystore
    env:
      KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
    run: echo "$KEYSTORE_BASE64" | base64 --decode > app/keystore.jks

  - name: Build signed APK
    env:
      KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
      KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
      KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
    run: ./gradlew assembleRelease
```

---

## 13. Artifacts — Passing Data Between Jobs

**Problem**: Each job runs on a DIFFERENT VM. Job 2 can't see files from Job 1.

**Solution**: Artifacts — upload files from Job 1, download in Job 2.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew assembleDebug

      # Upload the APK so deploy job can access it
      - uses: actions/upload-artifact@v4
        with:
          name: debug-apk
          path: app/build/outputs/apk/debug/app-debug.apk
          retention-days: 7        # Auto-delete after 7 days

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      # Download the APK from build job
      - uses: actions/download-artifact@v4
        with:
          name: debug-apk

      - run: ls -la    # app-debug.apk is here!
```

```
Job: build (VM #1)                    Job: deploy (VM #2)
─────────────────                     ──────────────────
Build APK                             (empty VM)
  ↓                                      ↓
Upload artifact ──→ GitHub Storage ──→ Download artifact
  ↓                                      ↓
VM destroyed                          Has the APK!
```

### Your Sticker CDN Uses This

```yaml
# In your workflow:
- uses: actions/upload-pages-artifact@v3    # Uploads sticker-cdn/ to GitHub
  with:
    path: 'sticker-cdn'

# Then in deploy job:
- uses: actions/deploy-pages@v4             # Downloads it and deploys to Pages
```

---

## 14. Caching — Speed Up Your Builds

Without cache: Every build downloads all dependencies from scratch.
With cache: First build downloads, subsequent builds reuse.

### Gradle Cache (Android)

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Java
    uses: actions/setup-java@v4
    with:
      distribution: 'temurin'
      java-version: '17'

  - name: Cache Gradle
    uses: actions/cache@v4
    with:
      path: |
        ~/.gradle/caches
        ~/.gradle/wrapper
      key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
      restore-keys: |
        gradle-${{ runner.os }}-

  - name: Build
    run: ./gradlew assembleDebug
```

### How Cache Keys Work

```
key: gradle-Linux-abc123

First run:
  → Cache miss (key "gradle-Linux-abc123" not found)
  → Download all dependencies (slow: 2-3 minutes)
  → Save to cache with key "gradle-Linux-abc123"

Second run (same gradle files):
  → Cache HIT (key "gradle-Linux-abc123" found!)
  → Restore from cache (fast: 10-20 seconds)
  → Skip downloads

Third run (gradle files changed):
  → key is now "gradle-Linux-def456"
  → Cache miss on exact key
  → Try restore-keys: "gradle-Linux-" → partial match!
  → Restore what we can, download only what's new
```

### Node.js Cache

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'     # ← Built-in caching! Just one line.
```

---

## 15. Matrices — Test Multiple Configurations

Run the SAME job with DIFFERENT configurations simultaneously.

### Android API Level Matrix

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        api-level: [26, 30, 34]
        # This creates 3 parallel jobs:
        # test (api-level=26)
        # test (api-level=30)
        # test (api-level=34)

    steps:
      - uses: actions/checkout@v4
      - name: Run tests on API ${{ matrix.api-level }}
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: ${{ matrix.api-level }}
          script: ./gradlew connectedCheck
```

### Multi-Dimensional Matrix

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    java: [11, 17]
    # Creates 4 jobs: ubuntu+11, ubuntu+17, macos+11, macos+17

  fail-fast: false   # Don't cancel other jobs if one fails
  max-parallel: 2    # Run max 2 jobs at once
```

---

## 16. Conditions & Expressions

### `if:` Conditions

```yaml
steps:
  # Always runs
  - name: Build
    run: ./gradlew build

  # Only on main branch
  - name: Deploy
    if: github.ref == 'refs/heads/main'
    run: ./deploy.sh

  # Only on pull requests
  - name: PR comment
    if: github.event_name == 'pull_request'
    run: echo "This is a PR"

  # Only if previous step failed
  - name: Notify on failure
    if: failure()
    run: echo "Build failed!"

  # Always (even if previous steps failed)
  - name: Cleanup
    if: always()
    run: rm -rf temp/

  # Custom condition
  - name: Release build
    if: startsWith(github.ref, 'refs/tags/v')
    run: ./gradlew assembleRelease
```

### Expression Syntax

```yaml
# String comparison
if: github.ref == 'refs/heads/main'

# Boolean
if: github.event.pull_request.draft == false

# Functions
if: contains(github.event.head_commit.message, '[skip ci]')
if: startsWith(github.ref, 'refs/tags/')
if: endsWith(github.repository, 'ai_sticker_maker')

# Status functions
if: success()    # All previous steps succeeded (default)
if: failure()    # Any previous step failed
if: cancelled()  # Workflow was cancelled
if: always()     # Run regardless of status

# Combining
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
if: failure() || cancelled()
```

---

## 17. Your Sticker CDN Workflow — Line by Line

Let's dissect YOUR actual workflow:

```yaml
# ─── THE NAME ──────────────────────────────────────────────
name: Deploy Sticker CDN
# Shows as "Deploy Sticker CDN" in the Actions tab on GitHub

# ─── THE TRIGGERS ──────────────────────────────────────────
on:
  push:
    branches: [main]           # Only main branch, not feature branches
    paths:                     # Only when these files change
      - 'sticker-cdn/**'      # Any file inside sticker-cdn/
      - 'scripts/generate.js' # Or the generate script

  workflow_dispatch:           # "Run workflow" button in GitHub UI
                               # Useful for re-deploying without code changes

# ─── PERMISSIONS ───────────────────────────────────────────
permissions:
  contents: read               # Can read repo files (for checkout)
  pages: write                 # Can write to GitHub Pages
  id-token: write              # Required for Pages deployment (OIDC)

# ─── CONCURRENCY ───────────────────────────────────────────
concurrency:
  group: "pages"               # Only one "pages" deploy at a time
  cancel-in-progress: true     # If new push arrives, cancel the old deploy
  # Why? Two simultaneous deploys would conflict

# ─── JOB 1: BUILD ─────────────────────────────────────────
jobs:
  build:
    runs-on: ubuntu-latest     # Fresh Ubuntu VM

    steps:
      # Step 1: Clone your repo into the VM
      - name: Checkout repository
        uses: actions/checkout@v4
        # Now the VM has all your files:
        # sticker-cdn/_master.json, packs/*, scripts/*, etc.

      # Step 2: Install Node.js (needed for generate.js)
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      # Step 3: THE CORE — validate + generate
      - name: Validate & generate registry files
        run: node scripts/generate.js
        # This does:
        # 1. Reads _master.json
        # 2. Validates all packs (folders exist? tray_icon? sequential?)
        # 3. Validates categories, regions, zones
        # 4. Generates index.json
        # 5. Generates 15 region/zone JSON files
        # 6. EXIT CODE 0 = success, EXIT CODE 1 = validation failed
        #
        # If generate.js exits with code 1 → this step FAILS
        # → all subsequent steps are SKIPPED
        # → deploy job NEVER runs
        # → broken data NEVER reaches production
        # → THIS IS YOUR SAFETY NET

      # Step 4: Debug output (optional, helpful for troubleshooting)
      - name: List generated files (debug)
        run: |
          echo "=== index.json ==="
          cat sticker-cdn/index.json | head -30
          echo ""
          echo "=== Region files ==="
          ls -la sticker-cdn/regions/
          echo ""
          echo "=== Pack folders ==="
          ls -la sticker-cdn/packs/

      # Step 5: Prepare GitHub Pages
      - name: Configure GitHub Pages
        uses: actions/configure-pages@v4
        # Sets up Pages metadata and configuration

      # Step 6: Package everything for deployment
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'sticker-cdn'
        # Takes the entire sticker-cdn/ folder and uploads it
        # as a .tar.gz artifact to GitHub's storage.
        # This is what gets deployed in the next job.
        #
        # IMPORTANT: Only sticker-cdn/ contents are uploaded.
        # scripts/, .github/, README.md are NOT deployed.
        # That's why your URLs start at the root:
        #   /index.json  (not /sticker-cdn/index.json)

  # ─── JOB 2: DEPLOY ────────────────────────────────────────
  deploy:
    needs: build               # Only runs AFTER build job succeeds
    runs-on: ubuntu-latest     # Fresh VM (different from build!)

    environment:
      name: github-pages       # GitHub tracks this as a "deployment"
      url: ${{ steps.deployment.outputs.page_url }}
      # After deploy, shows the URL in GitHub UI

    steps:
      - name: Deploy to GitHub Pages
        id: deployment          # Give this step an ID so we can reference it
        uses: actions/deploy-pages@v4
        # Downloads the artifact from build job
        # Deploys it to GitHub Pages CDN
        # Makes it live at https://hafizg.github.io/ai_sticker_maker/
```

### The Safety Chain

```
push to main
  ↓
Does it touch sticker-cdn/** or scripts/generate.js?
  NO → nothing happens
  YES ↓
  
[Build Job]
  checkout → setup-node → generate.js
                              ↓
                    Validation passes?
                      NO → ❌ Job fails → Deploy NEVER runs
                      YES ↓
                    Generate JSONs → Upload artifact
                              ↓
[Deploy Job]
  Download artifact → Deploy to Pages → Live! ✅
```

---

## 18. CI for Android Projects

Here's a production-ready Android CI workflow:

```yaml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── LINT & STATIC ANALYSIS ─────────────────────────────
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*') }}

      - name: Run lint
        run: ./gradlew lint

      - name: Upload lint report
        if: always()                  # Upload even if lint fails
        uses: actions/upload-artifact@v4
        with:
          name: lint-report
          path: app/build/reports/lint-results-debug.html

  # ─── UNIT TESTS ─────────────────────────────────────────
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*') }}

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: app/build/reports/tests/

  # ─── BUILD APK ──────────────────────────────────────────
  build:
    needs: [lint, test]             # Only build if lint + tests pass
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*') }}

      - name: Build debug APK
        run: ./gradlew assembleDebug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: app-debug
          path: app/build/outputs/apk/debug/app-debug.apk
```

### What This Gives You

```
Every push to main/develop:

  lint ─────────────┐
                    ├──→ build (APK)
  test ─────────────┘    ↓
                    Download APK from
                    Actions tab on GitHub

Every PR:
  Same pipeline runs
  Shows ✅/❌ on the PR
  Reviewer knows: "code compiles, tests pass, lint clean"
```

---

## 19. CD for Android — Automated Releases

### Build Signed APK + Upload to Play Store

```yaml
name: Release to Play Store

on:
  push:
    tags:
      - 'v*'          # Triggers on: git tag v1.0.0 && git push --tags

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      # Decode keystore from secret
      - name: Decode keystore
        env:
          KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
        run: echo "$KEYSTORE_BASE64" | base64 --decode > app/release.jks

      # Build signed release APK/AAB
      - name: Build release bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      # Upload to Play Store (internal track)
      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_JSON }}
          packageName: com.hafiz.stickersapp
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal            # internal → alpha → beta → production
          status: completed

      # Create GitHub Release
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            app/build/outputs/apk/release/app-release.apk
          generate_release_notes: true
```

### The Release Flow

```
Developer:
  1. Finish feature
  2. Update versionCode + versionName in build.gradle
  3. git commit -m "release v1.2.0"
  4. git tag v1.2.0
  5. git push origin main --tags

CI/CD:
  1. Tag push detected → workflow triggers
  2. Build signed AAB
  3. Upload to Play Store (internal track)
  4. Create GitHub Release with APK download
  5. Done!

Manual step:
  Go to Play Console → promote internal → production
  (or automate this too with track: production)
```

---

## 20. GitHub Pages Deployment — How It Works

This is exactly what your sticker CDN uses. Let's understand it deeply.

### What is GitHub Pages?

```
GitHub Pages = Free static file hosting by GitHub

Input:  A folder of files (HTML, JSON, images, etc.)
Output: A website at https://{user}.github.io/{repo}/

It's NOT a server. No backend code. No databases.
Just static files served from GitHub's CDN.
```

### Two Deployment Methods

```
METHOD 1: Deploy from Branch (old way)
───────────────────────────────────────
Settings → Pages → Source: "Deploy from branch"
Pick branch: main, folder: /docs

GitHub serves files from that branch/folder directly.
Simple but no build step — what's in the repo IS what's deployed.


METHOD 2: GitHub Actions (what you use)
───────────────────────────────────────
Settings → Pages → Source: "GitHub Actions"

You control exactly what gets deployed via your workflow.
You can BUILD files (generate JSONs) before deploying.
Only the artifact you upload gets published.
```

### The 3-Action Dance

```yaml
# Step 1: CONFIGURE — Tell GitHub "I want to deploy to Pages"
- uses: actions/configure-pages@v4

# Step 2: UPLOAD — Package your files into an artifact
- uses: actions/upload-pages-artifact@v3
  with:
    path: 'sticker-cdn'     # This folder becomes the website root
    # sticker-cdn/index.json → https://...github.io/ai_sticker_maker/index.json
    # sticker-cdn/regions/PK.json → https://...github.io/ai_sticker_maker/regions/PK.json

# Step 3: DEPLOY — Make it live
- uses: actions/deploy-pages@v4
```

### Why path: 'sticker-cdn' Makes the Root

```
Your repo:
  sticker-cdn/
    index.json
    regions/
    packs/
  scripts/
  README.md

Upload path: 'sticker-cdn'

What gets deployed (website root):
  /index.json          ← sticker-cdn/index.json
  /regions/PK.json     ← sticker-cdn/regions/PK.json
  /packs/pk-funny-urdu/1.webp

What does NOT get deployed:
  scripts/             ← Not inside sticker-cdn/
  README.md            ← Not inside sticker-cdn/
  .github/             ← Not inside sticker-cdn/
```

### Permissions Required

```yaml
permissions:
  contents: read       # Read repo files
  pages: write         # Write to GitHub Pages
  id-token: write      # OIDC token for secure deployment
```

Without these → deployment silently fails.

### Concurrency

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: true
```

**Why**: If you push twice quickly:
- Push 1 → starts deploying
- Push 2 → cancels Push 1's deploy → starts its own
- Only the LATEST push gets deployed

Without this, two deploys could run simultaneously and corrupt each other.

---

## 21. Common Patterns & Best Practices

### Pattern 1: PR Checks → Main Deploys

```yaml
# .github/workflows/ci.yml
on:
  pull_request:
    branches: [main]

jobs:
  check:
    steps:
      - run: ./validate.sh    # Tests on PR

# .github/workflows/deploy.yml
on:
  push:
    branches: [main]          # Only deploy merged code

jobs:
  deploy:
    steps:
      - run: ./deploy.sh
```

### Pattern 2: Branch Protection

In GitHub Settings → Branches → Add rule for `main`:
- ✅ Require status checks before merging
- ✅ Require `check` job to pass
- Result: **Can't merge broken code to main**

### Pattern 3: Semantic Versioning with Tags

```bash
# Development
git commit -m "feat: add new sticker pack"
git push origin main                          # CI runs, deploys

# Release
git tag v1.2.0
git push origin v1.2.0                        # CD builds release APK
```

### Pattern 4: Environment-Based Deploys

```yaml
jobs:
  deploy-staging:
    environment: staging      # Deploys to staging
    steps: ...

  deploy-production:
    needs: deploy-staging
    environment: production   # Manual approval required
    steps: ...
```

### Best Practices Checklist

```
✅ Use path filters — don't run CI on README changes
✅ Cache dependencies — save 2-3 minutes per build
✅ Use `needs:` — don't deploy if tests fail
✅ Pin action versions — @v4 not @main
✅ Use secrets — never hardcode passwords
✅ Use concurrency — prevent double deploys
✅ Upload artifacts — save build outputs
✅ Add if: always() to report steps — see failures
✅ Keep workflows small — split into multiple files if complex
✅ Use workflow_dispatch — ability to manually trigger
```

---

## 22. Debugging Failed Workflows

### Where to See Logs

```
GitHub.com → Your repo → Actions tab → Click the run → Click the job → Click the step
```

### Common Failures

```
❌ "Permission denied"
   → Check: permissions: section in workflow
   → Check: GitHub Pages source set to "GitHub Actions"
   → Check: repo is public (or you have Pro plan)

❌ "Process exited with code 1"
   → Your script (generate.js, gradlew) failed
   → Read the log output above the error
   → This is YOUR code failing, not CI

❌ "Resource not accessible by integration"
   → Missing permissions in workflow
   → Or: organization settings blocking Actions

❌ "No space left on device"
   → Runner disk is 14GB, your build is too big
   → Clean up: rm -rf ~/.gradle/caches before build
   → Or: use a larger runner

❌ Workflow not triggering
   → Check: branch name matches `branches:` filter
   → Check: file path matches `paths:` filter
   → Check: workflow file is in .github/workflows/ on the DEFAULT branch
   → Check: YAML syntax is valid (use yamllint)
```

### Debug Technique: Add Echo Statements

```yaml
steps:
  - name: Debug info
    run: |
      echo "Event: ${{ github.event_name }}"
      echo "Ref: ${{ github.ref }}"
      echo "SHA: ${{ github.sha }}"
      echo "Actor: ${{ github.actor }}"
      pwd
      ls -la
      cat some-file.json
```

### Debug Technique: Enable Debug Logging

Add this secret to your repo:
- Name: `ACTIONS_STEP_DEBUG`
- Value: `true`

Now ALL workflow runs show verbose debug output.

---

## 23. Security Considerations

### The Threat Model

```
Your workflow runs ARBITRARY CODE on GitHub's servers.
If someone can modify your workflow → they can:
  → Read your secrets
  → Deploy malicious code
  → Access any service your secrets connect to
```

### Rules

```
1. NEVER print secrets
   run: echo ${{ secrets.MY_KEY }}     # ❌ appears in logs!

2. NEVER use user input in run: directly
   run: echo "${{ github.event.comment.body }}"  # ❌ injection!

3. Pin actions to commit SHAs for critical workflows
   uses: actions/checkout@b4ffde65...  # ✅ immutable

4. Use environments for production deploys
   environment: production             # ✅ requires approval

5. Limit permissions to minimum needed
   permissions:
     contents: read                    # ✅ read-only
     # NOT: contents: write (unless you need it)

6. Review pull requests from forks
   # Fork PRs CAN run your CI but CANNOT access secrets
   # (unless you explicitly allow it — don't!)

7. Rotate secrets regularly
   # Change API keys, signing keys every 6-12 months
```

---

## 24. Cost & Limits

### Free Tier (Public Repos)

```
Public repositories: UNLIMITED CI minutes ✅
Private repositories: 2,000 minutes/month (free plan)
                      3,000 minutes/month (Pro)
```

### Minute Multipliers (Private Repos Only)

```
ubuntu   → 1x  (1 min used = 1 min counted)
windows  → 2x  (1 min used = 2 min counted)
macos    → 10x (1 min used = 10 min counted!)
```

### Storage Limits

```
Artifacts: 500 MB (free) / 2 GB (Pro)
GitHub Pages: 1 GB
Packages: 500 MB (free)
```

### Your Sticker CDN Cost

```
Public repo → $0
Each deploy: ~30 seconds
Storage: ~5MB (sticker images + JSONs)
Totally free. Forever.
```

---

## 25. Mental Model Summary

### The 30-Second CI Explanation

```
CI = "Run my script on a clean machine every time I push code."

Workflow file tells GitHub:
  WHEN to run  (push to main? PR? tag? schedule?)
  WHERE to run (ubuntu? macos? windows?)
  WHAT to run  (checkout → build → test → deploy)
  
If any step fails → everything after it stops.
That's your safety net.
```

### The Complete Mental Model

```
┌──────────────────────────────────────────────────────────┐
│                    YOUR BRAIN MODEL                       │
│                                                          │
│  1. TRIGGER                                              │
│     "Something happened" (push, PR, tag, schedule)       │
│              ↓                                           │
│  2. MATCH                                                │
│     "Does it match my workflow's on: rules?"             │
│     (right branch? right files changed?)                 │
│              ↓                                           │
│  3. PROVISION                                            │
│     "Spin up a fresh VM" (ubuntu/macos/windows)          │
│     It has NOTHING. Clean slate.                         │
│              ↓                                           │
│  4. EXECUTE                                              │
│     Run steps in order:                                  │
│     checkout → setup tools → YOUR COMMANDS → upload      │
│              ↓                                           │
│  5. GATE                                                 │
│     "Did it pass?"                                       │
│     YES → next job (deploy, release, notify)             │
│     NO  → STOP. Alert. Nothing ships.                    │
│              ↓                                           │
│  6. CLEANUP                                              │
│     VM is destroyed. Nothing persists.                   │
│     Only artifacts/deployments survive.                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### The One Rule That Matters Most

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   If it's not in the workflow file, it doesn't happen.    ║
║                                                           ║
║   Want tests? Add a step.                                 ║
║   Want linting? Add a step.                               ║
║   Want deployment? Add a job.                             ║
║   Want notifications? Add a step.                         ║
║                                                           ║
║   The workflow IS the definition of your pipeline.        ║
║   Nothing more, nothing less.                             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 26. Glossary

| Term | Definition |
|---|---|
| **CI** | Continuous Integration — automatically test/validate code on every push |
| **CD** | Continuous Delivery/Deployment — automatically ship code to production |
| **Pipeline** | The full sequence of automated steps (lint → test → build → deploy) |
| **Workflow** | A YAML file that defines a pipeline in GitHub Actions |
| **Job** | A group of steps that runs on ONE virtual machine |
| **Step** | A single command or action within a job |
| **Action** | A reusable module (like a library) used in a step |
| **Runner** | The machine (VM) that executes a job |
| **Trigger** | The event that starts a workflow (push, PR, tag, etc.) |
| **Artifact** | A file produced by a job, stored by GitHub, downloadable |
| **Secret** | An encrypted variable stored in GitHub (passwords, keys) |
| **Environment** | A deployment target (staging, production) with optional approval |
| **Matrix** | Run the same job with multiple configurations in parallel |
| **Cache** | Stored dependencies reused across workflow runs for speed |
| **Concurrency** | Control that prevents multiple simultaneous runs |
| **OIDC** | OpenID Connect — secure token-based auth (used by Pages) |
| **YAML** | The file format used for workflow definitions |
| **Path filter** | Trigger a workflow only when specific files change |
| **Needs** | Job dependency — "run this job only after that job succeeds" |

---

## 27. What to Learn Next — The CD Path

Now that you understand CI, here's your learning path to full CD:

### Level 1: CI (You Are Here ✅)
```
✅ Understand workflows, jobs, steps
✅ Triggers and path filters
✅ Auto-validate and deploy static files
✅ GitHub Pages deployment
```

### Level 2: Android CI (Next)
```
→ Cache Gradle dependencies
→ Run unit tests in CI
→ Run lint checks
→ Build debug APK as artifact
→ PR status checks (block merge if CI fails)
```

### Level 3: Android CD (After That)
```
→ Sign release APK/AAB in CI (using secrets)
→ Upload to Firebase App Distribution (for testers)
→ Upload to Play Store Internal track
→ Automated screenshots with Fastlane
→ Version bumping automation
```

### Level 4: Advanced (Later)
```
→ Instrumented tests on emulator (CI)
→ Multi-module build optimization
→ Dynamic feature modules
→ A/B testing via Play Store staged rollout
→ Crashlytics + CI integration
→ Custom GitHub Actions (write your own)
→ Reusable workflows (share across repos)
→ Self-hosted runners (save cost at scale)
```

### Practical Next Steps for You

```
1. Push your sticker CDN → Done ✅
2. Add real sticker images, update _master.json, push
   → Watch CI validate + deploy automatically
3. In your Android Compose project, add:
   .github/workflows/android-ci.yml
   → Auto-build + test on every push
4. Add branch protection on main
   → Can't merge broken PRs
5. Tag releases: git tag v1.0.0
   → Auto-build signed APK
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS CHEAT SHEET                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  File location: .github/workflows/name.yml               │
│                                                          │
│  Trigger:     on: push / pull_request / workflow_dispatch│
│  Runner:      runs-on: ubuntu-latest                     │
│  Clone repo:  uses: actions/checkout@v4                  │
│  Java:        uses: actions/setup-java@v4                │
│  Node:        uses: actions/setup-node@v4                │
│  Cache:       uses: actions/cache@v4                     │
│  Upload:      uses: actions/upload-artifact@v4           │
│  Secrets:     ${{ secrets.MY_SECRET }}                   │
│  Condition:   if: github.ref == 'refs/heads/main'       │
│  Depends on:  needs: [job1, job2]                        │
│  Env var:     env: KEY: value                            │
│                                                          │
│  View logs:   GitHub → Actions → Click run → Click step  │
│  Re-run:      GitHub → Actions → Click run → Re-run      │
│  Manual run:  GitHub → Actions → Run workflow button      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

*Written for mid-level Android developers. Read once slowly, then use as reference.*
*Total reading time: ~45 minutes.*
