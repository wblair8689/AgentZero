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

  # # Mark remaining scenarios to skip with @wip tag
  # @wip
  # Scenario: Delegate task to specialized agent
  #   Given the Orchestrator Agent is running
  #   And the Product Research Agent is available
  #   When I ask to research "wireless headphones"
  #   Then the Orchestrator should delegate the task to the Product Research Agent
  #   And wait for the response
  #   And return the results to me

  # @wip
  # Scenario: Maintain conversation context
  #   Given the Orchestrator Agent is running
  #   And I have previously asked about "wireless headphones"
  #   When I ask "What price range do they come in?"
  #   Then the Orchestrator should understand the context is still "wireless headphones"
  #   And provide relevant pricing information

  # @wip
  # Scenario: Handle agent state management
  #   Given the Orchestrator Agent is running
  #   When a specialized agent becomes unavailable
  #   Then the Orchestrator should detect the failure
  #   And gracefully handle the error
  #   And inform the user of the issue

  # @wip
  # Scenario: Process responses from multiple specialized agents
  #   Given the Orchestrator Agent is running
  #   And I request a complete product analysis for "wireless headphones"
  #   When all specialized agents return their results
  #   Then the Orchestrator should compile the information
  #   And present a unified response
  #   And include insights from each specialized agent

  # @wip
  # Scenario: Coordinate overall product research workflow
  #   Given the Orchestrator Agent is running
  #   When I request to find profitable products
  #   Then the Orchestrator should execute the complete workflow:
  #     | Step | Agent                | Purpose                      |
  #     | 1    | Product Research     | Identify potential products  |
  #     | 2    | Market Analysis      | Evaluate market opportunity  |
  #     | 3    | Sales Opportunity    | Calculate profit potential   |
  #     | 4    | Product Evaluation   | Score overall viability      |
  #   And present the final product recommendations 