# Conventional Commits 1.0.0 — reference

Information-oriented description of the Conventional Commits message format. Normative keywords follow RFC 2119: MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, OPTIONAL.

## Message structure

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

## Type

- Commits MUST be prefixed with a type: a noun such as `feat`, `fix`, etc.
- After the type come, in order: OPTIONAL scope, OPTIONAL `!`, then a REQUIRED colon and space.
- The type `feat` MUST be used when a commit adds a new feature.
- The type `fix` MUST be used when a commit represents a bug fix.
- Types other than `feat` and `fix` MAY be used (for example `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test`). Additional types are not mandated by the specification and have no implicit SemVer effect unless they include a breaking change.

## Scope

- A scope MAY be provided after the type.
- A scope MUST be a noun describing a section of the codebase, surrounded by parentheses, for example `fix(parser):`.

## Description

- A description MUST immediately follow the colon and space after the type/scope prefix.
- The description is a short summary of the code changes.

## Body

- A longer body MAY follow the description.
- The body MUST begin one blank line after the description.
- The body is free-form and MAY consist of any number of newline-separated paragraphs.

## Footers

- One or more footers MAY be provided one blank line after the body (or after the description if there is no body).
- Each footer MUST consist of a word token, followed by either `:<space>` or `<space>#`, followed by a string value (git-trailer style).
- A footer’s token MUST use `-` in place of whitespace, for example `Acked-by`. Exception: `BREAKING CHANGE` MAY be used as a token.
- A footer’s value MAY contain spaces and newlines. Parsing MUST terminate when the next valid footer token/separator pair is observed.
- Footers other than `BREAKING CHANGE: <description>` MAY be provided.

## Breaking changes

- Breaking changes MUST be indicated in the type/scope prefix, or as a footer entry, or both.
- As a footer: MUST be the uppercase text `BREAKING CHANGE`, then colon, space, and description, for example `BREAKING CHANGE: environment variables now take precedence over config files`.
- In the prefix: MUST be indicated by `!` immediately before `:`. If `!` is used, `BREAKING CHANGE:` MAY be omitted from the footer, and the description SHALL describe the breaking change.
- A breaking change MAY be part of a commit of any type.
- `BREAKING-CHANGE` MUST be synonymous with `BREAKING CHANGE` when used as a footer token.

## Case sensitivity

- Units of Conventional Commits information MUST NOT be treated as case-sensitive by implementors, except `BREAKING CHANGE`, which MUST be uppercase.

## SemVer mapping

| Commit signal | SemVer bump |
|---------------|-------------|
| `fix` | PATCH |
| `feat` | MINOR |
| Breaking change (`!` and/or `BREAKING CHANGE` footer), any type | MAJOR |

## Spec examples

**Description and breaking-change footer**

```text
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

**`!` in the prefix**

```text
feat!: send an email to the customer when a product is shipped
```

**Scope and `!`**

```text
feat(api)!: send an email to the customer when a product is shipped
```

**Both `!` and `BREAKING CHANGE` footer**

```text
feat!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

**No body**

```text
docs: correct spelling of CHANGELOG
```

**With scope**

```text
feat(lang): add Polish language
```

**Multi-paragraph body and multiple footers**

```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

For step-by-step authorship guidance, see [how-to-write-conventional-commits.md](./how-to-write-conventional-commits.md).
