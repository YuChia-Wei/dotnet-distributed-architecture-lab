Feature: Complete Feature Example
  This feature demonstrates how to organize scenarios using Rule blocks.

  Rule: Happy Path Scenarios
    Scenario: Successful basic operation
      Given valid input data
      When I perform the operation
      Then the operation succeeds

    Scenario: Successful operation with optional parameters
      Given valid input with optional fields
      When I perform the operation
      Then the optional fields are persisted

  Rule: Input Validation
    Scenario: Reject null required field
      Given input with a null required field
      When I attempt the operation
      Then the operation is rejected for validation errors

    Scenario: Reject empty string field
      Given input with an empty string
      When I attempt the operation
      Then the operation is rejected for validation errors

  Rule: Business Rule Enforcement
    Scenario: Enforce unique constraint
      Given an existing entity
      When I attempt to create a duplicate
      Then the operation is rejected for business rule violations

    Scenario: Enforce maximum limit
      Given entities at the maximum limit
      When I attempt to exceed the limit
      Then the operation is rejected for business rule violations

  Rule: Error Handling
    Scenario: Handle repository failure
      Given a failing repository
      When I perform the operation
      Then the failure is handled gracefully

  Rule: Edge Cases
    Scenario: Handle maximum field length
      Given input at maximum length
      When I perform the operation
      Then the operation succeeds

  Rule: Security and Authorization
    Scenario: Prevent unauthorized access
      Given an unauthorized user
      When I attempt the operation
      Then access is denied

  Rule: Performance Requirements
    Scenario: Complete within time limit
      Given performance test data
      When I perform the operation
      Then the operation completes within the expected time limit
