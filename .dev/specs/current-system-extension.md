# Current System Extension (updated 2026-09-29)

This file records the implemented scope added after the three-context reconstruction baseline. It is a navigation and source-binding record, not a complete replacement for the versioned machine-readable reconstruction contracts.

## Current additions

| Area | Current source authority | Operating reference |
| --- | --- | --- |
| Procurement business context: quote, purchase, reconciliation, partial receipt | `src/Procurement/`, `src/BC-Contracts/Lab.BoundedContextContracts.Procurement/`, `tests/Procurement.Tests/` | `../operations/procurement-supplier-lab.md` |
| Fixed supplier HTTP profiles, sandbox, WireMock.Net and Microcks | `src/Procurement/DomainCore/Procurement.Infrastructure/HttpSupplierGateway.cs`, `samples/SupplierSandbox/`, `samples/SupplierMock/`, `docker-compose/docker-compose.procurement.yml` | `../operations/procurement-supplier-lab.md` |
| First committed receipt to Inventory | `GoodsReceived` contract, Procurement source outbox, `src/Inventory/Presentation/InventoryControl.Consumer/Messaging/GoodsReceivedHandler.cs` | `../operations/event-catalog.md`, `../operations/mq-topology.md` |
| Internal Web/Admin frontends and YARP paths | `src/Frontend/Web/`, `src/Frontend/Admin/`, `docker-compose/docker-compose.frontend.yml`, gateway route config | `../operations/commerce-frontend.md` |

The solution currently contains 27 `src/` projects, five `samples/` projects, and nine `tests/` projects. The original reconstruction `project-manifest.json`, HTTP/message/persistence/runtime contracts, coverage matrix, and acceptance procedure describe an earlier three-context target. They do not specify Procurement, supplier simulation, the two frontends, or their complete acceptance gates. The [Procurement specification set](domains/procurement/README.md), added on 2026-09-29 and bound to source revision `179b3e12bb1e5f1c67cee3158ccd414bd9a8b6a5`, now documents its aggregate, six operations, HTTP contract, supplier adapter, persistence and receipt messaging. The [formal test entry](tests/procurement/README.md) maps the original scenario IDs to test-source presence and remaining verification targets. These additions do not rewrite the earlier machine-readable reconstruction contracts. A full source-independent rebuild of all additions still needs complete reconstruction contracts and verification; this document does not claim that those gates have passed.
