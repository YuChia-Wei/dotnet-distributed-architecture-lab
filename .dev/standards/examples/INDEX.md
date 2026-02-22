# Examples Index (.NET)

This index maps source stack examples to their .NET counterparts. Use it as the
single source of truth for migration scope and completion tracking.

Note: Source file names keep their legacy extensions (e.g., `.java`) for traceability.
TODO: Remove legacy file references once mapping is no longer needed.

## Status Legend
- TODO: Not migrated yet.
- IN-PROGRESS: Work started, not complete.
- DONE: Migrated and reviewed.

## Conversion Notes (Apply to All)
- Preserve DDD/CA/CQRS semantics and ezDDD/ezSpec intent (no concept loss).
- Use WolverineFx for CQRS/MQ/eventing patterns.
- Use EF Core for persistence and projections.
- Use xUnit + BDDfy (Gherkin-style naming) for tests; do NOT use BaseTestClass patterns.
- Legacy Gherkin `.feature` examples exist for Reqnroll under `examples/bdd-gherkin-*` for reference only.
- Use NSubstitute for mocks.
- Use TODO for parts that cannot be expressed in .NET yet.

## Aggregate (DDD Core)
- Source: `examples/aggregate/Plan.java` -> .NET: `examples/aggregate/Plan.cs` (DONE)
- Source: `examples/aggregate/PlanEvents.java` -> .NET: `examples/aggregate/PlanEvents.cs` (DONE)
- Source: `examples/aggregate/PlanId.java` -> .NET: `examples/aggregate/PlanId.cs` (DONE)
- Source: `examples/aggregate/Project.java` -> .NET: `examples/aggregate/Project.cs` (DONE)
- Source: `examples/aggregate/ProjectId.java` -> .NET: `examples/aggregate/ProjectId.cs` (DONE)
- Source: `examples/aggregate/ProjectName.java` -> .NET: `examples/aggregate/ProjectName.cs` (DONE)
- Source: `examples/aggregate/TagEvents.java` -> .NET: `examples/aggregate/TagEvents.cs` (DONE)
- Source: `examples/aggregate/TagId.java` -> .NET: `examples/aggregate/TagId.cs` (DONE)
- Source: `examples/aggregate/TaskId.java` -> .NET: `examples/aggregate/TaskId.cs` (DONE)
- Source: `examples/aggregate/README.md` -> .NET: `examples/aggregate/README.md` (DONE)

## Contracts (Contract Testing / UContract)
- Source: `examples/contract/CONTRACT-GUIDE.md` -> .NET: `examples/contract/CONTRACT-GUIDE.md` (DONE)
- Source: `examples/contract/UCONTRACT-GUIDE.md` -> .NET: `examples/contract/UCONTRACT-GUIDE.md` (DONE)
- Source: `examples/contract/ucontract-detailed-examples.md` -> .NET: `examples/contract/ucontract-detailed-examples.md` (DONE)
- Source: `examples/contract/aggregate-contract-example.md` -> .NET: `examples/contract/aggregate-contract-example.md` (DONE)
- Source: `examples/contract/usecase-contract-example.md` -> .NET: `examples/contract/usecase-contract-example.md` (DONE)
- Source: `examples/contract/value-object-contract-example.md` -> .NET: `examples/contract/value-object-contract-example.md` (DONE)
- Source: `examples/contract/README.md` -> .NET: `examples/contract/README.md` (DONE)

## Controllers / API
- Source: `examples/controller/CreateTaskController.java` -> .NET: `examples/controller/CreateTaskController.cs` (DONE)
- Source: `examples/controller/README.md` -> .NET: `examples/controller/README.md` (DONE)

## DTOs
- Source: `examples/dto/PlanDto.java` -> .NET: `examples/dto/PlanDto.cs` (DONE)
- Source: `examples/dto/ProjectDto.java` -> .NET: `examples/dto/ProjectDto.cs` (DONE)
- Source: `examples/dto/TaskDto.java` -> .NET: `examples/dto/TaskDto.cs` (DONE)
- Source: `examples/dto/README.md` -> .NET: `examples/dto/README.md` (DONE)

## BDDfy Rule Examples (ezSpec -> BDDfy)
- Source: `examples/ezspec-rule-examples/complete-usecase-with-rules.java` -> .NET: `examples/bdd-given-when-then-example/CompleteUseCaseRuleTests.cs` (DONE)
- Source: `examples/ezspec-rule-examples/ProductOutboxRepositoryTest.java` -> .NET: `examples/bdd-given-when-then-example/ProductOutboxRepositoryTests.cs` (DONE)
- Source: `examples/ezspec-rule-examples/OUTBOX-TEST-CONFIGURATION.md` -> .NET: `examples/bdd-given-when-then-example/OUTBOX-TEST-CONFIGURATION.md` (DONE)
- Source: `examples/ezspec-rule-examples/rule-design-before-after.md` -> .NET: `examples/bdd-given-when-then-example/rule-design-before-after.md` (DONE)
- Source: `examples/ezspec-rule-examples/rule-migration-guide.md` -> .NET: `examples/bdd-given-when-then-example/rule-migration-guide.md` (DONE)
- Source: `examples/ezspec-rule-examples/README.md` -> .NET: `examples/bdd-given-when-then-example/README.md` (DONE)

