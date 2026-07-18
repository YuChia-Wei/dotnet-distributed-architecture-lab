Feature: Create Task
  Tasks belong to projects inside a plan. Task creation must update the plan
  and publish a domain event.

  Rule: Task creation modifies plan state and emits events
    Scenario: Create a task in an existing project
      Given a plan with a project exists
      And I want to add a task to the project
      When I create a task
      Then the task should be added to the project
      And a task created event should be published

  Rule: Task requires an existing plan and project
    Scenario: Fail when plan not found
      Given a plan id that does not exist
      When I try to create a task
      Then the operation should fail with "plan not found"
      And no events should be published

    Scenario: Fail when project not found
      Given a plan exists without the project
      When I try to create a task
      Then the operation should be rejected with "Project must exist"
      And no events should be published
