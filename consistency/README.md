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
  - [Git](#git)
    - [🔴 Commit Message Format by Angular](#-commit-message-format-by-angular)
    - [🟠 Conventional Branch](#-conventional-branch)
    - [🔴 Semantic Versioning](#-semantic-versioning)
  - [Go](#go)
    - [🔴 gofmt for Go Style Guide](#-gofmt-for-go-style-guide)
    - [🟠 Go Best Practices](#-go-best-practices)
  - [JavaScript](#javascript)
    - [🟠 Prettier Code Formatter](#-prettier-code-formatter)
  - [Python](#python)
    - [🟠 autopep8 for PEP 8](#-autopep8-for-pep-8)
  - [Rust](#rust)
    - [🔴 rustfmt Formatter](#-rustfmt-formatter)
    - [🔴 Clippy Linter](#-clippy-linter)
  - [Shell](#shell)
    - [🟢 ShellCheck](#-shellcheck)
    - [🔴 shfmt for Shell Style Guide](#-shfmt-for-shell-style-guide)
  - [Miscellaneous](#miscellaneous)
    - [🟠 Project Template by adore\_blvnk](#-project-template-by-adore_blvnk)
- [Digital Life](#digital-life)
  - [OS Post-install](#os-post-install)
    - [🟢 Linux (Debian / Ubuntu)](#-linux-debian--ubuntu)
    - [🟢 Windows](#-windows)
    - [🟢 Android](#-android)
  - [Miscellaneous](#miscellaneous-1)
    - [🟢 Password Manager Vault Structure](#-password-manager-vault-structure)
</details>

## About

[Consistency](https://www.tuple.nl/en/knowledge-base/consistency) in software development eases readability, maintainability, and collaboration between teams. Consistency attains cognitive fluency, as developers process information better when encountering predictable patterns. Furthermore, consistent code reduces the learning curve during collaboration and maintenance.

Enforcing consistency is achieved via defining a clear set of **Standards**, **Best Practices**, and **Guidelines**.

1. Standards. I borrow the definition from [ISO standards](https://www.iso.org/standards.html), where standards are a set of rules to be **strictly followed** without deviation. Because of the "strictness", new standards must go through rigorous testing before being added.
2. Best Practices. The definition for both "Best Practice" and "Guideline" is best defined in this [W3C email](https://lists.w3.org/Archives/Public/public-ldp-wg/2013Jul/0006.html), although Wikipedia definitions for "[Best Practice](https://wikipedia.org/wiki/Coding_best_practices)" and "[Guideline](https://wikipedia.org/wiki/Guideline)" are also accepted for clarification purposes. Best Practices are methods or techniques that consistently show results superior to those achieved with other means and are used as a benchmark. Best Practices are **opinionated**, in other words, they are specific, and if not applicable to your use case, developer discretion can be applied on whether Best Practices should be adhered to.
3. Guidelines. A Guideline is a tip, a trick, a note, a suggestion, or answer to a frequently asked question. These are personal tips that **can be ignored** if a better implementation exists. Hence, guidelines can change frequently.

Philosophically, consistency has also applied in daily life via habits and schedules. **Documenting** them creates accountability and helps identify iterative improvement over inefficiencies in said habits and schedules.

In this document, 🔴 = Standards, 🟠 = Best Practices, and 🟢 = Guidelines.

## Software Development

### [Git](https://git-scm.com)

#### 🔴 [Commit Message Format](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md) by Angular

"type" field must be strictly be in [types](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md#type).

**Pull Request Naming Convention**

PR commits should be [squashed and merged](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges#squash-and-merge-your-commits) to create a single meaningful clean commit. With this, the PR name is the commit message, & should follow [Commit Message Format](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md).

#### 🟠 [Conventional Branch](https://conventional-branch.github.io)

Follow [Branch Naming Prefixes](https://conventional-branch.github.io/#branch-naming-prefixes) when creating branches.

When contributing to other projects & creating PRs, if the project has another branch naming specification, use that.

#### 🔴 [Semantic Versioning](https://semver.org)

"v" prefix is still used for [git tag](https://git-scm.com/docs/git-tag) names in the following format as documented in [Is "v1.2.3" a semantic version?](https://semver.org/#is-v123-a-semantic-version):

```bash
git tag v1.2.3 -m "Release version 1.2.3"
```

Each release is to be documented in CHANGELOG, which is in the format of [keep a changelog](https://keepachangelog.com/en/1.1.0).

### [Go](https://go.dev)

#### 🔴 [gofmt](https://pkg.go.dev/cmd/gofmt) for [Go Style Guide](https://google.github.io/styleguide/go/guide)

Google's official [Go Style Guide](https://google.github.io/styleguide/go/guide) is enforced by [gofmt](https://pkg.go.dev/cmd/gofmt), the official Go formatter.

#### 🟠 [Go Best Practices](https://google.github.io/styleguide/go/best-practices)

[Go Best Practices](https://google.github.io/styleguide/go/best-practices) documents some of the patterns that have evolved over time that solve common problems, read well, and are robust to code maintenance needs.

### JavaScript

#### 🟠 [Prettier](https://prettier.io) Code Formatter

JavaScript unfortunately does not have a definitive style guide. However, [Prettier](https://prettier.io), the most popular formatter, loosely documents its choices when it comes to formatting in its [rationale](https://prettier.io/docs/en/rationale).

### [Python](https://python.org)

#### 🟠 [autopep8](https://github.com/hhatto/autopep8) for [PEP 8](https://peps.python.org/pep-0008)

[PEP 8](https://peps.python.org/pep-0008) is the official style guide for Python. Despite being relatively unopinionated, [autopep8](https://github.com/hhatto/autopep8) is the chosen formatter as [black](https://github.com/psf/black) sacrifices readability for consistency. As stated in [PEP 8](https://peps.python.org/pep-0008), "sometimes style guide recommendations just aren’t applicable. When in doubt, use your best judgment."

### [Rust](https://www.rust-lang.org)

#### 🔴 [rustfmt](https://github.com/rust-lang/rustfmt) Formatter

[Rust Style Guide](https://doc.rust-lang.org/style-guide/index.html) defines the default Rust style. The official code formatter is [rustfmt](https://github.com/rust-lang/rustfmt).

```
cargo fmt
```

#### 🔴 [Clippy](https://github.com/rust-lang/rust-clippy) Linter

[`cargo check`](https://doc.rust-lang.org/cargo/commands/cargo-check.html) helps to check that the code compiles successfully first. Thereafter, [Clippy](https://github.com/rust-lang/rust-clippy) is the official linter for Rust & it can be used in conjunction with [`cargo check`](https://doc.rust-lang.org/cargo/commands/cargo-check.html).

```
cargo check && cargo clippy
```

### [Shell](https://www.gnu.org/software/bash)

#### 🟢 [ShellCheck](https://www.shellcheck.net)

A static analysis tool for shell scripts.

#### 🔴 [shfmt](https://github.com/mvdan/sh) for [Shell Style Guide](https://google.github.io/styleguide/shellguide.html)

Google's Shell Style Guide is the most popular style guide for Shell. Formatted by [shfmt](https://github.com/mvdan/sh) with the following flags as specified in the documentation [examples](https://github.com/mvdan/sh/blob/master/cmd/shfmt/shfmt.1.scd#examples):

```bash
shfmt -i 2 -ci -bn
```

### Miscellaneous

#### 🟠 [Project Template](./../project_template/README.md) by adore_blvnk

A project template for personal use. Contains a README and CHANGELOG. Omit sections from README as necessary.

## Digital Life

### OS Post-install

#### 🟢 Linux (Debian / Ubuntu)

[cozydot](https://github.com/adoreblvnk/cozydot) is an automated post-install, update, & config (dotfile) manager for Linux. In the context of consistency, cozydot maintains consistency between multiple systems & ensures reliability by tracking changes made, thus reducing potential errors while setting up.

#### 🟢 Windows

[cozydot](https://github.com/adoreblvnk/cozydot) supports WSL too.

#### 🟢 Android

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
