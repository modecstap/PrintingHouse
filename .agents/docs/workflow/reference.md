# Reference: Task Workflow

Facts for implementing one task. Each stage produces a verifiable result before the next starts. How to apply this: [instructions](howto.md).

## Stages

Run in this order.

### Behavior Tests

- Result: tests of expected feature behavior: normal cases, edge cases, and failure scenarios.
- Shown as: tests, built from the acceptance criteria and Design interfaces, that assert what a caller observes: status, stored state, returned value, error.

### Implement

- Result: a minimal working implementation that satisfies the behavior tests.
- Shown as: behavior tests pass.

### Harden Tests

- Result: tests for performance, concurrency, race conditions, resource limits, resilience, and failure recovery, where applicable.
- Shown as: a test for each risk this architecture and workload can hit; a stated reason for each risk that does not apply.

### Harden

- Result: correctness, reliability, and resource management are addressed.
- Shown as: behavior and hardening tests pass; resources are bounded or released on the failure path.

### Security

- Result: security requirements verified: input validation, authorization, sensitive data handling, and the threat scenarios that apply to this change.
- Shown as: a recorded check of each.

### Refactor

- Result: better structure, duplication removed, simpler dependencies, easier future changes; observable behavior unchanged.
- Shown as: the structure change; existing behavior tests pass without edits to expected behavior.

### Observability

- Result: logs, metrics, traces, and diagnostic events, where appropriate, to understand system behavior and troubleshoot failures.
- Shown as: the added signals, or a recorded reason none are appropriate.

### Documentation

- Result: affected documentation updated: public interfaces, configuration, operational procedures, important design decisions.
- Shown as: an update to each affected item, using the Design and final interfaces. If none apply, a recorded reason.

### Check

- Result: all required tests and quality checks pass: regressions, linting, type checks, and build.
- Shown as: passing results of the applicable commands.

## Rules

### Tests first

Write tests before implementation. Tests assert externally observable behavior, never private calls, branches, or structure. Behavior test rules: [reference](../tests/behavior/reference.md).

Stages: Behavior Tests, Implement.

### Keep the implementation minimal

Implement only what the behavior tests and current requirements need. No speculative abstractions, no premature optimization.

Stages: Design, Implement.

### Harden based on risk

Prioritize concurrency, performance, reliability, security, and resource usage by the system's architecture and expected workload. Test every real risk from the workload; spend no effort on a risk the architecture cannot hit.

Stages: Harden Tests, Harden, Security.

### Preserve behavior during refactoring

Refactoring makes no functional change. Existing behavior tests keep passing and are not rewritten to accept new behavior.

Stages: Refactor.

### Make observability actionable

Each signal must locate the failure, latency, bottleneck, or unexpected behavior. Never log secrets or sensitive data.

Stages: Observability.

### Automate verification

Run the applicable test suites, static analysis, formatting, linting, type checks, and build. Claim a pass only with a command result.

Stages: Check, and any stage that claims its tests pass.

### Do not skip failed checks

The workflow is iterative, not strictly linear. When a stage fails, or testing, review, or production feedback finds a problem, return to the earliest stage that can fix the cause and fix it there. Then repeat verification for that stage and every later stage already completed. Never start a later stage on a failed result.

Stages: all.

### Keep scope controlled

Make no change unrelated to the task. Record every necessary deviation from the original plan.

Stages: all, especially Implement and Refactor.

### Verify compatibility

Keep existing APIs, data formats, configuration, migrations, and clients working, unless a break is an accepted requirement.

Stages: Analyze, Design, Check.

## Examples

Task: save a user draft, reject an empty body, do not log the body.

### Behavior test

Bad:

```text
should call validate then insert when saving a draft
```

It names internal steps, so a behavior-preserving refactor breaks it.

Good:

```text
should return 400 and store nothing when the body is empty
should save a draft that can be read back when the body is valid
```

### Log line

Bad:

```text
saveDraft failed: userId=42 body="token sk-live-..." 
```

It logs the sensitive body, which holds a secret.

Good:

```text
saveDraft failed: userId=42 reason=timeout
```

The operation, id, and failure are enough to troubleshoot; the body is absent.
