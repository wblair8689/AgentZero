import unittest
import os
import sys
import uuid
import time

# Add the src directory to the path so we can import the agent
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/agents'))

# Import our orchestrator agent
from orchestrator import OrchestratorAgent

# Import the specialized agents
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/agents/specialized'))
from product_research import ProductResearchAgent
from market_analysis import MarketAnalysisAgent

class TestVertexOrchestratorIntegration(unittest.TestCase):
    """Integration tests for the Vertex Orchestration Agent.
    
    These tests use actual Vertex AI connections and real agent implementations.
    Requires valid Google Cloud credentials to be configured.
    """

    @classmethod
    def setUpClass(cls):
        """Set up resources for all tests.
        
        Ensure Google Cloud credentials are properly configured before running.
        You can run 'gcloud auth application-default login' to set this up.
        """
        # Check for required environment variables
        cls.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "agentzero-457213")
        cls.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        print(f"\nSetting up Vertex Orchestrator Agent with:")
        print(f"- Project ID: {cls.project_id}")
        print(f"- Location: {cls.location}")
        
        # Create the main orchestrator agent
        cls.orchestrator = OrchestratorAgent(
            project_id=cls.project_id,
            location=cls.location
        )
        
        # Fail fast if the agent couldn't initialize
        if not cls.orchestrator.is_ready():
            raise RuntimeError(f"Orchestrator agent failed to initialize: {cls.orchestrator.get_status_message()}")
            
        print("✓ Orchestrator Agent initialized successfully")
        
        # Initialize and register specialized agents
        cls.product_research = ProductResearchAgent()
        cls.market_analysis = MarketAnalysisAgent()
        
        # Register the specialized agents with the orchestrator
        cls.orchestrator.register_agent('ProductResearchAgent', cls.product_research)
        cls.orchestrator.register_agent('MarketAnalysisAgent', cls.market_analysis)
        
        print("✓ Specialized agents registered successfully")

    def test_01_agent_initialization(self):
        """Verify that the agent initializes correctly with Vertex AI."""
        self.assertTrue(self.orchestrator.is_ready())
        self.assertIsNone(self.orchestrator.get_status_message())
        self.assertEqual(len(self.orchestrator.specialized_agents), 2)
        print("\n✓ Agent initialization successful")

    def test_02_route_product_research_request(self):
        """Test routing a product research request to the appropriate agent."""
        # This product query should be routed to the Product Research Agent
        response = self.orchestrator.route_request("I need information about wireless headphones")
        
        # Verify the response structure
        self.assertIsNotNone(response)
        self.assertEqual(response.get('status'), 'success')
        self.assertEqual(response.get('delegated_to'), 'ProductResearchAgent')
        self.assertIn('request_id', response)
        
        # Verify we got agent-specific response data
        self.assertIn('agent_response', response)
        self.assertIn('products', response['agent_response'])
        self.assertTrue(len(response['agent_response']['products']) > 0)
        
        # Log the response for debugging
        print(f"\nProduct Research Response: {response}")
        print(f"✓ Found {response['agent_response']['total_found']} products")

    def test_03_route_market_analysis_request(self):
        """Test routing a market analysis request to the appropriate agent."""
        # This market query should be routed to the Market Analysis Agent
        response = self.orchestrator.route_request("What is the market like for smart watches?")
        
        # Verify the response structure
        self.assertIsNotNone(response)
        self.assertEqual(response.get('status'), 'success')
        self.assertEqual(response.get('delegated_to'), 'MarketAnalysisAgent')
        self.assertIn('request_id', response)
        
        # Verify we got agent-specific response data
        self.assertIn('agent_response', response)
        self.assertIn('market_data', response['agent_response'])
        
        # Log the response for debugging
        print(f"\nMarket Analysis Response: {response}")
        print(f"✓ Market size: {response['agent_response']['market_data']['market_size']}")

    def test_04_conversation_context(self):
        """Test the orchestrator's ability to maintain conversation context."""
        # First request establishes context
        request_id = str(uuid.uuid4())
        response1 = self.orchestrator.route_request(
            "I'm interested in wireless headphones",
            request_id=request_id
        )
        
        # Verify first response
        self.assertEqual(response1.get('status'), 'success')
        
        # Second request should maintain context from the first
        response2 = self.orchestrator.route_request(
            "What price range are they available in?",
            request_id=request_id  # Same request ID to maintain session
        )
        
        # Verify context was maintained
        self.assertEqual(response2.get('status'), 'success')
        self.assertTrue(self.orchestrator.has_conversation_context(request_id))
        self.assertIn('context', response2)
        self.assertIn('wireless', response2.get('context', '').lower())
        
        # Verify the agent used the appropriate context
        self.assertEqual(response2.get('delegated_to'), 'ProductResearchAgent')
        
        # Log the responses for debugging
        print(f"\nContext Test - First Response: {response1}")
        print(f"Context Test - Second Response: {response2}")
        print(f"✓ Context maintained: {response2['context']}")

    def test_05_complete_workflow(self):
        """Test the execution of a complete workflow across multiple specialized agents."""
        # This test can be expanded as more specialized agents are implemented
        # For now, we're testing with the agents we have
        
        query = "Find profitable wireless headphones to sell online"
        result = self.orchestrator.execute_workflow(query)
        
        # Verify the workflow executed successfully
        self.assertIsNotNone(result)
        self.assertEqual(result.get('status'), 'success')
        
        # Verify the result contains expected data
        self.assertIn('products', result)
        self.assertIn('market_analysis', result)
        
        # Log the workflow result
        print(f"\nComplete Workflow Result:")
        print(f"- Query: {result.get('query')}")
        print(f"- Workflow ID: {result.get('workflow_id')}")
        print(f"- Products found: {len(result.get('products', []))}")
        print(f"- Market size: {result.get('market_analysis', {}).get('market_size', 'N/A')}")
        print(f"✓ Workflow completed successfully")

if __name__ == '__main__':
    unittest.main() 