import os
from behave import given, when, then, step
from expects import expect, be_a, be_true, be_none, raise_error

# Import the actual agent class relative to project root
from src.agents.orchestrator import OrchestratorAgent

@given('the Orchestrator Agent is configured with ADK')
def step_impl(context):
    """
    Sets up the configuration needed to initialize the agent.
    Reads GCP Project ID and Location from environment variables.
    """
    context.project_id = os.getenv('GCP_PROJECT_ID')
    context.location = os.getenv('GCP_LOCATION', 'us-central1') # Default if not set

    if not context.project_id:
        raise ValueError("GCP_PROJECT_ID environment variable must be set.")

    # Store config for the 'When' step
    context.agent_config = {
        "project_id": context.project_id,
        "location": context.location
    }
    print(f"Agent configured for project: {context.project_id}, location: {context.location}")

@when('the agent is initialized')
def step_impl(context):
    """
    Instantiate the Orchestrator Agent using the configuration from the context.
    The agent's __init__ method handles the actual Vertex AI connection.
    """
    expect(context.agent_config).to_not(be_none)
    try:
        context.agent = OrchestratorAgent(
            project_id=context.agent_config['project_id'],
            location=context.agent_config['location']
        )
        print(f"OrchestratorAgent instantiated.")
    except Exception as e:
        # Catch potential issues during instantiation beyond what the agent handles internally
        print(f"Error during OrchestratorAgent instantiation: {e}")
        context.agent_instantiation_error = e
        context.agent = None # Ensure agent is None if instantiation failed

@then('it should be ready to accept commands')
def step_impl(context):
    """
    Verify the agent initialized successfully by checking its ready state.
    """
    expect(context.agent).to_not(be_none)
    expect(context.agent.is_ready()).to(be_true)
    print("Agent reported ready.")

@then('it should return a valid agent instance')
def step_impl(context):
    """
    Verify the agent instance created is of the expected type and not None.
    """
    expect(context.agent).to_not(be_none)
    expect(context.agent).to(be_a(OrchestratorAgent))
    print("Agent instance type is valid.") 