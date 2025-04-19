from behave import given, when, then
from hamcrest import assert_that, equal_to, is_not, none, contains_string

# Import the orchestrator agent implementation
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/agents'))
from orchestrator import OrchestratorAgent

# Set up mocks if needed
from unittest.mock import patch, MagicMock

@given('the Vertex Orchestrator Agent is configured with valid credentials')
def step_impl_vertex_config(context):
    """Configure the Vertex Orchestrator Agent with valid project settings."""
    # Use test values or environment variables
    context.agent_config = {
        'project_id': os.environ.get('GOOGLE_CLOUD_PROJECT', 'agentzero-457213'),
        'location': os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
    }
    print(f"Configured Vertex Orchestrator Agent with: {context.agent_config}")

@given('the Vertex Orchestrator Agent is connected to Vertex AI')
def step_impl_vertex_connect(context):
    """Create and connect the Orchestrator Agent to Vertex AI."""
    # This could be real or mocked depending on test environment
    with patch('google.cloud.aiplatform.init') as mock_init:
        mock_init.return_value = None  # Simulate successful initialization
        context.agent = OrchestratorAgent(
            project_id=context.agent_config['project_id'],
            location=context.agent_config['location']
        )
        assert_that(context.agent.is_ready(), equal_to(True))

@when('a request for "{request_type}" is sent to the Vertex Orchestrator')
def step_impl_vertex_request(context, request_type):
    """Send a specific request to the Vertex Orchestrator Agent."""
    # Mock the agent's behavior for receiving requests
    # In a real implementation, this would interact with the Vertex AI API
    with patch.object(context.agent, 'route_request', return_value={
        'status': 'success',
        'delegated_to': f"{request_type.replace(' ', '')}Agent",
        'request_id': '12345'
    }):
        context.request_type = request_type
        context.response = context.agent.route_request(request_type)
        print(f"Request response: {context.response}")

@then('the Vertex Orchestrator should recognize it as a "{agent_type}" task')
def step_impl_vertex_recognition(context, agent_type):
    """Verify the Orchestrator correctly recognizes the request type."""
    assert_that(context.response, is_not(none()))
    assert_that(context.response['status'], equal_to('success'))
    expected_agent = f"{agent_type.replace(' ', '')}Agent"
    assert_that(context.response['delegated_to'], equal_to(expected_agent))

@then('the Vertex Orchestrator should delegate to the "{agent_name}" specialized agent')
def step_impl_vertex_delegation(context, agent_name):
    """Verify the Orchestrator delegates to the correct specialized agent."""
    assert_that(context.response, is_not(none()))
    assert_that(context.response['delegated_to'], equal_to(agent_name))
    
@then('the Vertex Orchestrator should maintain the conversation context')
def step_impl_vertex_context(context):
    """Verify that the Orchestrator maintains conversation context across requests."""
    # Implement logic to check that context is maintained
    # This would typically involve making a follow-up request and checking
    # that the agent's response shows understanding of the previous interaction
    with patch.object(context.agent, 'has_conversation_context', return_value=True):
        has_context = context.agent.has_conversation_context(context.request_type)
        assert_that(has_context, equal_to(True))

@then('the Vertex Orchestrator should return a structured response')
def step_impl_vertex_response(context):
    """Verify the response from the Orchestrator is properly structured."""
    assert_that(context.response, is_not(none()))
    assert_that(context.response, contains_string('status'))
    assert_that(context.response, contains_string('delegated_to'))
    assert_that(context.response, contains_string('request_id')) 