# Architecture and Workflow Notes

This document describes the intended high-level design. It is not a claim that every box below is already implemented; check the source code and configuration for the current implementation details.

## Logical flow

```text
Event / security signal
        |
        v
Input validation and normalization
        |
        v
Rule evaluation
        |
        +---- no match ----> Record / analyst review
        |
        v
Playbook selection
        |
        +----> AWS integration
        |
        +----> ServiceNow incident workflow
        |
        v
Execution status and audit evidence
```

## Component responsibilities

- **Integrations:** authenticate to external platforms, make API requests, and translate external responses into project-level results.
- **Automation rules:** decide whether an event meets the conditions for a workflow.
- **Playbooks:** define repeatable steps and expected outcomes for a scenario.
- **Workflow orchestration:** pass context between steps and handle success, failure, and skipped actions.
- **Audit trail:** preserve enough metadata to explain why a workflow ran and what happened, while minimizing sensitive information.

## Recommended execution states

Use explicit states such as `pending`, `running`, `succeeded`, `failed`, and `skipped`. Record a correlation ID, rule/playbook identifier, start and finish timestamps, and a concise outcome. Never log secrets or full sensitive payloads.

## Reliability and safety controls

1. Validate input schemas before rule evaluation.
2. Apply timeouts and bounded retries for external API calls.
3. Handle rate limits and partial failures explicitly.
4. Use idempotency keys or deduplication where supported.
5. Keep credentials scoped to the minimum required operations.
6. Require authorization and target confirmation before disruptive actions.
7. Make every response action traceable and provide a recovery path.

## EDR containment extension

EDR containment is a planned extension, not represented as complete. Before enabling it, add and test:
- endpoint identity verification and allow/deny safeguards;
- approval or policy authorization for isolation;
- duplicate-request protection;
- API failure and timeout handling;
- an auditable result;
- a documented release/recovery procedure.
