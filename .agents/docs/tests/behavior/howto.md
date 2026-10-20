# How to Write a Behavior Test

Steps for an agent writing behavior tests for one business rule. Rules and examples: [reference](reference.md).

Running example: a user places an order; the order is created only for an item in stock.

## Pick the Scenarios

1. Take the business rule from the requirements or acceptance criteria.
2. List a positive, a negative, and a boundary scenario for it. See [Scenario categories](reference.md#scenario-categories).
3. Keep the scenarios that cover a business risk, a requirement, or a boundary. Drop scenarios that differ only in insignificant details.
4. Plan one test per scenario. See [One test, one scenario](reference.md#one-test-one-scenario).

Example:

```text
should create an order when the item is in stock
should reject an order when the item is out of stock
should create an order for the last item in stock
```

## Name the Test

Name each test `should <expected behavior> [when <condition>]`. See [Naming](reference.md#naming).

## Write the Context (Given)

1. Create only the data this scenario needs.
2. Create it inside the test. Never rely on state from other tests or a shared environment.

Example: `Given the cart holds an item in stock` and `And the user is logged in`. No order history, no extra items.

## Write the Action (When)

Write one action by a user or an external system, in business language. Never call internal methods or name classes unless they are the contract. See [Describe behavior in business language](reference.md#describe-behavior-in-business-language).

Example: `When the user confirms the order`, not `When orderService.create() is called`.

## Write the Assertions (Then)

1. Assert the observable result: status, message, available action, or changed state. See [Assert the outcome](reference.md#assert-the-outcome-not-that-the-action-ran).
2. Assert only what confirms this scenario.
3. Replace vague words ("correctly", "successfully", "processed") with the concrete result. See [No vague assertions](reference.md#no-vague-assertions).

Example: `Then the order has status "Created"` and `And the user sees the order confirmation`, not `Then the order is processed`.

## Synchronize on State

When the result arrives asynchronously, wait for the specific event or state. Never use a fixed `sleep`.

## Review the Test

Check each item and fix any failure:

- Passes in any run order and on repeated runs.
- Fails when the actual result is wrong.
- Survives a refactor that keeps behavior.
- The name alone tells which behavior is checked.
- Does not depend on HTML structure, internal call order, or changing data.

See [Quality properties](reference.md#quality-properties) and [Anti-patterns](reference.md#anti-patterns).

Result:

```text
should create an order when the item is in stock
  Given the cart holds an item in stock
  And the user is logged in
  When the user confirms the order
  Then the order has status "Created"
  And the user sees the order confirmation
```

The test holds preconditions, one action, and observable results. It does not depend on whether the system uses a REST API, a message queue, or a specific database.
