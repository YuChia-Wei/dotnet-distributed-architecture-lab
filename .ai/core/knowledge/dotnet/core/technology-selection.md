# .NET technology selection

Establish the actual SDK, target framework, C# language settings, package
versions and deployment platform before applying a .NET reference or sample.
Use the solution and project files, `global.json` when present, central package
properties and lock files, supported deployment settings and accepted target
decisions. A generated summary can point to these inputs. When inputs disagree
or are missing, keep the affected choice unresolved for its target owner.

Reusable examples describe their sample version. Confirm the actual version
before using package APIs or changing dependencies. The knowledge package
supplies no SDK or provider installation and requires no target initialization
skill or fixed `.dev` location.

Apply Linux/container portability where the target adopted the existing backend
deployment baseline or actually deploys there. In that scope, prefer portable
path APIs such as `Path.Combine`, avoid unsupported platform APIs and packages,
and validate against the deployment platform. An explicitly different target
platform governs its own artifacts.

Select additional guidance only when the target evidence identifies the
[architecture](../architecture/ddd-cqrs/overview.md),
[persistence](../integration/persistence/configuration.md),
[messaging](../integration/messaging/persistence-and-messaging.md) or
[testing](../testing/test-standards.md) concern.
