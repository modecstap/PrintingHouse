# Reference: Observability

Facts for instrumenting code. How to apply them: [instructions](howto.md). Examples are pseudocode.

Observability is the ability to move fast from a symptom to its cause and to a recovery decision, using only the data the system emits at runtime: no code changes, no manual reproduction. Telemetry must show what happens, why, and where to look (service, operation, request, or dependency). More logs do not mean better observability.

## Signals

| Signal  | Answers                 |
| ------- | ----------------------- |
| Logs    | What happened           |
| Metrics | How often and how much  |
| Traces  | Where and why           |

The signals are useful only when linked: every log record and span of one request carries the same `request_id` and `trace_id`. An alert on a metric then leads to the trace of one slow request, and the trace to its logs.

## Logs

Write events in a structured format such as JSON, with shared fields and a level: `DEBUG`, `INFO`, `WARN`, or `ERROR`.

```text
log.info({
  event: "payment_processed",
  order_id: order.id,
  amount: payment.amount,
  status: "success"
})
```

Rules:

- Log the start and the end of important operations.
- Add `request_id`, `trace_id`, `span_id`, and the IDs of the entities involved.
- Keep event names and field names stable. Dashboards and queries depend on them.

## Metrics

```text
http_requests_total.increment(method = "POST", route = "/orders", status = 500)
request_duration.observe(elapsed_ms)
```

### Method sets

| Method         | Applies to | Measure                                    |
| -------------- | ---------- | ------------------------------------------ |
| RED            | Services   | Rate, Errors, Duration                     |
| USE            | Resources  | Utilization, Saturation, Errors            |
| Golden Signals | Services   | Latency, traffic, errors, saturation       |

Resources include CPU, memory, disk, queues, and connection pools.

### Rules

- Measure latency as percentiles: p50, p95, p99. An average hides slow requests.
- Count successes, not only failures, to get the success rate. Example: `orders_created` and `orders_rejected`.
- Keep label values from a bounded set. Never put IDs, emails, or free text in a label. Each unique value creates a new time series (cardinality).
- Measure business results, such as completed payments, orders, and sign-ups, to link technical health to the business result.

### Queues and background jobs

For each queue and background job:

```text
metrics.queue_depth.set(queue.size)
metrics.job_duration.observe(elapsed)
metrics.job_failures.increment()
```

## Traces

```text
trace = tracer.startTrace("checkout")

span = trace.startSpan("inventory.check")
inventory.check(order.items)
span.end()

trace.end()
```

Rules:

- Create a span for each important operation and each call across a [system boundary](#where-to-add-spans).
- Record the duration, the status, and the error of each span.
- End every span, also when the operation fails.
- Sample part of the traces when needed to control data volume and storage cost, but keep all important events.
- Manage the span lifecycle with the API of the chosen tracing library.

### Where to Add Spans

Instrument every place where code talks to the outside world:

- HTTP API and RPC;
- databases;
- queues and message brokers;
- external APIs;
- cache and file storage;
- background jobs.

```text
with span("database.query"):
    result = repository.findById(id)
```

## Context Propagation

Pass the request ID and the trace context through calls, queues, and background jobs.

```text
context = {
  request_id: "req-123",
  trace_id: "trace-456",
  user_ref: pseudonymize(user.id)
}

orderService.create(order, context)
paymentService.charge(order, context)
```

Rules:

- Create and read the context in middleware for HTTP requests.
- Put the context into the headers or metadata of queue messages.
- Use the W3C Trace Context standard between services.
- Never treat an incoming ID as proof of user identity. A client can send any value.

## Errors

Capture each exception with its stack trace and the context of the operation.

```text
try:
  result = processOrder(order)
catch error:
  errorTracker.capture(error, context = {
    operation: "process_order",
    order_id: order.id
  })
  throw error
```

Rules:

- Never swallow an exception silently. Capture it and rethrow, or handle it and log why.
- Keep the original cause when wrapping an error.
- Separate expected business errors (for example, insufficient funds) from unexpected failures. Only unexpected failures are incidents.
- Group repeated errors by type so new error types stand out.

## Profiling

Measure CPU, memory, lock contention, and the run time of single functions.

```text
profile.start("generate_report")
generateReport(data)
profile.stop("generate_report")
```

Rules:

- Compare profiles before and after an optimization.
- Use continuous profiling in high-load systems.
- Use traces, not profiles, for request latency. It also includes network, queues, and waiting on dependencies.

## Technical and Business Events

Keep technical events and business events apart.

```text
log.info(event = "database_connection_acquired")

businessEvent.publish(name = "order_completed", order_id = order.id)
```

Technical logs diagnose the system. Business events describe what happens in the domain. A business event used as a source of truth needs guaranteed delivery and storage, which a log does not give.

## Single Observability Interface

Call telemetry through one shared interface, not through ad-hoc logging calls spread over the code.

```text
observability.recordEvent(...)
observability.recordMetric(...)
observability.startSpan(...)
```

The interface owns the format and the shared fields, and is the one place to replace the implementation. Build it on top of a standard SDK, not a custom monitoring system.

## Telemetry Safety

```text
log.info({
    event: "login_attempt",
    user_ref: pseudonymize(user.id),
    result: "failure"
})
```

Rules:

- Never write passwords, access tokens, API keys, or session cookies to logs, spans, metrics, or error reports.
- Mask or pseudonymize personal data.
- Apply redaction in the shared interface, not at each call site.
- Limit who can read telemetry, how long it is stored, and how much is collected.

## Health Checks, SLO, and Alerts

- Health checks: expose readiness and liveness checks so the orchestrator can replace broken instances.
- SLO and error budget: set target values for availability and latency of critical operations.
- Alerts: alert on user-visible symptoms and SLO violations, not on every internal error.
- Runbooks: document diagnosis and recovery steps for each alert.

## Failure Isolation

A failure of the telemetry pipeline, such as an unreachable log collector or tracing backend, must not break the business process. Send telemetry asynchronously and drop it when buffers are full.

## Quality Criteria

Observability is good when:

- all events of one request can be found by its ID;
- the slowest step of an operation is visible;
- errors carry context and keep the original cause;
- there are metrics for latency, errors, traffic, and resource saturation;
- an alert leads to the matching logs and traces;
- critical operations have an SLO and clear alerts;
- telemetry holds no secrets, and cardinality and storage cost are under control;
- a failure of the telemetry pipeline does not break the business process.
