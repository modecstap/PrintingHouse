# How to write a Conventional Commit message

Use this guide when you need to produce a commit message that follows [Conventional Commits 1.0.0](https://www.conventionalcommits.org/). One commit, one clear intent.

## When to use

Write a Conventional Commit whenever the change will land in history that tools or humans consume for changelogs, version bumps, or review. Prefer one type per commit. If the change fits more than one type, split into multiple commits when possible.

## 1. Choose the type

Pick a noun that states intent:

| Type | Use when |
|------|----------|
| `feat` | You add a new feature |
| `fix` | You patch a bug |
| Other | Allowed (for example `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test`) |

`feat` and `fix` drive SemVer (MINOR / PATCH). Other types do not imply a SemVer bump unless they include a breaking change.

## 2. Add an optional scope

If the change targets one area of the codebase, put a noun in parentheses after the type:

```text
feat(parser):
fix(api):
```

Skip the scope when it adds no useful context.

## 3. Write the description

After the type (and optional scope), write a colon, a space, then a short summary of the change:

```text
fix: array parsing issue when multiple spaces were contained in string
docs: correct spelling of CHANGELOG
feat(lang): add Polish language
```

Keep the description as the one-line summary. Put detail in the body if needed.

## 4. Add an optional body

Leave one blank line after the description. Then write free-form context: why, how, trade-offs. Multiple paragraphs are fine.

```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.
```

## 5. Mark a breaking change (if any)

Indicate a breaking API change in one or both of these ways:

- Put `!` immediately before the `:` in the type/scope prefix. The description then describes the break. A `BREAKING CHANGE:` footer may be omitted.
- Add a footer: `BREAKING CHANGE: <description>` (uppercase token required).

```text
feat!: send an email to the customer when a product is shipped

feat(api)!: send an email to the customer when a product is shipped

feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files

feat!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

A breaking change may appear on any type, not only `feat` or `fix`.

## 6. Add optional footers

After the body (or after the description if there is no body), leave one blank line, then add one or more footers. Each footer is a token, then `:<space>` or `<space>#`, then a value (git-trailer style). Use `-` instead of spaces in tokens, except `BREAKING CHANGE` (and synonym `BREAKING-CHANGE`).

```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request.

Reviewed-by: Z
Refs: #123
```

## Checklist before you commit

- [ ] Type is a noun (`feat`, `fix`, or another agreed type)
- [ ] Optional scope is a noun in parentheses
- [ ] Optional `!` sits immediately before `:` if the change breaks the API
- [ ] Colon and space precede the description
- [ ] Description is a short summary of the change
- [ ] Body (if any) starts one blank line after the description
- [ ] Footers (if any) start one blank line after the body; tokens use `-` for spaces (except `BREAKING CHANGE`)
- [ ] Breaking change is marked with `!` and/or a `BREAKING CHANGE:` footer
- [ ] One primary intent per commit; split mixed intents when possible

## Examples

**Feature with scope**

```text
feat(lang): add Polish language
```

**Docs, description only**

```text
docs: correct spelling of CHANGELOG
```

**Breaking change via `!`**

```text
feat!: send an email to the customer when a product is shipped
```

**Breaking change via footer**

```text
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

**Fix with body and footers**

```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

**Revert (common convention; not mandated by the core types)**

```text
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

For exact MUST/MAY rules and SemVer mapping, see [conventional-commits-reference.md](./conventional-commits-reference.md).
