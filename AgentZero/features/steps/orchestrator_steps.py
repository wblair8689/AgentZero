from behave import given, when, then
from flask import json
import sys
import os

# Add the project root to the Python path to allow importing app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app

@given('the Orchestrator Agent is initialized')
def step_impl_init(context):
    context.client = app.test_client()
    # You might add more initialization logic here if needed
    # For example, resetting state or setting up mocks
    context.client.testing = True # Propagate exceptions

@when('a new product research request is received')
def step_impl_request(context):
    # We'll assume a POST request to an endpoint like '/request'
    # You might need to adjust the endpoint and payload based on your app
    response = context.client.post('/request', json={
        'request_type': 'product_research',
        'details': 'Find trending gadgets'
    })
    context.response = response

@then('the Orchestrator should delegate the task to the appropriate agent')
def step_impl_delegate(context):
    assert context.response.status_code == 200, f"Expected status code 200, but got {context.response.status_code}"
    response_data = json.loads(context.response.data)
    assert 'message' in response_data, "Response JSON should contain a 'message' key"

    # Determine expected agent based on the request made in the 'When' step
    # Note: This assumes the request details are stored in context, which they are not currently.
    # Let's make the test specific to the hardcoded request for now.
    expected_agent = "Product Research Agent"
    expected_substring = f"Delegating to {expected_agent}".lower()

    assert expected_substring in response_data['message'].lower(), \
        f"Expected message to indicate delegation to '{expected_agent}', but got: {response_data['message']}" 