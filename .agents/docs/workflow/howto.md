# How to Implement a Task

Steps for an agent implementing one task. Stage results and rules: [reference guide](reference.md).

Running example: save a user draft, reject an empty body, and do not log the body.

## Take the Next Stage

1. Read that stage's result.
2. Produce the result.
3. Check that it can be shown: a list, a decision record, tests, or a passing command.
4. Leave unrelated code unchanged; record any deviation from the plan. See [Keep scope controlled](reference.md#keep-scope-controlled).
5. Start the next stage only after that check.

## Write Behavior Tests

1. Write a test for the normal case, each edge case from Analyze, and each failure scenario.
2. Assert what the caller observes: status, stored state, returned value, or error. Never assert private calls, branches, or structure. See [Tests first](reference.md#tests-first).
3. Write each test as in [How to write a behavior test](../tests/behavior/howto.md).

## Implement the Minimum

1. Write only the code the behavior tests and current requirements need. See [Keep the implementation minimal](reference.md#keep-the-implementation-minimal).
2. Run the behavior tests. Proceed when they pass.

Example: `saveDraft` rejects an empty body and a body over the limit, then inserts one row. No cache and no shared validator framework.

## Add Hardening Tests

1. For each of performance, concurrency, race conditions, resource limits, resilience, and failure recovery: add a test if this change can hit the risk; otherwise record why it cannot.
2. Prioritize by the architecture and expected workload. See [Harden based on risk](reference.md#harden-based-on-risk).

Example: two parallel saves of one draft must not corrupt the row. There is no shared in-memory cache, so a cache-stampede test does not apply.

## Harden

1. Change the implementation until the behavior and hardening tests pass.
2. Fix correctness, reliability, and resource management for those risks. Bound or release resources on the failure path.

Example: the store call uses one connection and closes it on timeout. A timed-out save leaves no partial row.

## Check Security

Check each item and record the result:

- Input validation, against the acceptance criteria.
- Authorization: a caller acts only on data they are allowed to use.
- Sensitive data: not logged, stored beyond the requirement, or returned to the wrong caller.
- The threat scenarios that apply to this change.

Example: the handler logs `draft saved: userId` and does not log the body. A user cannot read another user's draft.

## Refactor

1. Remove local duplication and simplify dependencies this change introduced.
2. Run the existing behavior tests without changing what they expect. See [Preserve behavior during refactoring](reference.md#preserve-behavior-during-refactoring).

Example: move the size check next to the empty check. The behavior tests stay green.

## Add Observability

Add logs, metrics, traces, or diagnostic events where they help. See [Make observability actionable](reference.md#make-observability-actionable).

1. Record the operation and the ids needed to find a failure.
2. On a request or job path, record latency and failures with a metric or trace.
3. Leave out secrets and sensitive data.
4. If no signal is appropriate, record why.

Example: log `saveDraft failed: userId=42 reason=timeout`, and emit `draft_save_seconds`. The body is absent from both.

## Update Documentation

Update what this change makes incomplete: public interfaces, configuration, operational procedures, important design decisions. If none changed, record that no update is required.

Example: document the `400` and `413` responses and the body size limit on the Draft API.

## Run the Check

1. Run the relevant test suites, including regression coverage for the behavior this change touches.
2. Run static analysis, formatting, linting, type checks, and the build where they apply. See [Automate verification](reference.md#automate-verification).
3. Confirm the Analyze constraints still hold: existing APIs, data formats, configuration, migrations, and clients. See [Verify compatibility](reference.md#verify-compatibility).
4. Keep the command results. A pass is the output, not a recollection.

The task is done when [Check](reference.md#check) passes.

## Return to an Earlier Stage

Use when a stage fails, or testing, review, or production feedback finds a problem. See [Do not skip failed checks](reference.md#do-not-skip-failed-checks).

1. Name the failed result.
2. Return to the earliest stage that can fix the cause, and fix it there.
3. Repeat verification for that stage and every later stage already completed.

Example: Check Security finds the draft body in an error log. Return to Add Observability, remove the body, then repeat Check Security and Run the Check.
