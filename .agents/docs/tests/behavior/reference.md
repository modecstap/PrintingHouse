# Reference: Behavior Tests

Facts for writing behavior tests. A behavior test checks what the system does as a user or the business sees it, not how it is built. How to apply this: [instructions](howto.md).

## Rules

### One test, one scenario

Each test checks one business rule or one user scenario. Never chain unrelated processes, such as login, password change, and account deletion, in one test.

### Describe behavior in business language

Name actions and results as the user or the business sees them. Never name internal classes, methods, fields, or database tables unless they are part of the contract.

### Context, action, result

Each test has a context (the state before the action), one action (by a user or an external system), and an expected result (what the system does). Given/When/Then is the usual form. The keywords are optional; the context, action, result order must stay clear.

### Assert the outcome, not that the action ran

Assert an observable result: status, message, available action, or changed state. Assert only what confirms this scenario, not every property of the result.

### No vague assertions

Never assert "the system works correctly", "the operation succeeded", "the data is processed correctly", or "the right information is shown". Name the concrete status, message, action, or change instead.

## Quality Properties

- Independent: does not depend on the run order of other tests.
- Repeatable: same conditions, same result.
- Isolated: does not use state left by other tests.
- Deterministic: no random delays or arbitrary waits.
- Minimal preconditions: creates only the data the scenario needs.
- Explicit assertions: checks a concrete expected result.
- Clear name: the name tells which behavior is checked.
- No extra detail: does not check internal mechanisms without need.

## Naming

Format: `should <expected behavior> [when <condition>]`. The name answers: under which conditions, which behavior is expected.

```text
should allow login with valid credentials
should reject login with an invalid password
should prevent checkout when the cart is empty
should apply a discount to an eligible order
```

The team's language is allowed. One style across the project matters more than the language.

## Scenario Categories

Consider each category for every important business rule:

- Positive: valid input, expected success. Example: correct credentials grant access.
- Negative: invalid input, refusal. Example: a wrong password is denied.
- Boundary: a value at a limit. Example: an empty password, or a password of the minimum allowed length.

Do not test every combination. Choose scenarios by business risk, requirements, and boundary conditions.

## Anti-Patterns

- Brittle test: depends on HTML structure, internal call order, or a specific implementation.
- Oversized scenario: one test covers several unrelated business processes.
- Weak assertion: the test passes while the actual result is wrong.
- Unstable data: the test depends on an environment or data that can change.
- Timer instead of synchronization: a fixed `sleep` where the test can wait for a specific event or state.
- Excess duplication: many tests check the same behavior with insignificant differences.
- Implementation instead of contract: the test fails after a safe refactor, although behavior did not change.

## Examples

### One scenario per test

Bad:

```text
should handle the user
  Given a user exists
  When the user logs in
  And changes the password
  And deletes the account
  Then everything works correctly
```

It covers three processes and asserts nothing concrete.

Good:

```text
should allow login with valid credentials
  Given the user is registered
  When the user enters valid credentials
  Then the user gets access to their account
```

### Business language

Bad:

```text
should set isAuthenticated on login
  When userService.login() is called
  Then isAuthenticated becomes true
```

It names a method and a field, so a behavior-preserving refactor breaks it.

Good:

```text
should open the account page after login with valid credentials
  When the user enters valid credentials
  Then the system opens the user's account page
```

### Outcome, not execution

Bad:

```text
should process the order
  When the user places an order
  Then the order is processed
```

"Processed" passes whatever the actual result is.

Good:

```text
should create an order when the item is in stock
  When the user places an order for an item in stock
  Then the order is created
  And the user sees the order number
  And the item is reserved
```
