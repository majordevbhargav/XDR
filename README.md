# XDR Security Automation Platform

A hands-on Extended Detection and Response (XDR) project focused on connecting security telemetry, cloud services, incident management, and response automation in a single workflow.

> **Project status:** AWS integration and ServiceNow integration are implemented. Detection/automation playbooks and workflow rules are part of the project. EDR containment workflow is the remaining major item and is not yet complete.

## Overview

Security teams often investigate alerts across separate tools. This project explores how integrations and repeatable playbooks can reduce manual handoffs, standardize triage, and make incident handling easier to follow.

The repository is a learning and engineering project. Capabilities should be considered implemented only where the corresponding integration, configuration, and workflow are present and tested in this codebase.

## Current scope

- **AWS integration** — cloud-side integration work for the project.
- **ServiceNow integration** — incident-management integration to support ticket and response workflows.
- **Automation rules** — conditions and actions that route events through defined handling logic.
- **Playbooks** — repeatable steps for common security-response scenarios.
- **Workflow orchestration** — connecting integration events and response steps.
- **Planned: EDR containment** — endpoint isolation/containment orchestration, including safe execution controls and outcome verification.

## Response lifecycle

```text
Security signal / event
        |
        v
Normalize and evaluate
        |
        v
Automation rule matches?
        |
        +---- No ----> Log / leave for analyst review
        |
       Yes
        |
        v
Run applicable playbook
        |
        +----> AWS integration actions
        |
        +----> ServiceNow incident workflow
        |
        v
Record execution result and evidence
        |
        v
Analyst review / follow-up
```

This diagram describes the intended high-level flow. Refer to the implementation and configuration in the repository for the exact event sources, conditions, and actions currently available.

## Security design principles

- **Least privilege:** use narrowly scoped credentials and roles for each integration.
- **Secrets hygiene:** keep API keys, tokens, and account credentials out of source control.
- **Auditable actions:** record which rule or playbook ran, its inputs, outcome, and errors, while avoiding unnecessary sensitive data.
- **Human oversight:** require explicit approval for destructive or disruptive response actions until the safeguards are implemented and tested.
- **Idempotency:** design retries so duplicate events do not create duplicate incidents or repeat risky actions.
- **Failure handling:** distinguish successful, failed, skipped, and partially completed steps.
- **Safe testing:** validate integrations in a sandbox or test tenant before using production systems.

## Configuration checklist

Before running the project, review the configuration and environment files in the repository and provide the required integration settings through environment variables or a local, untracked configuration file.

- [ ] AWS identity/role and minimum required permissions
- [ ] ServiceNow instance URL and scoped integration credentials
- [ ] Event source and automation-rule configuration
- [ ] Playbook-specific parameters
- [ ] Logging and error handling
- [ ] Test credentials and a non-production environment

Do not commit real credentials, access tokens, customer data, or production incident details.

## Validation checklist

Use this as a practical test plan when reviewing or extending the project:

1. Verify each integration's authentication and permission scope.
2. Test successful and failed API calls.
3. Confirm that rules match expected events and ignore unrelated events.
4. Confirm that playbooks record their execution status and useful diagnostic details.
5. Test retries, duplicate events, rate limits, and timeouts.
6. Verify that ServiceNow updates map to the intended incident fields and states.
7. Confirm that no response action executes without the configured authorization checks.
8. For future EDR containment, test authorization, endpoint targeting, rollback/release, and post-action verification in a lab environment.

## Roadmap

- [x] AWS integration
- [x] ServiceNow integration
- [x] Automation rules and playbook workflows
- [ ] EDR containment workflow
- [ ] End-to-end integration tests with documented sample events
- [ ] Execution audit trail and clearer failure/retry reporting
- [ ] Architecture diagram reflecting the concrete implementation
- [ ] Setup guide with exact prerequisites and safe test commands

## Contributing

1. Create a focused branch for your change.
2. Keep credentials and environment-specific configuration out of commits.
3. Add or update tests for rule and workflow changes.
4. Document required configuration and expected behavior.
5. Test against non-production services before proposing a merge.

## Disclaimer

This project is for educational and defensive security engineering. Integrations and automated actions should be tested with least-privilege credentials in a controlled environment. Do not enable endpoint isolation or other disruptive response actions without authorization, safeguards, and a recovery procedure.
