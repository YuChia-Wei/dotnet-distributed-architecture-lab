# Profile-based testing

Use profile-based testing when the target runs the same observable behavior
against more than one infrastructure configuration. Record each supported
environment, provider registration, settings/fixture and external dependency
from project evidence. A profile's name does not establish its provider. Follow
the [selected persistence profile](../integration/persistence/configuration.md)
when it defines exact environments and dependencies.

## Choose the smallest real boundary

- Construct a unit subject directly when host composition or transport adds
  no evidence. Replace only the outbound dependencies needed by the scenario
  using the target's accepted test doubles.
- Use a host or service-provider fixture when configuration, DI or a selected
  adapter is the claim. Initialize and dispose the selected dependencies in the
  fixture. For xUnit, class fixtures or collection fixtures are options. A
  shared fixture can own infrastructure lifetime while each scenario owns
  fresh mutable state, unique keys or a documented reset.
- Use the selected HTTP host factory for route/HTTP behavior. Confirm its
  overrides replace the intended port before resolution. Use the real durable
  adapter and actual required dependencies when the claim concerns the
  [transaction or delivery](../integration/messaging/transactional-messaging-standards.md).

## Select and verify each profile

Select the environment through the test host, its fixture configuration or
the command/IDE run configuration before host construction. Do not mutate
process-global environment variables inside test classes. When the adopted
[host selector](../core/host-configuration.md) is a process variable, execute
conflicting environment selections in separate processes. Set the selector
read by the actual host and preserve exact casing.

For example, an adopted dual-profile target using `DOTNET_ENVIRONMENT` can run
the following commands in separate processes with its own project and filter:

```bash
DOTNET_ENVIRONMENT=TestInMemory dotnet test <test-project>
DOTNET_ENVIRONMENT=TestOutbox dotnet test <test-project> --filter <target-filter>
```

Use the IDE's equivalent configuration for an IDE run. Choose an existing xUnit
trait or another runner-supported filter when a subset is needed, then confirm
the intended cases and profiles actually ran. For dual-profile smoke coverage,
verify the fast host has no durable dependencies and the outbox host resolves
its complete persistence chain. Record the selected provider and the specific
behavior observed per run.

## Isolate scenario evidence

Apply the target-selected [test standards](test-standards.md). Give scenarios
only the state they need and keep materially different values visible. Establish
Given through the supported port when that boundary is part of the scenario.
Use lower-level setup only where the test design permits it. Observe outcomes
through supported reads, actual captured events, or another agreed boundary.

For asynchronous event capture, wait for the fixture's documented condition
before checking or clearing setup events. Keep setup events distinguishable
from the event that the primary action should produce. Verify capture and cleanup
separately from the feature assertion when a shared fixture could hide failures.
Test order must not determine the scenario's data or event history.

When host composition fails, trace the resolved environment, selected module,
missing dependency and intended provider. See [troubleshooting](../references/troubleshooting.md).
