import os
from google.cloud import aiplatform
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
import logging
import uuid
import json
from typing import Dict, List, Any, Optional

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """
    Coordinates specialized agents for product research using Vertex AI.
    Initializes connection to Google Cloud Vertex AI.
    """
    def __init__(self, project_id: str, location: str):
        """
        Initializes the agent and connects to Vertex AI.

        Args:
            project_id: Google Cloud project ID.
            location: Google Cloud region (e.g., 'us-central1').
        """
        self.project_id = project_id
        self.location = location
        self._initialized = False
        self._error_message = None
        self.specialized_agents = {}
        self.conversation_contexts = {}

        try:
            # Initialize Vertex AI SDK
            # Uses Application Default Credentials (ADC) by default
            aiplatform.init(project=self.project_id, location=self.location)
            logger.info(f"Vertex AI SDK initialized successfully for project {self.project_id} in {self.location}")

            # Optional: Verify credentials explicitly
            credentials, project_id_from_creds = default()
            if not credentials:
                raise DefaultCredentialsError("Could not automatically determine credentials. Please run 'gcloud auth application-default login'.")
            logger.info(f"Using credentials for project: {project_id_from_creds}")
            # You might add a check here: if project_id_from_creds != self.project_id: logger.warning(...)

            self._initialized = True
        except DefaultCredentialsError as e:
            self._error_message = f"Authentication error: {e}. Please run 'gcloud auth application-default login' or configure service account credentials."
            logger.error(self._error_message)
        except Exception as e:
            self._error_message = f"Failed to initialize Vertex AI SDK: {e}"
            logger.error(self._error_message, exc_info=True)

    def is_ready(self) -> bool:
        """
        Checks if the agent initialized successfully and is ready.

        Returns:
            True if the agent is ready, False otherwise.
        """
        # Basic check: Did aiplatform.init() succeed?
        # More complex checks could involve a lightweight API call
        return self._initialized

    def get_status_message(self) -> Optional[str]:
        """
        Returns the error message if initialization failed.

        Returns:
            The error message string, or None if initialization was successful.
        """
        return self._error_message
        
    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """
        Registers a specialized agent with the orchestrator.
        
        Args:
            agent_name: The name/identifier for the specialized agent.
            agent_instance: The agent instance that implements a process_task method.
        """
        self.specialized_agents[agent_name] = agent_instance
        logger.info(f"Registered specialized agent: {agent_name}")
        
    def route_request(self, request: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Routes a user request. May delegate to a specialized agent or generate a plan.
        
        Args:
            request: The user's request text.
            request_id: Optional identifier for maintaining conversation context.
            
        Returns:
            A dictionary containing the response details.
        """
        if not self.is_ready():
            return {
                "status": "error",
                "message": "Orchestrator agent is not ready",
                "error": self.get_status_message()
            }
            
        # Generate a request ID if none was provided
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        # Check for existing context
        context = None
        if request_id in self.conversation_contexts:
            context = self.conversation_contexts[request_id]
            logger.info(f"Using existing context for request {request_id}: {context}")
            
        # Simple check for high-level planning requests
        request_lower = request.lower()
        if "profitable niche" in request_lower or "drop shipping" in request_lower or "business plan" in request_lower:
            plan = "I will collaborate with experts to answer question"
            logger.info(f"Request identified as high-level planning. Generating plan: {plan}")
            # Update context if needed
            self.conversation_contexts[request_id] = request # Store the original complex request
            return {
                "status": "success",
                "action": "plan_generated",
                "plan": plan,
                "request_id": request_id
            }
            
        # --- Existing Routing Logic --- 
        # In a real implementation, we would use Vertex AI for routing
        # For this implementation, we'll use keyword matching
        agent_type = None
        if "headphones" in request_lower or "product" in request_lower or "gadgets" in request_lower:
            agent_type = "ProductResearchAgent"
        elif "market" in request_lower or "watches" in request_lower:
            agent_type = "MarketAnalysisAgent"
        elif "profit" in request_lower or "sales" in request_lower:
            agent_type = "SalesOpportunityAgent"
        elif "evaluate" in request_lower or "score" in request_lower:
            agent_type = "ProductEvaluationAgent"
        else:
            agent_type = "ProductResearchAgent"  # Default
            
        # Store or update context based on the request (if not a planning request)
        if context is None:
            # Extract keywords from the request to establish context
            keywords = [word for word in request_lower.split() 
                       if len(word) > 4 and word not in ["about", "information", "what", "where", "when", "would", "should"]]
            context = " ".join(keywords)
            
        # Update the context
        self.conversation_contexts[request_id] = context
            
        response = {
            "status": "success",
            "action": "delegation", # Changed from "delegated_to" to "action"
            "delegated_to": agent_type,
            "request_id": request_id,
            "context": context
        }
        
        # If we have a registered agent of this type, delegate the task
        if agent_type in self.specialized_agents:
            try:
                logger.info(f"Delegating task to {agent_type} for request: {request}")
                agent_response = self.delegate_task(agent_type, {
                    "query": request,
                    "context": context
                })
                response["agent_response"] = agent_response
            except Exception as e:
                logger.error(f"Error delegating to {agent_type}: {e}")
                response["agent_error"] = str(e)
        else:
            logger.warning(f"Agent type {agent_type} determined but no agent registered.")
            response["status"] = "error"
            response["message"] = f"No agent available for {agent_type}"
            # Remove delegation info if no agent available
            del response["delegated_to"]
            del response["action"]
                
        return response
        
    def delegate_task(self, agent_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegates a task to a specialized agent.
        
        Args:
            agent_type: The type/name of the agent to delegate to.
            task_data: The task data to send to the agent.
            
        Returns:
            The response from the specialized agent.
            
        Raises:
            ValueError: If the specified agent type is not registered.
        """
        if agent_type not in self.specialized_agents:
            raise ValueError(f"Agent '{agent_type}' is not registered with the orchestrator")
            
        agent = self.specialized_agents[agent_type]
        return agent.process_task(task_data)
        
    def has_conversation_context(self, request_id: str) -> bool:
        """
        Checks if conversation context exists for a given request ID.
        
        Args:
            request_id: The request identifier.
            
        Returns:
            True if context exists, False otherwise.
        """
        return request_id in self.conversation_contexts
        
    def execute_workflow(self, query: str) -> Dict[str, Any]:
        """
        Executes a complete product research workflow across all specialized agents.
        
        Args:
            query: The user's query to start the workflow.
            
        Returns:
            A dictionary containing the combined results from all agents.
        """
        if not self.is_ready():
            return {
                "status": "error",
                "message": "Orchestrator agent is not ready",
                "error": self.get_status_message()
            }
            
        workflow_id = str(uuid.uuid4())
        logger.info(f"Starting workflow {workflow_id} for query: {query}")
        
        # In a real implementation with registered agents, we would:
        # 1. Call the Product Research Agent to find products
        # 2. Send those products to the Market Analysis Agent
        # 3. Send market data to the Sales Opportunity Agent
        # 4. Send all results to the Product Evaluation Agent
        
        # For this basic implementation without real agents, simulate the process
        result = {
            "status": "success",
            "workflow_id": workflow_id,
            "query": query,
            # Simulated results from specialized agents
            "products": ["Wireless Headphone A", "Wireless Headphone B"],
            "market_analysis": {
                "market_size": "$8.7B",
                "growth_rate": "12.3% annually",
                "competitors": 7
            },
            "sales_potential": {
                "profit_margin": "42%",
                "estimated_demand": "High",
                "price_sensitivity": "Medium"
            },
            "evaluation": {
                "score": 87,
                "recommendation": "Recommended for investment",
                "risk_level": "Low"
            }
        }
        
        logger.info(f"Completed workflow {workflow_id}")
        return result

# Example usage (for direct script execution testing)
if __name__ == '__main__':
    # Load from environment variables for testing
    gcp_project = os.getenv('GCP_PROJECT_ID')
    gcp_location = os.getenv('GCP_LOCATION', 'us-central1') # Default location if not set

    if not gcp_project:
        print("Error: GCP_PROJECT_ID environment variable not set.")
    else:
        orchestrator = OrchestratorAgent(project_id=gcp_project, location=gcp_location)
        if orchestrator.is_ready():
            # Register dummy agents for testing
            class DummyAgent:
                def process_task(self, task_data):
                    return {"result": "success", "data": task_data, "source": self.__class__.__name__}
            class DummyPRA(DummyAgent):
                pass
            class DummyMAA(DummyAgent):
                pass

            orchestrator.register_agent("ProductResearchAgent", DummyPRA())
            orchestrator.register_agent("MarketAnalysisAgent", DummyMAA())

            # Test basic delegation
            print("\nTesting Delegation:")
            response1 = orchestrator.route_request("research wireless headphones")
            print(json.dumps(response1, indent=2))

            # Test planning request
            print("\nTesting Planning Request:")
            response2 = orchestrator.route_request("Find a profitable niche for a drop shipping business")
            print(json.dumps(response2, indent=2))

            # Test context
            print("\nTesting Context:")
            response3 = orchestrator.route_request("Tell me more about the market", request_id=response1['request_id'])
            print(json.dumps(response3, indent=2)) 