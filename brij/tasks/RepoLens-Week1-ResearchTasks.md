## Brij · research

Goal: prove the risky parts of the design work on our real Python repos, before we build them.

### Monday

**B1 · Project onboarding** → *Questions list*
- **What:** Read docs 11, 01 and 08, plus diagrams A1, A2, E3 and F1 in doc 10.
- **Why:** Every spike this week tests an assumption in these docs; you need the big picture first.
- **How:** Note questions and anything that looks inconsistent as you read; bring them to stand-up.

**B2 · Local setup + PostgreSQL 18 check** → *Setup notes*
- **What:** Install Docker, Python 3.13 + uv, Node 24 and pnpm; run PostgreSQL 18 with pgvector.
- **Why:** The database design relies on PostgreSQL 18 features and pgvector. If they don't work locally, setup stalls.
- **How:** Start the `pgvector/pgvector:pg18` container, enable the `vector` extension, and try a table with a vector column and index.

**B3 · GitLab API and OAuth** → *GitLab notes*
- **What:** Check that WCA GitLab gives us the data our API design expects.
- **Why:** Login, repo lists, branches and file reads all depend on GitLab. A blocker here affects everything.
- **How:** Use a personal token with `curl` on the endpoints in doc 05 §3. Ask an admin whether we can register an OAuth app and a clone-only service account.

### Tuesday

**B4 · Python project graph** → *Script + findings*
- **What:** A small script that draws a repo's package and module graph.
- **Why:** The Graph tab must come from real imports, not AI guesses.
- **How:** Read `pyproject.toml` / `requirements.txt`, scan `import` statements to link modules, and output a Mermaid graph. Note tricky cases (relative imports, several services in one repo).

**B5 · tree-sitter parsing** → *Script + findings*
- **What:** Try tree-sitter on Python files to extract classes, functions and imports.
- **Why:** It's how we'll understand code structure and split code into pieces for chat search.
- **How:** Install `py-tree-sitter`, parse about 10 files, then time a whole repo. Record anything it gets wrong.

### Wednesday

**B6 · Clone and hot files** → *Timings + hot-file list*
- **What:** Measure a fast "blobless" clone, and find the files that change most.
- **Why:** Clone speed drives analysis time; hot files drive the Test safety net score.
- **How:** Compare a normal clone with `--filter=blob:none`. Use `git log` over 6 months to count changes per file. Ask a repo owner if the top of the list looks right.

**B7 · lizard and gitleaks** → *Findings*
- **What:** Run the complexity checker and the secret scanner on the pilot repos.
- **Why:** They feed the Maintainability and Security scores; we need to know their speed and how noisy they are.
- **How:** Run both from the command line and review the output for false positives. Confirm secret values stay hidden (`--redact`).

**B8 · Package lookups** → *Findings*
- **What:** Check latest versions and known vulnerabilities for a repo's dependencies.
- **Why:** This feeds the Dependency hygiene score.
- **How:** Take the package list from B4 and query the OSV API and the PyPI JSON API. Note speed, limits and how severity is reported.

### Thursday

**B9 · Job queue + retry** → *Working spike*
- **What:** A tiny 3-step job that fails at step 2, then resumes from step 2 on retry.
- **Why:** "Retry from the failed step" is a core promise of the Run page.
- **How:** Combine Procrastinate with a LangGraph graph that uses the Postgres checkpointer. Stop the worker mid-run and see what happens.

**B10 · Summary and demo** → *Summary + 10-min demo*
- **What:** Turn the week's notes into recommendations.
- **Why:** Your findings decide what changes in the docs before we start building.
- **How:** One or two pages covering what worked, what didn't, what to change, and open risks.

### Friday (optional)

**B11 · pgvector search benchmark** → *Benchmark notes*
- Load about 20k test vectors and time filtered searches, to check chat search will stay fast.

---

## Henali · learning and research

Goal: understand the product, learn the basics, and produce useful inputs for the team.

### Monday

**H1 · What are we building?** → *Half-page note + word list*
- **What:** Read doc 11, sections 1–3, and explain RepoLens in your own words.
- **Why:** Explaining something simply is the fastest way to understand it.
- **How:** Skip technical words on the first read and write them in a list instead.

**H2 · Explore the designs** → *Page inventory*
- **What:** Go through every design page and note what it's for.
- **Why:** The team will build these screens; your inventory becomes our checklist.
- **How:** Open each page in a browser. For each, write its purpose, main buttons and what it shows, and add a screenshot.

### Tuesday

**H3 · Git basics** → *Link to your first merge request*
- **What:** Learn how the team shares work with Git and GitLab. 
- **Why:** Every piece of work, including notes, goes through a merge request.
- **How:** Follow a beginner Git tutorial. In the sandbox repo, create a branch, add your H1 note, and open a merge request for Brij to review.

**H4 · Team glossary** → *Glossary (25+ terms)*
- **What:** A simple dictionary of project terms.
- **Why:** It helps you now and every new joiner later.
- **How:** Start from doc 11 §9 and your word list. Write one simple line and one everyday example per term.

### Wednesday

**H5 · How websites work** → *Short notes*
- **What:** Learn what HTML, CSS and JavaScript each do, and what Next.js is.
- **Why:** RepoLens is a web app; this makes frontend discussions easier to follow.
- **How:** Use MDN's beginner guide, then the first chapters of the Next.js Learn course. Write 3–5 lines per topic.

**H6 · Data inventory** → *Data inventory table*
- **What:** List every piece of information each screen shows.
- **Why:** We'll build screens with sample data before the backend is ready; this list becomes that data.
- **How:** Use your page inventory and copy example values from the designs. Check it with Brij for 30 minutes.

### Thursday

**H7 · Similar tools** → *1-page comparison*
- **What:** Look at 3–4 code-quality tools, for example SonarQube, CodeScene, Codacy and Sourcegraph.
- **Why:** Learn what others show well, and what to avoid.
- **How:** Use their official sites and demo videos. For each, note who it's for, one idea to borrow and one thing to avoid.

**H8 · Show and tell** → *Short note or slides*
- **What:** A 5-minute share at the Thursday demo.
- **Why:** It's practice in explaining your work, and the team learns from a fresh view.
- **How:** Cover 3 things you learned, 1 thing that confused you, and 2 questions for next week.

### Friday (optional)

**H9 · Accessibility basics** → *Checklist*
- Read a beginner introduction to web accessibility, then check 2 design pages for colour contrast, keyboard use and text size.