## BDD Gherkin Examples (Reqnroll, Reference Only)
- Source: `examples/ezspec-rule-examples/complete-usecase-with-rules.java` -> .NET: `examples/bdd-gherkin-example/complete-usecase-with-rules.feature` + `examples/bdd-gherkin-example/CompleteUseCaseSteps.cs` (REF)
- Source: `examples/ezspec-rule-examples/ProductOutboxRepositoryTest.java` -> .NET: `examples/bdd-gherkin-example/product-outbox-repository.feature` + `examples/bdd-gherkin-example/ProductOutboxRepositorySteps.cs` (REF)
- Source: `examples/ezspec-rule-examples/OUTBOX-TEST-CONFIGURATION.md` -> .NET: `examples/bdd-gherkin-example/OUTBOX-TEST-CONFIGURATION.md` (REF)
- Source: `examples/ezspec-rule-examples/rule-design-before-after.md` -> .NET: `examples/bdd-gherkin-example/rule-design-before-after.md` (REF)
- Source: `examples/ezspec-rule-examples/rule-migration-guide.md` -> .NET: `examples/bdd-gherkin-example/rule-migration-guide.md` (REF)
- Source: `examples/ezspec-rule-examples/README.md` -> .NET: `examples/bdd-gherkin-example/README.md` (REF)

## Generation Templates (Test/Code Templates)
- Source: `examples/generation-templates/base-test-classes.md` -> .NET: `examples/generation-templates/base-test-classes.md` (DONE)
- Source: `examples/generation-templates/complex-aggregate-spec.md` -> .NET: `examples/generation-templates/complex-aggregate-spec.md` (DONE)
- Source: `examples/generation-templates/local-utils.md` -> .NET: `examples/generation-templates/local-utils.md` (DONE)
- Source: `examples/generation-templates/reactor-full.md` -> .NET: `examples/generation-templates/reactor-full.md` (DONE)
- Source: `examples/generation-templates/test-case-full.md` -> .NET: `examples/generation-templates/test-case-full.md` (DONE)
- Source: `examples/generation-templates/test-suites.md` -> .NET: `examples/generation-templates/test-suites.md` (DONE)
- Source: `examples/generation-templates/README.md` -> .NET: `examples/generation-templates/README.md` (DONE)

## Inquiry / Archive
- Source: `examples/inquiry-archive/FindCardsByTagIdInquiry.java` -> .NET: `examples/inquiry-archive/FindCardsByTagIdInquiry.cs` (DONE)
- Source: `examples/inquiry-archive/EsFindCardsByTagIdInquiry.java` -> .NET: `examples/inquiry-archive/EsFindCardsByTagIdInquiry.cs` (DONE)
- Source: `examples/inquiry-archive/JpaFindCardsByTagIdInquiry.java` -> .NET: `examples/inquiry-archive/EfFindCardsByTagIdInquiry.cs` (DONE)
- Source: `examples/inquiry-archive/JpaUserArchive.java` -> .NET: `examples/inquiry-archive/EfUserArchive.cs` (DONE)
- Source: `examples/inquiry-archive/UserArchive.java` -> .NET: `examples/inquiry-archive/UserArchive.cs` (DONE)
- Source: `examples/inquiry-archive/UserOrmClient.java` -> .NET: `examples/inquiry-archive/UserDbContext.cs` (DONE)
- Source: `examples/inquiry-archive/USAGE-GUIDE.md` -> .NET: `examples/inquiry-archive/USAGE-GUIDE.md` (DONE)
- Source: `examples/inquiry-archive/README.md` -> .NET: `examples/inquiry-archive/README.md` (DONE)

## Mappers
- Source: `examples/mapper/PlanMapper.java` -> .NET: `examples/mapper/PlanMapper.cs` (DONE)
- Source: `examples/mapper/TaskMapper.java` -> .NET: `examples/mapper/TaskMapper.cs` (DONE)
- Source: `examples/mapper/README.md` -> .NET: `examples/mapper/README.md` (DONE)

