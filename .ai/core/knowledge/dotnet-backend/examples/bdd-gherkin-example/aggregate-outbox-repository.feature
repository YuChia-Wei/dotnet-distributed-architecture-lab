Feature: SampleAggregate Outbox Repository
  Standard Outbox repository integration tests for every aggregate.

  Rule: Data persistence
    Scenario: Persist aggregate to database with all fields
      Given a SampleAggregate aggregate with complete data
      When I save the aggregate using OutboxRepository
      Then the aggregate is persisted with all fields

  Rule: Data retrieval
    Scenario: Retrieve aggregate with complete data
      Given a aggregate exists in the database
      When I load the aggregate from repository
      Then the aggregate data is fully rehydrated

  Rule: Soft delete
    Scenario: Soft delete aggregate
      Given a aggregate exists in the database
      When I mark the aggregate as deleted and save
      Then the aggregate is marked as deleted in the database

  Rule: Version control
    Scenario: Version increments on update
      Given a aggregate exists in the database
      When I update the aggregate and save
      Then the version is incremented in storage
