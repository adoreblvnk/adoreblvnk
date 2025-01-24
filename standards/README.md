<div align="center"> <!-- use align as CSS is not allowed on GitHub markdown https://github.com/orgs/community/discussions/22728 -->
  <h1>Rules & Resources</h1> <!-- Project Name -->
  <p> <!-- Description -->
    A set of standards, best practices, & guidelines for software developers.
  </p>
</div>

---

<details>
<summary>Table of Contents</summary>

- [About](#about)
- [Standards](#standards)
  - [Git](#git)
    - [Commit Message Format: Angular's Commit Message Format](#commit-message-format-angulars-commit-message-format)
    - [Semantic Versioning: Semantic Versioning](#semantic-versioning-semantic-versioning)
- [Best Practices](#best-practices)
  - [Project Template: adore\_blvnk's Project Template](#project-template-adore_blvnks-project-template)
- [Guidelines](#guidelines)
</details>

## About

Consistency in software development eases readability and understanding. This reduces the learning curve when coming back or collaborating with others in a codebase. But how is consistency established when there's nuance in everything? I personally believe there are 3 ways to establish this:

1. Standards. I borrow the definition from [ISO standards](https://www.iso.org/standards.html), where standards are a set of rules to be strictly followed without deviation. Because of the "strictness", new standards must go through rigorous testing before being added.
2. Best Practices. The definition for both "Best Practice" and "Guideline" is best defined in this [W3C email](https://lists.w3.org/Archives/Public/public-ldp-wg/2013Jul/0006.html), although Wikipedia definitions for "[Best Practice](https://wikipedia.org/wiki/Coding_best_practices)" and "[Guideline](https://wikipedia.org/wiki/Guideline)" are also accepted for clarification purposes. Best Practices are methods or techniques that consistently show results superior to those achieved with other means and are used as a benchmark. Best Practices are opinionated, in other words, they are specific, and if not applicable to your use case, then developer discretion can be applied on whether Best Practices should be adhered to.
3. Guidelines. A Guideline is a tip, a trick, a note, a suggestion, or answer to a frequently asked question. These are personal tips that can be ignored if a better implementation exists. Hence, guidelines can change frequently.

## Standards

### Git

#### Commit Message Format: [Angular's Commit Message Format](https://github.com/angular/angular/blob/main/CONTRIBUTING.md)

To adhere strictly to for all Git commits, and "type" field must be strictly be in [types](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#type).

#### Semantic Versioning: [Semantic Versioning](https://semver.org/#is-v123-a-semantic-version)

To adhere strictly to for all releases. Note that the "v" prefix is still used for [git tag](https://git-scm.com/docs/git-tag) names in the following format:

```bash
git tag v1.2.3 -m "Release version 1.2.3"
```

Each release is to be documented in CHANGELOG, which is in the format of [keep a changelog](https://keepachangelog.com/en/1.1.0).

## Best Practices

### Project Template: [adore_blvnk's Project Template](./../project_template/README.md)

Omit sections from README as necessary.

## Guidelines

## Credits <!-- omit in toc -->

- [adore_blvnk](https://x.com/adore_blvnk)
