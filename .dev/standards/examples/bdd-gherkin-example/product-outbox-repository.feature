Feature: Product Outbox Repository
  Standard Outbox repository integration tests for every aggregate.

  Rule: Data persistence
    Scenario: Persist product to database with all fields
      Given a Product aggregate with complete data
      When I save the product using OutboxRepository
      Then the product is persisted with all fields

  Rule: Data retrieval
    Scenario: Retrieve product with complete data
      Given a product exists in the database
      When I load the product from repository
      Then the product data is fully rehydrated

  Rule: Soft delete
    Scenario: Soft delete product
      Given a product exists in the database
      When I mark the product as deleted and save
      Then the product is marked as deleted in the database

  Rule: Version control
    Scenario: Version increments on update
      Given a product exists in the database
      When I update the product and save
      Then the version is incremented in storage
