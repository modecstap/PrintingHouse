# How to Write a Unit Test

Steps for an agent writing unit tests for one unit of code. Rules and examples: [reference](reference.md).

Running example: `calculate_discount(price, percent)` returns the price reduced by the discount percent.

## Build the Test List

1. Take the contract of the unit: inputs, outputs, errors.
2. List the cases: a typical value, limits, invalid input. See [Choosing what to test](reference.md#choosing-what-to-test).
3. Keep the cases that a requirement or a likely error justifies. Drop cases that check the same behavior.

Example:

```text
discount is subtracted from price      (100, 10)  -> 90
zero discount keeps price              (100, 0)   -> 100
full discount gives zero price         (100, 100) -> 0
negative price is rejected             (-1, 10)   -> error
```

## Name the Test

Name each test `<unit> <expected behavior> [<condition>]`. See [Naming](reference.md#naming).

## Write One Test per Behavior

1. Create the starting state inside the test or in a fixture that gives a fresh state. Never share mutable state between tests. See [Independent](reference.md#independent).
2. Call the unit once for the scenario.
3. Keep one reason to fail. Several asserts are fine when they confirm the same behavior. See [One test, one behavior](reference.md#one-test-one-behavior).

## Assert the Contract

1. Assert a concrete expected value. Never print the result instead. See [Self-checking](reference.md#self-checking).
2. Write the expected value as a literal. Never recompute it with the algorithm under test.
3. Assert the result, not internal calls. See [Behavior, not implementation](reference.md#behavior-not-implementation).

Example: `assert calculate_discount(100, 10) == 90`, not `assert result == price - price * percent / 100`.

## Isolate Dependencies

1. Replace the network, external APIs, remote databases, the clock, and random values with fakes or fixed values. See [Fast](reference.md#fast).
2. Mock a dependency only when the unit needs it, and assert the mock's calls only when the interaction is the behavior.
3. If setup grows large, report that the unit has too many dependencies instead of adding more helpers. See [Simple](reference.md#simple).

## Triangulate

If the implementation could pass by returning a fixed value, add a second example with different input. See [Triangulation](reference.md#triangulation).

Example: after `(100, 10) -> 90`, add `(200, 25) -> 150`.

## Review the Test

Check each item and fix any failure:

- Passes in any run order and on repeated runs.
- Fails when the actual result is wrong.
- Survives a refactor that keeps behavior.
- The name alone tells which unit and behavior are checked.
- No branching, no deep helpers, no recomputed expected values.
- No real network, external API, or remote database.

When an existing test blocks the change, see [When to delete or change a test](reference.md#when-to-delete-or-change-a-test).

Result:

```text
test: discount is subtracted from price
  assert calculate_discount(100, 10) == 90

test: discount is subtracted from price for another input
  assert calculate_discount(200, 25) == 150

test: negative price is rejected
  assert calculate_discount(-1, 10) raises error
```

Each test holds its own input, one call, and a literal expected result. None depends on how `calculate_discount` computes the value.
