# How to Instrument Code

Steps for an agent adding observability to new or changed code. Rules and examples: [reference](reference.md).

Running example: `checkout(order, context)` checks stock, charges the payment, and saves the order.

## Find What to Instrument

1. Find the critical path: the business operations whose failure or delay users notice.
2. Inside it, list each call across a system boundary. See [Where to add spans](reference.md#where-to-add-spans).
3. Call telemetry only through the [shared observability interface](reference.md#single-observability-interface), never a logging or tracing library directly from business code.

Example:

```text
checkout            critical path
  inventory.check   external API
  payment.charge    external API
  order.save        database
```

## Add Spans

1. Start one trace or root span for the operation, from the incoming context.
2. Wrap each boundary call in its own span. Name it `<component>.<action>`.
3. End every span, also on error. Record the status and the error. See [Traces](reference.md#traces).

## Propagate Context

1. Read `request_id` and `trace_id` from the incoming request in middleware.
2. Pass the context to every downstream call, queue message, and background job. See [Context propagation](reference.md#context-propagation).
3. Never use an incoming ID to identify the user.

## Log Events

1. Log the start and the end of the operation, and each failure.
2. Use a structured record with a stable `event` name, `request_id`, `trace_id`, and entity IDs. See [Logs](reference.md#logs).
3. Pick the level: `ERROR` for an unexpected failure, `WARN` for an expected business error, `INFO` for normal milestones, `DEBUG` for details.

## Record Metrics

1. Count both success and failure of the operation.
2. Record the duration as a histogram, for p95 and p99.
3. Take label values from a bounded set. Classify an error into a fixed `error_type` instead of using its message. See [Metrics](reference.md#metrics).

## Capture Errors

1. Capture the error with the operation name and entity IDs, then rethrow or handle it. See [Errors](reference.md#errors).
2. Keep the original cause when wrapping.
3. Do not report expected business errors as incidents.

## Instrument Async Work

For each queue or background job touched by the change:

1. Pass the context in the message.
2. Start a span in the consumer from that context.
3. Record `queue_depth`, `job_duration`, and `job_failures`. See [Queues and background jobs](reference.md#queues-and-background-jobs).

## Check Telemetry Safety

Check each new log field, span attribute, metric label, and error context:

- no passwords, tokens, keys, or cookies;
- personal data is masked or pseudonymized;
- no unbounded values in metric labels.

See [Telemetry safety](reference.md#telemetry-safety).

## Verify Diagnosis

1. Simulate a dependency timeout, a database error, and a load spike.
2. For each case, find the cause from telemetry only, without reproducing it by hand.
3. If a step is missing from the trace, or a log lacks the IDs to find it, fix the instrumentation.

Example diagnosis of a slow checkout:

1. The metric shows checkout p95 latency grew from 200 ms to 2 s.
2. The trace shows that `payment.charge` takes 1.7 s.
3. The logs filtered by `trace_id` show a timeout of the external payment provider.
4. The SLO alert notifies the team. The runbook gives the recovery steps.

## Result

```text
function checkout(order, context):
    trace = startTrace("checkout", context)

    try:
        with span("inventory.check"):
            inventory.check(order.items)

        with span("payment.charge"):
            payment.charge(order)

        with span("order.save"):
            database.save(order)

        metrics.checkout_success.increment()
        return success(order)

    catch error:
        metrics.checkout_failure.increment(error_type = classify(error))

        log.error({
            event: "checkout_failed",
            request_id: context.request_id,
            trace_id: context.trace_id,
            error_type: classify(error)
        })

        throw error
    finally:
        trace.end()
```

## Add Observability to an Existing Service

Introduce it in this order:

1. Structured logs: one format, `request_id`, levels, context, central collection.
2. RED metrics for the main routes: requests, errors, latency.
3. Traces: external calls, databases, critical business operations.
4. Correlation: `trace_id` and `span_id` in logs, context passed across services.
5. SLO and alerts: decide which latency and errors break user expectations. See [Health checks, SLO, and alerts](reference.md#health-checks-slo-and-alerts).
6. Profiling and business metrics.
7. Verification: run [Verify diagnosis](#verify-diagnosis) and check the [quality criteria](reference.md#quality-criteria).
