Feature: Market Analysis Agent Capabilities

  Scenario: Agent uses simulated Google Search for current market trends
    Given the Orchestrator Agent is initialized
    When the Orchestrator receives the query "What are the latest market trends for smart watches?"
    Then the response should indicate delegation to "MarketAnalysisAgent"
    # Check that the agent's response reflects that search was attempted (even simulated)
    And the Market Analysis Agent response source should contain "simulated search"
    # Check for specific data points expected from the simulated search
    And the Market Analysis Agent response market data should contain key "search_summary"
    And the Market Analysis Agent response market data key "identified_trends" should not be empty
    And the Market Analysis Agent response market data key "identified_competitors" list should include "Apple"
    And the Market Analysis Agent response market data key "identified_competitors" list should include "Samsung" 