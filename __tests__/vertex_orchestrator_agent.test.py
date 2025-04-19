import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the src directory to the path so we can import the agent
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/agents'))

# Import our orchestrator agent (assuming it exists at this path)
# If it doesn't exist yet, this test will fail - this is normal TDD
from orchestrator import OrchestratorAgent

class TestVertexOrchestratorAgent(unittest.TestCase):
    """Unit tests for the Vertex Orchestration Agent."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use test configuration values
        self.project_id = "test-project-id"
        self.location = "us-central1"
        
        # Create patches for external dependencies
        self.aiplatform_patch = patch('google.cloud.aiplatform.init')
        self.credentials_patch = patch('google.auth.default')
        
        # Start the patches
        self.mock_aiplatform = self.aiplatform_patch.start()
        self.mock_credentials = self.credentials_patch.start()
        
        # Configure the credentials mock to return a valid response
        self.mock_credentials.return_value = (MagicMock(), self.project_id)

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Stop the patches
        self.aiplatform_patch.stop()
        self.credentials_patch.stop()

    def test_initialization(self):
        """Test that the agent initializes correctly."""
        # Create an agent instance
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # Verify the agent initialized correctly
        self.assertTrue(agent.is_ready())
        self.assertIsNone(agent.get_status_message())
        
        # Verify that Vertex AI was initialized with the correct parameters
        self.mock_aiplatform.assert_called_once_with(
            project=self.project_id, 
            location=self.location
        )

    def test_initialization_failure(self):
        """Test agent's behavior when initialization fails."""
        # Configure the aiplatform mock to raise an exception
        self.mock_aiplatform.side_effect = Exception("Failed to initialize")
        
        # Create an agent instance - should handle the error gracefully
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # Verify the agent is not ready and has an error message
        self.assertFalse(agent.is_ready())
        self.assertIsNotNone(agent.get_status_message())
        self.assertIn("Failed to initialize", agent.get_status_message())

    def test_credential_verification(self):
        """Test the agent correctly verifies credentials."""
        # Configure the credentials mock to return None for credentials
        self.mock_credentials.return_value = (None, self.project_id)
        
        # Create an agent instance - should handle the error gracefully
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # Verify the agent is not ready and has a specific error message about credentials
        self.assertFalse(agent.is_ready())
        self.assertIsNotNone(agent.get_status_message())
        self.assertIn("Authentication error", agent.get_status_message())

    @patch('google.cloud.aiplatform.PredictionService')
    def test_route_request(self, mock_prediction_service):
        """Test that the agent can route requests to the appropriate specialized agent."""
        # Configure the mock to return a successful prediction
        mock_instance = MagicMock()
        mock_prediction_service.return_value = mock_instance
        mock_instance.predict.return_value = MagicMock(
            predictions=["ProductResearchAgent"]
        )
        
        # Create the agent and set up any route_request implementation
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # When we implement route_request, it should:
        # 1. Take a request string
        # 2. Use Vertex AI to determine the appropriate specialized agent
        # 3. Return a response with the delegated agent info
        response = agent.route_request("I need information about wireless headphones")
        
        # Verify the response structure
        self.assertIsNotNone(response)
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['delegated_to'], 'ProductResearchAgent')
        self.assertIn('request_id', response)

    @patch('google.cloud.aiplatform.PredictionService')
    def test_conversation_context(self, mock_prediction_service):
        """Test that the agent maintains conversation context across requests."""
        # Configure the mock for the first request
        mock_instance = MagicMock()
        mock_prediction_service.return_value = mock_instance
        mock_instance.predict.return_value = MagicMock(
            predictions=["ProductResearchAgent"]
        )
        
        # Create the agent
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # First request
        agent.route_request("I need information about wireless headphones")
        
        # Configure the mock for the second request - should use context
        mock_instance.predict.return_value = MagicMock(
            predictions=["ProductResearchAgent", "PreviousContext: wireless headphones"]
        )
        
        # Second request (follow-up)
        response = agent.route_request("What price range are they available in?")
        
        # Verify the context was maintained
        self.assertTrue(agent.has_conversation_context("wireless headphones"))
        self.assertEqual(response['delegated_to'], 'ProductResearchAgent')
        self.assertEqual(response['context'], 'wireless headphones')

    def test_specialized_agent_integration(self):
        """Test the orchestrator's ability to work with specialized agents."""
        # Create the agent
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # Create mock specialized agents
        product_research_agent = MagicMock()
        product_research_agent.process_task.return_value = {
            'result': 'Found 5 trending wireless headphones'
        }
        
        market_analysis_agent = MagicMock()
        market_analysis_agent.process_task.return_value = {
            'result': 'Market size is $5B annually'
        }
        
        # Register the specialized agents with the orchestrator
        agent.register_agent('ProductResearchAgent', product_research_agent)
        agent.register_agent('MarketAnalysisAgent', market_analysis_agent)
        
        # Test delegating to the product research agent
        result = agent.delegate_task('ProductResearchAgent', {
            'query': 'Find trending wireless headphones'
        })
        
        # Verify the correct agent was called with the right parameters
        product_research_agent.process_task.assert_called_once()
        self.assertEqual(result['result'], 'Found 5 trending wireless headphones')

    def test_complete_workflow(self):
        """Test the orchestrator's ability to manage a complete workflow with multiple agents."""
        # Create the agent
        agent = OrchestratorAgent(project_id=self.project_id, location=self.location)
        
        # Create mock specialized agents
        product_research_agent = MagicMock()
        market_analysis_agent = MagicMock()
        sales_opportunity_agent = MagicMock()
        product_evaluation_agent = MagicMock()
        
        # Configure return values
        product_research_agent.process_task.return_value = {'products': ['Product A', 'Product B']}
        market_analysis_agent.process_task.return_value = {'market_size': '$5B'}
        sales_opportunity_agent.process_task.return_value = {'profit_potential': 'High'}
        product_evaluation_agent.process_task.return_value = {'score': 85}
        
        # Register all specialized agents
        agent.register_agent('ProductResearchAgent', product_research_agent)
        agent.register_agent('MarketAnalysisAgent', market_analysis_agent)
        agent.register_agent('SalesOpportunityAgent', sales_opportunity_agent)
        agent.register_agent('ProductEvaluationAgent', product_evaluation_agent)
        
        # Execute the complete workflow
        result = agent.execute_workflow("Find profitable products to sell online")
        
        # Verify all agents were called in the correct sequence
        product_research_agent.process_task.assert_called_once()
        market_analysis_agent.process_task.assert_called_once()
        sales_opportunity_agent.process_task.assert_called_once()
        product_evaluation_agent.process_task.assert_called_once()
        
        # Verify the final result includes data from all agents
        self.assertIn('products', result)
        self.assertIn('market_size', result)
        self.assertIn('profit_potential', result)
        self.assertIn('score', result)

if __name__ == '__main__':
    unittest.main() 