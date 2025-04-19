Feature: Orchestrator Agent
  As a user
  I want an Orchestrator Agent that coordinates specialized agents
  So that I can identify great products to sell online

  # This is the simplest scenario - mark as runnable
  Scenario: Initialize Orchestrator Agent
    Given the Orchestrator Agent is configured with ADK
    When the agent is initialized
    Then it should be ready to accept commands
    And it should return a valid agent instance

  # Scenario for direct agent interaction (using steps from orchestrator_steps.py)
  Scenario: Basic Product Research Request Delegation
    Given the Orchestrator Agent is initialized
    When a new product research request is received
    Then the Orchestrator should delegate the task to the appropriate agent

  Scenario: Generate Plan for High-Level Request
    Given the Orchestrator Agent is initialized
    When the user asks "Find a profitable niche for a drop shipping business"
    Then the Orchestrator should generate a plan to answer the question
    And the plan should state "I will collaborate with experts to answer question"