## Outbox / Integration
- Source: `examples/outbox/BootstrapConfig.java` -> .NET: `examples/outbox/BootstrapConfig.cs` (DONE)
- Source: `examples/outbox/DataSourceConfig.java` -> .NET: `examples/outbox/DataSourceConfig.cs` (DONE)
- Source: `examples/outbox/RepositoryConfig.java` -> .NET: `examples/outbox/RepositoryConfig.cs` (DONE)
- Source: `examples/outbox/PlanData.java` -> .NET: `examples/outbox/PlanData.cs` (DONE)
- Source: `examples/outbox/PlanMapper.java` -> .NET: `examples/outbox/PlanOutboxMapper.cs` (DONE)
- Source: `examples/outbox/PlanOrmClient.java` -> .NET: `examples/outbox/PlanDbContext.cs` (DONE)
- Source: `examples/outbox/ProjectData.java` -> .NET: `examples/outbox/ProjectData.cs` (DONE)
- Source: `examples/outbox/ProjectMapper.java` -> .NET: `examples/outbox/ProjectOutboxMapper.cs` (DONE)
- Source: `examples/outbox/TaskData.java` -> .NET: `examples/outbox/TaskData.cs` (DONE)
- Source: `examples/outbox/TaskMapper.java` -> .NET: `examples/outbox/TaskOutboxMapper.cs` (DONE)
- Source: `examples/outbox/README.md` -> .NET: `examples/outbox/README.md` (DONE)

## Profile Configs
- Source: `examples/profile-configs/event-architecture-reference.md` -> .NET: `examples/profile-configs/event-architecture-reference.md` (DONE)
- Source: `examples/profile-configs/inmemory-profile-config.md` -> .NET: `examples/profile-configs/inmemory-profile-config.md` (DONE)
- Source: `examples/profile-configs/outbox-profile-config.md` -> .NET: `examples/profile-configs/outbox-profile-config.md` (DONE)

## Projections
- Source: `examples/projection/AllTagsProjection.java` -> .NET: `examples/projection/AllTagsProjection.cs` (DONE)
- Source: `examples/projection/PlanDtosProjection.java` -> .NET: `examples/projection/PlanDtosProjection.cs` (DONE)
- Source: `examples/projection/TasksByDateProjection.java` -> .NET: `examples/projection/TasksByDateProjection.cs` (DONE)
- Source: `examples/projection/TasksDueTodayProjection.java` -> .NET: `examples/projection/TasksDueTodayProjection.cs` (DONE)
- Source: `examples/projection/TasksSortedByDeadlineProjection.java` -> .NET: `examples/projection/TasksSortedByDeadlineProjection.cs` (DONE)
- Source: `examples/projection/JpaAllTagsProjection.java` -> .NET: `examples/projection/EfAllTagsProjection.cs` (DONE)
- Source: `examples/projection/JpaPlanDtosProjection.java` -> .NET: `examples/projection/EfPlanDtosProjection.cs` (DONE)
- Source: `examples/projection/JpaTasksByDateProjection.java` -> .NET: `examples/projection/EfTasksByDateProjection.cs` (DONE)
- Source: `examples/projection/JpaTasksDueTodayProjection.java` -> .NET: `examples/projection/EfTasksDueTodayProjection.cs` (DONE)
- Source: `examples/projection/README.md` -> .NET: `examples/projection/README.md` (DONE)

## Reference
- Source: `examples/reference/ezddd-import-mapping.md` -> .NET: `examples/reference/ezddd-import-mapping.md` (DONE)
- Source: `examples/reference/ezspec-test-template.md` -> .NET: `examples/reference/ezspec-test-template.md` (DONE)
- Source: `examples/reference/maven-dependencies.md` -> .NET: `examples/reference/nuget-dependencies.md` (DONE)
- Source: `examples/reference/reactor-pattern-guide.md` -> .NET: `examples/reference/reactor-pattern-guide.md` (DONE)
- Source: `examples/reference/README.md` -> .NET: `examples/reference/README.md` (DONE)

## Bootstrap / Hosting (ASP.NET Core equivalents)
- Source: `examples/spring/AiScrumApp.java` -> .NET: `examples/aspnet-core/Program.cs` (DONE)
- Source: `examples/spring/UseCaseConfiguration.java` -> .NET: `examples/aspnet-core/UseCaseConfiguration.cs` (DONE)
- Source: `examples/spring/InMemoryRepositoryConfig.java` -> .NET: `examples/aspnet-core/InMemoryRepositoryConfig.cs` (DONE)
- Source: `examples/spring/InMemoryRepositoryConfig-v2.java` -> .NET: `examples/aspnet-core/InMemoryRepositoryConfig.cs` (DONE)
- Source: `examples/spring/OutboxRepositoryConfig.java` -> .NET: `examples/aspnet-core/OutboxRepositoryConfig.cs` (DONE)
- Source: `examples/spring/application.properties` -> .NET: `examples/aspnet-core/appsettings.json` (DONE)
- Source: `examples/spring/application-inmemory.properties` -> .NET: `examples/aspnet-core/appsettings.InMemory.json` (DONE)
- Source: `examples/spring/application-outbox.properties` -> .NET: `examples/aspnet-core/appsettings.Outbox.json` (DONE)
- Source: `examples/spring/application-test-inmemory.properties.template` -> .NET: `examples/aspnet-core/appsettings.Test.InMemory.json` (DONE)
- Source: `examples/spring/application-test-outbox.properties.template` -> .NET: `examples/aspnet-core/appsettings.Test.Outbox.json` (DONE)
- Source: `examples/spring/README.md` -> .NET: `examples/aspnet-core/README.md` (DONE)

