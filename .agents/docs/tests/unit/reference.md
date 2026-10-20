# Reference: Unit Tests

Facts for writing unit tests. A unit test checks the behavior of one small unit of code (a function, a class, a module) in isolation. How to apply this: [instructions](howto.md).

## Rules

### One test, one behavior

Each test checks one scenario and has one reason to pass or fail. Several asserts are allowed when they confirm the same behavior. Do not split one logical scenario into micro-tests.

### Independent

Each test creates its own starting state. The result never depends on which tests ran before. Isolate not only objects but also the database, files, global variables, the clock, and random values.

### Self-checking

Each test has an explicit success criterion and decides pass or fail by itself. Never rely on printed output, logs, or manual review.

### Fast

Unit tests run fast enough to run on every change. Never call a real network, an external API, a remote database, or slow infrastructure. If a test keeps needing heavy environment setup, revise the boundaries of the unit under test.

Integration tests check interactions between parts. They complement unit tests, never replace them.

### Behavior, not implementation

Assert the contract: the result, applied rules, rounding, raised errors. A test must keep passing after a refactor that keeps the result, such as replacing a loop with a library function.

Never assert how many times an internal method is called when it does not affect behavior. Assert an interaction with a dependency only when the interaction itself is the behavior. Example: a payment is sent exactly once.

### Simple

Test code is code to read, maintain, and change. Avoid:

- conditions and branching inside a test;
- several levels of helper functions without need;
- many mocks and complex setup;
- repeating the algorithm under test to compute the expected value;
- a generic test framework built for a few simple checks.

If testing one small method needs a lot of helper code, the unit is likely too complex or has too many dependencies.

## Naming

Format: `<unit> <expected behavior> [<condition>]`. The name tells which unit and which behavior is checked. Follow the case style and prefix of the test framework in use.

```text
user has name after creation
user can change email
discount is subtracted from price
adds negative and positive numbers
```

## Choosing What to Test

Write a short test list before starting. Derive cases from the contract and from likely errors, not from the number of code lines.

Example for a discount function:

- Price 100, discount 10%: result 90.
- Price 100, discount 0%: result 100.
- Price 100, discount 100%: result 0.
- Negative price: error or other result per the contract.
- Discount above the allowed maximum: error or capped discount per the contract.

Do not test every case from the list by default. Keep the cases that a requirement or a likely error justifies.

## Triangulation

One example may be enough to start an implementation, but not to prove the general rule. Add another example when the implementation could be fitted to the first one. Add only examples that tell the general rule apart from a special-case solution; do not pile up similar tests.

## When to Delete or Change a Test

A test suite does not have to keep growing. Delete or merge a test when:

- it checks the same behavior in the same way as another test;
- a stronger test already covers it;
- the checked detail is no longer part of the contract;
- it is bound to an outdated implementation, not to a requirement.

Never delete a test only because it blocks a refactor. First find what it protects: meaningful behavior or an internal detail.

## Examples

### One behavior per test

Bad:

```text
test: user
  user = User("Alex")
  assert user.name == "Alex"
  user.change_email("alex@example.com")
  assert user.email == "alex@example.com"
  user.deactivate()
  assert user.is_active == false
```

It checks creation, email change, and deactivation. A failure does not tell which behavior broke.

Good:

```text
test: user has name after creation
  user = User("Alex")
  assert user.name == "Alex"

test: user can change email
  user = User("Alex")
  user.change_email("alex@example.com")
  assert user.email == "alex@example.com"

test: user can be deactivated
  user = User("Alex")
  user.deactivate()
  assert user.is_active == false
```

### Independent state

Bad:

```text
shared user = User("Alex", email: "old@example.com")

test: user can change email
  user.change_email("new@example.com")
  assert user.email == "new@example.com"

test: user keeps initial email
  assert user.email == "old@example.com"
```

The second test depends on state the first one may have changed.

Good: create the user inside each test, or use a fixture that gives each test a fresh starting state.

### Explicit success criterion

Bad:

```text
test: discount
  result = calculate_discount(100, 10)
  print(result)
```

It runs the code but never checks the result.

Good:

```text
test: discount is subtracted from price
  result = calculate_discount(100, 10)
  assert result == 90
```

### Triangulation

First example:

```text
test: adds two numbers
  assert add(2, 3) == 5
```

An implementation that returns `5` passes it. A second example rules that out:

```text
test: adds negative and positive numbers
  assert add(-2, 3) == 1
```
