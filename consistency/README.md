<div align="center"> <!-- use align as CSS is not allowed on GitHub markdown https://github.com/orgs/community/discussions/22728 -->
  <h1>Consistency</h1> <!-- Project Name -->
  <p> <!-- Description -->
    A set of standards, best practices, & guidelines for software developers & a digital life.
  </p>
</div>

---

<details>
<summary>Table of Contents</summary>

- [About](#about)
- [Software Development](#software-development)
  - [Docker](#docker)
  - [Git](#git)
  - [Go](#go)
  - [HTML / CSS](#html--css)
  - [JavaScript](#javascript)
  - [Markdown](#markdown)
  - [Python](#python)
  - [Rust](#rust)
  - [Shell](#shell)
  - [YAML](#yaml)
  - [Miscellaneous](#miscellaneous)
- [Digital Life](#digital-life)
  - [Linux (Debian / Ubuntu)](#linux-debian--ubuntu)
  - [Windows](#windows)
  - [Android](#android)
  - [Miscellaneous](#miscellaneous-1)
</details>

## About

[Consistency](https://www.tuple.nl/en/knowledge-base/consistency) in software development eases readability, maintainability, and collaboration between teams. Consistency attains cognitive fluency, as developers process information better when encountering predictable patterns. Furthermore, consistent code reduces the learning curve during collaboration and maintenance.

Enforcing consistency is achieved via defining a clear set of **Standards**, **Best Practices**, and **Guidelines**.

1. Standards. I borrow the definition from [ISO standards](https://www.iso.org/standards.html), where standards are a set of rules to be **strictly followed** without deviation. Standards must be explicitly defined and not open to interpretation. Because of the "strictness", new standards must go through rigorous testing before being added.
2. Best Practices. The definition for both "Best Practice" and "Guideline" is best defined in this [W3C email](https://lists.w3.org/Archives/Public/public-ldp-wg/2013Jul/0006.html), although Wikipedia definitions for "[Best Practice](https://wikipedia.org/wiki/Coding_best_practices)" and "[Guideline](https://wikipedia.org/wiki/Guideline)" are also accepted for clarification purposes. Best Practices are methods or techniques that consistently show results superior to those achieved with other means and are used as a benchmark. Best Practices are **opinionated**, in other words, they are specific, and if not applicable to your use case, developer discretion can be applied on whether Best Practices should be adhered to.
3. Guidelines. A Guideline is a tip, a trick, a note, a suggestion, or answer to a frequently asked question. Guidelines are typically not explicitly defined. These are personal tips that **can be ignored** if a better implementation exists. Hence, guidelines can change frequently.

Philosophically, consistency has also applied in daily life via habits and schedules. **Documenting** them creates accountability and helps identify iterative improvement over inefficiencies in said habits and schedules.

**How to use / contribute this document:**

This document is a collection of **official** Standards, Best Practices, and Guidelines, and does not include unofficial recommendations. Each item must be For each item, my personal interpretation of what / how / why is included.

In this document, &#x1F534; = Standards, &#x1F7E1; = Best Practices, and &#x1F7E2; = Guidelines.

## Software Development

### [Docker](https://www.docker.com)

#### 🟡 [Building best practices](https://docs.docker.com/build/building/best-practices) for Dockerfile

A collection of Dockerfile best practices & optimizations for Dockerfile instructions. Apply developer discretion, as certain "best practices" are optional (eg "Build and test your images in CI").

### [Git](https://git-scm.com)

#### 🔴 [commitlint](https://commitlint.js.org) for [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0)

"type" field must be strictly be in [type-enum](https://commitlint.js.org/reference/rules.html#type-enum). Since commitlint is based on [Commit Message Format](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md) by Angular, the type definition can be referenced here. For missing type definitions, refer to [types of conventional commits](https://graphite.dev/guides/understanding-using-conventional-commits#types-of-conventional-commits) by Graphite.

**Pull Request Naming Convention**

PR commits should be [squashed and merged](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#squash-and-merge-your-commits) to create a single meaningful clean commit. With this, the PR name is the commit message, & should follow Commit Message Format by Angular.

#### 🟡 [gitignore](https://github.com/github/gitignore) by GitHub

GitHub provides gitignore templates for each OS, language, & version. For monorepos / monoliths, place each gitignore inside each project.

#### 🔴 [keep a changelog](https://keepachangelog.com/en/1.1.0)

Document notable changes between each release inside CHANGELOG.md, which is in the format of [keep a changelog](https://keepachangelog.com/en/1.1.0).

#### 🔴 [Semantic Versioning](https://semver.org)

"v" prefix is still used for [git tag](https://git-scm.com/docs/git-tag) names in the following format as documented in [Is "v1.2.3" a semantic version?](https://semver.org/#is-v123-a-semantic-version):

```bash
git tag v1.2.3 -m "Release version 1.2.3"
```

**Guidelines for Tags & Releases**

- Keep the names of tags & (GitHub) releases consistent (eg "v1.2.3").
- If making a commit message for a tag / release, follow this convention. Note the lack of "v" in the version for messages.
  ```
  git commit -m "chore(release): 1.2.3"
  ```
  - *Reference: [Determine the version bump](https://nx.dev/recipes/nx-release/automatically-version-with-conventional-commits#determine-the-version-bump) by Nx, [Community configurations](https://semantic-release.gitbook.io/semantic-release/extending/shareable-configurations-list#community-configurations) by semantic-release*


### [Go](https://go.dev)

#### 🟡 [Go Best Practices](https://google.github.io/styleguide/go/best-practices)

[Go Best Practices](https://google.github.io/styleguide/go/best-practices) documents some of the patterns that have evolved over time that solve common problems, read well, and are robust to code maintenance needs.

#### 🔴 [gofmt](https://pkg.go.dev/cmd/gofmt) Formatter for [Go Style Guide](https://google.github.io/styleguide/go/guide)

Google's official [Go Style Guide](https://google.github.io/styleguide/go/guide) is enforced by [gofmt](https://pkg.go.dev/cmd/gofmt), the official Go formatter.

#### 🔴 [Staticcheck](https://staticcheck.dev) Linter

State of the art linter for Go.

#### 🟢 [Standard Go Project Layout](https://github.com/golang-standards/project-layout)

Basic layout for medium to complex Go application projects.

### HTML / CSS

#### 🟢 [HTML ESLint](https://html-eslint.org) & [CSS](https://github.com/eslint/css) Plugin for [ESLint](https://eslint.org) Linter

Note that ESLint released [official support for CSS linting](https://eslint.org/blog/2025/02/eslint-css-support).

#### 🟡 [Prettier](https://prettier.io) Code Formatter with [Google Style Guide](https://google.github.io/styleguide/htmlcssguide.html)

See [this](#-prettier-code-formatter-with-airbnb-style-guide) for handling conflicts between Prettier & a style guide.

### JavaScript

#### 🔴 [ESLint](https://eslint.org) Linter

Most popular JavaScript linter.

#### 🟢 [JSDoc](https://jsdoc.app)

API documentation generator for JavaScript via code comments. Imperative to document classes, methods, functions & constants (configs).

#### 🔴 [Prettier](https://prettier.io) Code Formatter with [Airbnb Style Guide](https://github.com/airbnb/javascript)

[Prettier](https://prettier.io) unfortunately does not have a definitive style guide but documents its formatting choices in its [rationale](https://prettier.io/docs/en/rationale).

Note the use of "X Code Formatter **with** Y Style Guide". Write code according to a style guide (eg Airbnb's Style Guide), & in case of conflicts, prefer Prettier.

### Markdown

[CommonMark](https://commonmark.org), the official specification, has not reached maturity (latest version is [0.31.2](https://github.com/commonmark/commonmark-spec/releases) as of 2025). Hence, [GitHub Flavored Markdown](https://github.github.com/gfm) spec is used. Note that [GitHub Flavored Markdown](https://github.github.com/gfm) is a strict superset of [CommonMark](https://commonmark.org).

#### 🟡 [Prettier](https://prettier.io) Code Formatter with [Google Markdown Style Guide](https://google.github.io/styleguide/docguide/style.html)

See [this](#-prettier-code-formatter-with-airbnb-style-guide) for handling conflicts between Prettier & a style guide. NOTE: As of 2025, Prettier deletes the closing tag in a Table of Contents, make sure to restore it.

### [Python](https://python.org)

#### 🔴 [Ruff](https://docs.astral.sh/ruff) Linter & Code Formatter

[Ruff](https://docs.astral.sh/ruff) performs linting, formatting, & import sorting, reducing toolchain complexity. [Ruff](https://docs.astral.sh/ruff) is a [drop-in replacement for Black](https://astral.sh/blog/the-ruff-formatter), which loosely follows [PEP 8](https://peps.python.org/pep-0008).

#### 🔴 [uv](https://docs.astral.sh/uv) Python Package Manager

[uv](https://docs.astral.sh/uv) is a Python package & project manager (eg via `uv init`).

**But what about [pip](https://pip.pypa.io) / [pipx](https://pipx.pypa.io)?**

While [uv](https://docs.astral.sh/uv) is intended to be a [drop-in replacement for pip](https://docs.astral.sh/uv/pip/compatibility), certain differences exist. In general, use `uv add` instead of `pip` & `uvx` (`uv tool run`) instead of `pipx`.

### [Rust](https://www.rust-lang.org)

#### 🔴 [Clippy](https://github.com/rust-lang/rust-clippy) Linter

[`cargo check`](https://doc.rust-lang.org/cargo/commands/cargo-check.html) helps to check that the code compiles successfully first. Thereafter, [Clippy](https://github.com/rust-lang/rust-clippy) is the official linter for Rust & it can be used in conjunction with [`cargo check`](https://doc.rust-lang.org/cargo/commands/cargo-check.html).

```
cargo check && cargo clippy
```

#### 🔴 [rustfmt](https://github.com/rust-lang/rustfmt) Formatter for the [Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide)

[Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide) defines the default Rust style. The official code formatter is [rustfmt](https://github.com/rust-lang/rustfmt).

```
cargo fmt
```

### [Shell](https://www.gnu.org/software/bash)

#### 🟢 [ShellCheck](https://www.shellcheck.net) Linter

A static analysis tool for shell scripts.

#### 🔴 [shfmt](https://github.com/mvdan/sh) Formatter for [Shell Style Guide](https://google.github.io/styleguide/shellguide.html)

Google's Shell Style Guide is the most popular style guide for Shell. [shfmt](https://github.com/mvdan/sh) formats with the following flags as specified in the documentation [examples](https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd#examples):

```bash
shfmt -i 2 -ci -bn
```

### [YAML](https://yaml.org)

#### 🟡 [Prettier](https://prettier.io) Code Formatter

The [YAML spec](https://yaml.org/spec/1.2.2) does not dictate a style guide, but YAML is self-explanatory.

### Miscellaneous

#### 🟢 [Project Template](./../project_template/README.md) by [adore_blvnk](https://x.com/adore_blvnk)

A project template for personal use. Contains a README and CHANGELOG. Omit sections from README as necessary.

## Digital Life

### Linux (Debian / Ubuntu)

[cozydot](https://github.com/adoreblvnk/cozydot) is an automated post-install, update, & config (dotfile) manager for Linux. In the context of consistency, cozydot maintains consistency between multiple systems & ensures reliability by tracking changes made, thus reducing potential errors while setting up.

### Windows

Guide for installing Windows 11 & post-install.

1. Install Windows 11. Bypass network connection by opening Command Prompt with <kbd>Shift</kbd> + <kbd>F10</kbd>, then running `OOBE\BYPASSNRO`.
2. After install finishes, install updates & drivers via Settings.
3. Run [Win11Debloat](https://github.com/Raphire/Win11Debloat) with standard options.
4. Install [Office C2R](https://gravesoft.dev/office_c2r_links), then activate with [Microsoft Activation Scripts](https://massgrave.dev).
5. Install [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) dependency.
6. Enable [Hyper-V](https://learn.microsoft.com/en-us/windows/wsl/faq#is-wsl-2-available-on-windows-10-home-and-windows-11-home-), then [install WSL](https://learn.microsoft.com/en-us/windows/wsl/install) with `wsl --install`.
7. Download your preferred [NerdFont](https://www.nerdfonts.com/font-downloads) & [add font](https://support.microsoft.com/en-us/office/add-a-font-b7c5f17c-4426-4b53-967f-455339c564c1).

**Installing Apps**

1. Git (Windows & WSL):
   1. Install [Git for Windows](https://git-scm.com/downloads/win). Copy this [`.gitconfig`](https://github.com/adoreblvnk/cozydot/blob/master/dotfiles/bash/.gitconfig) over to both Windows & WSL.
      - _NOTE: If GPG is not desired, remove lines pertaining to GPG._
   2. Generate a GPG signing key on Windows:
      1. Download [Gpg4win](https://www.gpg4win.org).
         - _Reference: Storing GPG passphrase in [Signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)_
      2. [Generate a new GPG key](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key) & copy the key ID from [tell Git about your signing key](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key).
      3. Export signing key & owner trust with:
         ```powershell
         gpg --export-ownertrust > otrust.txt; gpg --export <key ID> > private.asc
         ```
   3. Use Gpg4win on WSL by creating a symlink:
      ```bash
      sudo ln -s "/mnt/c/Program Files (x86)/GnuPG/bin/gpg.exe" /usr/local/bin/gpg
      ```
      - _NOTE: Same GPG program is used for Windows & WSL, which is recommended but may have issues for [file permissions](https://learn.microsoft.com/en-us/windows/wsl/file-permissions)_
   4. Restart WSL, then import GPG key & owner trust on WSL with:
      ```bash
      gpg --import-ownertrust /mnt/c/Users/<otrust path>; gpg --import /mnt/c/Users/<private.asc path>
      ```
   5. On both Windows & WSL `.gitconfig`, set your username, email, & the signingkey (key ID).
   6. On Windows, run:
      ```powershell
      git config --global credential.credentialStore wincredman
      git config --global credential.helper "C:/Program\ Files/Git/mingw64/bin/git-credential-manager.exe" # or git credential-manager configure
      git config --global gpg.program "C:/Program Files (x86)/GnuPG/bin/gpg.exe"
      ```
      - _Reference: [Credential stores](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/credstores.md#credential-stores)_
   7. On WSL, to use Windows' GCM (& GPG pinentry) in WSL, run:
      ```bash
      git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"
      git config --global gpg.program "/mnt/c/Program Files (x86)/GnuPG/bin/gpg.exe"
      ```
      - _Reference: [Configuring WSL for Git with Windows](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/wsl.md#configuring-wsl-with-git-for-windows-recommended)_
2. VS Code (Windows & WSL):
   1. Install VS Code & the WSL extension as per [developing in WSL](https://code.visualstudio.com/docs/remote/wsl).
3. Docker (Windows & WSL):
   1. Follow the steps in [turn on Docker Desktop WSL 2](https://docs.docker.com/desktop/features/wsl/#turn-on-docker-desktop-wsl-2) to install Docker Desktop for Windows & use WSL 2 based engine.
   2. [Optional] Follow the steps in [enabling Docker support in WSL 2 distributions](https://docs.docker.com/desktop/features/wsl/#enabling-docker-support-in-wsl-2-distributions) to enable Docker command in WSL by setting the default distro for WSL. This typically defaults to Ubuntu & does not require further action.
   - _NOTE: Follow [best practices](https://docs.docker.com/desktop/features/wsl/best-practices) to optimize your experience._
   - _NOTE: Set [logging driver to local](https://docs.docker.com/engine/logging/configure) in [daemon.json](https://docs.docker.com/desktop/settings-and-maintenance/settings/#docker-engine) to prevent disk exhaustion._

[cozydot](https://github.com/adoreblvnk/cozydot) supports WSL too.

### Android

### Miscellaneous

#### 🟢 Password Manager Vault Structure

The purpose of having a structured (sorted / tagged / labeled) vault is mainly aesthetical. Retrieving passwords should be done via search. Refer to Gmail's philosophy of [Search, don't sort](https://googlesystem.blogspot.com/2007/02/gmails-philosophy-today.html). Nevertheless, here is my vault structure:

- `banking 💳`: Also includes crypto logins. eg Coinbase, PayPal
- `commerce 🛍️`: eg Shein, Temu
- `credentials 📄`: eg Coursera, Credly
- `dev 👨‍💻`: For developer work. eg Claude, GitHub
- `emails ✉️`
- `entertainment 🎮`: eg Netflix, Steam
- `gov 🏛️`: For logins into government services
- `hardware ⚙️`: Laptop / phone logins & GPG / SSH keys
- `IDs 🪪`: Personal identification & family members
- `socials 🌐`: Social media. eg Discord, Instagram, X
- `utilities 🛠️`: Other random permanent logins. eg Mozilla, Strava
- `No Folder`: Temporary logins. eg uni applications

## Credits <!-- omit in toc -->

- [adore_blvnk](https://x.com/adore_blvnk)
