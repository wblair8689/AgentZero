import os
from behave import given, when, then
# Remove Flask imports if no longer needed for other steps
# from flask import json
# from app import app

# Import the agent classes
from src.agents.orchestrator import OrchestratorAgent
from src.agents.specialized.product_research import ProductResearchAgent
from src.agents.specialized.market_analysis import MarketAnalysisAgent


@given('the Orchestrator Agent is initialized')
def step_impl_init(context):
    # Get config from environment variables
    project_id = os.getenv('GCP_PROJECT_ID')
    location = os.getenv('GCP_LOCATION', 'us-central1') # Default location

    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    # Instantiate the orchestrator if not already done
    if not hasattr(context, 'agent') or context.agent is None:
        context.agent = OrchestratorAgent(project_id=project_id, location=location)
        assert context.agent.is_ready(), f"Orchestrator failed to initialize: {context.agent.get_status_message()}"

        # Instantiate and register specialized agents (only if needed for the scenario)
        # We might optimize this later to only register if a delegation step is expected
        product_agent = ProductResearchAgent()
        market_agent = MarketAnalysisAgent()
        context.agent.register_agent("ProductResearchAgent", product_agent)
        context.agent.register_agent("MarketAnalysisAgent", market_agent)

    # Clear any previous results
    context.result = None
    context.request_query = None


@when('a new product research request is received')
def step_impl_request(context):
    # Define the request query
    context.request_query = "Find trending gadgets" # Or "research wireless headphones" to match simulated data better? Let's stick to the original idea.
    # Call the agent's routing method directly
    context.result = context.agent.route_request(context.request_query)


@then('the Orchestrator should delegate the task to the appropriate agent')
def step_impl_delegate(context):
    assert context.result is not None, "No result received from the agent"
    print(f"Agent Result: {context.result}") # Add print for debugging if needed

    assert context.result.get("status") == "success", f"Expected status 'success', but got {context.result.get('status')}. Error: {context.result.get('error') or context.result.get('message')}"
    assert context.result.get("action") == "delegation", f"Expected action 'delegation', but got '{context.result.get('action')}'"

    # Determine expected agent based on the request made in the 'When' step and orchestrator logic
    # Based on "Find trending gadgets", the orchestrator routes to ProductResearchAgent
    expected_agent_type = "ProductResearchAgent"
    expected_agent_name_in_source = "Product Research Agent" # Match the name used in the agent's simulated source string

    assert context.result.get("delegated_to") == expected_agent_type, \
        f"Expected delegation to '{expected_agent_type}', but got: {context.result.get('delegated_to')}"

    # Check if the specialized agent actually processed the request
    assert "agent_response" in context.result, "Orchestrator did not return an agent response."
    agent_response = context.result["agent_response"]
    assert agent_response.get("result") == "success", f"Specialized agent returned an error: {agent_response}"

    # Check the source more simply
    actual_source = agent_response.get('source')
    assert actual_source is not None, "Agent response source is missing"
    assert actual_source.startswith(expected_agent_name_in_source), f"Expected source to start with '{expected_agent_name_in_source}', but got '{actual_source}'"

    assert agent_response.get("query") == context.request_query, f"Agent processed wrong query: {agent_response.get('query')}"

# --- New Steps for Planning Scenario --- 

@when('the user asks "{query}"')
def step_impl_ask_question(context, query):
    context.request_query = query
    context.result = context.agent.route_request(context.request_query)

@then('the Orchestrator should generate a plan to answer the question')
def step_impl_check_plan_generation(context):
    assert context.result is not None, "No result received from the agent"
    print(f"Agent Result: {context.result}") # Add print for debugging
    assert context.result.get("status") == "success", f"Expected status 'success', but got '{context.result.get('status')}'"
    assert context.result.get("action") == "plan_generated", f"Expected action 'plan_generated', but got '{context.result.get('action')}'"
    assert "plan" in context.result, "Result dictionary does not contain a 'plan' key"

@then('the plan should state "{expected_plan}"')
def step_impl_check_plan_content(context, expected_plan):
    assert context.result is not None, "No result received from the agent (check previous step)"
    actual_plan = context.result.get("plan")
    assert actual_plan == expected_plan, f"Expected plan '{expected_plan}', but got '{actual_plan}'" 