## Testing (xUnit + BDDfy)
- Source: `examples/test/BaseSpringBootTest.java` -> .NET: `examples/test/TestHostFixture.cs` (DONE)
- Source: `examples/test/BaseUseCaseTest.java` -> .NET: `examples/test/UseCaseTestFixture.cs` (DONE)
- Source: `examples/test/CreateTaskUseCaseTest.java` -> .NET: `examples/test/CreateTaskUseCaseTests.cs` (DONE)
- Source: `examples/test/README.md` -> .NET: `examples/test/README.md` (DONE)

## Testing (Reqnroll Gherkin, Reference Only)
- Source: `examples/test/CreateTaskUseCaseTest.java` -> .NET: `examples/bdd-gherkin-test/CreateTaskUseCase.feature` + `examples/bdd-gherkin-test/CreateTaskUseCaseSteps.cs` (REF)
- Source: `examples/test-example.md` -> .NET: `examples/test-example.md` (DONE)
- Source: `examples/testing-guide.md` -> .NET: `examples/testing-guide.md` (DONE)
- Source: `examples/use-case-test-example.md` -> .NET: `examples/use-case-test-example.md` (DONE)

## Use Cases / Application Services
- Source: `examples/usecase/AssignTagService.java` -> .NET: `examples/usecase/AssignTagService.cs` (DONE)
- Source: `examples/usecase/AssignTagUseCase.java` -> .NET: `examples/usecase/AssignTagUseCase.cs` (DONE)
- Source: `examples/usecase/CreatePlanService.java` -> .NET: `examples/usecase/CreatePlanService.cs` (DONE)
- Source: `examples/usecase/CreatePlanUseCase.java` -> .NET: `examples/usecase/CreatePlanUseCase.cs` (DONE)
- Source: `examples/usecase/CreateTaskService.java` -> .NET: `examples/usecase/CreateTaskService.cs` (DONE)
- Source: `examples/usecase/CreateTaskUseCase.java` -> .NET: `examples/usecase/CreateTaskUseCase.cs` (DONE)
- Source: `examples/usecase/DeleteTaskService.java` -> .NET: `examples/usecase/DeleteTaskService.cs` (DONE)
- Source: `examples/usecase/DeleteTaskUseCase.java` -> .NET: `examples/usecase/DeleteTaskUseCase.cs` (DONE)
- Source: `examples/usecase/GetPlanService.java` -> .NET: `examples/usecase/GetPlanService.cs` (DONE)
- Source: `examples/usecase/GetPlanUseCase.java` -> .NET: `examples/usecase/GetPlanUseCase.cs` (DONE)
- Source: `examples/usecase/GetPlansService.java` -> .NET: `examples/usecase/GetPlansService.cs` (DONE)
- Source: `examples/usecase/GetPlansUseCase.java` -> .NET: `examples/usecase/GetPlansUseCase.cs` (DONE)
- Source: `examples/usecase/GetTasksByDateService.java` -> .NET: `examples/usecase/GetTasksByDateService.cs` (DONE)
- Source: `examples/usecase/GetTasksByDateUseCase.java` -> .NET: `examples/usecase/GetTasksByDateUseCase.cs` (DONE)
- Source: `examples/usecase/RenameTaskService.java` -> .NET: `examples/usecase/RenameTaskService.cs` (DONE)
- Source: `examples/usecase/RenameTaskUseCase.java` -> .NET: `examples/usecase/RenameTaskUseCase.cs` (DONE)
- Source: `examples/usecase/README.md` -> .NET: `examples/usecase/README.md` (DONE)

## Use Case Injection
- Source: `examples/use-case-injection/README.md` -> .NET: `examples/use-case-injection/README.md` (DONE)

## Misc
- Source: `examples/.versions.json` -> .NET: `examples/.versions.json` (DONE)
- Source: `examples/INDEX.md` -> .NET: `examples/INDEX.md` (DONE)
- Source: `examples/README.md` -> .NET: `examples/README.md` (DONE)
- Source: `examples/TEMPLATE-INDEX.md` -> .NET: `examples/TEMPLATE-INDEX.md` (DONE)
- Source: `examples/pom/pom.xml` -> .NET: `examples/nuget/Directory.Packages.props` (DONE)
- Source: `examples/projection-example.md` -> .NET: `examples/projection-example.md` (DONE)
