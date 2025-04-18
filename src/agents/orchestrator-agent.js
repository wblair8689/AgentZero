const { VertexAI } = require('@google-cloud/vertexai');

/**
 * OrchestratorAgent - A central agent that coordinates the specialized agents
 * using Google Vertex AI Agent Development Kit (ADK)
 */
class OrchestratorAgent {
  /**
   * Creates a new OrchestratorAgent
   * @param {Object} config - Configuration for the agent
   * @param {string} config.name - Name of the agent
   * @param {string} config.description - Description of the agent's purpose
   * @param {string} [config.projectId] - Google Cloud project ID
   * @param {string} [config.location] - Google Cloud location
   */
  constructor(config) {
    this.name = config.name;
    this.description = config.description;
    this.projectId = config.projectId || process.env.GOOGLE_CLOUD_PROJECT;
    this.location = config.location || 'us-central1';
    this.ready = false;
    this.id = null;
    this.specializedAgents = {};
    this.vertexAI = null;
    this.generativeModel = null;
  }

  /**
   * Initializes the agent with ADK
   * @returns {Promise<Object>} - The initialized agent instance
   */
  async initialize() {
    try {
      // Initialize Vertex AI
      this.vertexAI = new VertexAI({
        project: this.projectId,
        location: this.location,
      });

      // Create a generative model interface
      const generativeAI = this.vertexAI.getGenerativeAI();
      this.generativeModel = generativeAI.getGenerativeModel({
        model: 'gemini-1.5-pro',
      });

      // For now we just simulate an agent ID
      this.id = `orchestrator-${Date.now()}`;
      this.ready = true;
      
      return {
        id: this.id,
        name: this.name,
        ready: this.ready
      };
    } catch (error) {
      console.error('Error initializing Orchestrator Agent:', error);
      throw error;
    }
  }

  /**
   * Checks if the agent is ready to accept commands
   * @returns {boolean} - True if the agent is ready
   */
  isReady() {
    return this.ready;
  }

  /**
   * Registers a specialized agent with the orchestrator
   * @param {string} agentType - Type of the specialized agent (e.g., "ProductResearch")
   * @param {Object} agent - The agent instance to register
   */
  registerAgent(agentType, agent) {
    this.specializedAgents[agentType] = agent;
  }

  /**
   * Delegates a task to a specialized agent
   * @param {string} agentType - Type of agent to delegate to
   * @param {Object} task - The task to delegate
   * @returns {Promise<Object>} - The result from the specialized agent
   */
  async delegateTask(agentType, task) {
    // Check if agent exists
    if (!this.specializedAgents[agentType]) {
      throw new Error(`Specialized agent "${agentType}" not registered`);
    }

    // For now, simply delegate to the specialized agent
    return this.specializedAgents[agentType].processTask(task);
  }

  /**
   * Processes a user query by determining which specialized agent to use
   * @param {string} query - The user's query
   * @returns {Promise<Object>} - The response to the user
   */
  async processQuery(query) {
    if (!this.isReady()) {
      throw new Error('Orchestrator Agent is not initialized');
    }

    try {
      // Use Gemini to determine which specialized agent to use
      const prompt = `
        Given this user query: "${query}"
        
        Which of these specialized agents should handle it?
        - ProductResearch: Researches product information, specifications, and reviews
        - MarketAnalysis: Analyzes market trends and competition
        - SalesOpportunity: Evaluates sales potential and profit margins
        - ProductEvaluation: Evaluates overall product viability
        
        Return ONLY the name of ONE most appropriate agent, nothing else.
      `;

      const result = await this.generativeModel.generateContent(prompt);
      const response = await result.response;
      const agentType = response.text().trim();
      
      // Check if the determined agent exists
      if (!this.specializedAgents[agentType]) {
        // If not, use a fallback approach
        return {
          response: `I don't have a specialized agent to handle queries about ${agentType} yet.`,
          agentUsed: 'None'
        };
      }
      
      // Delegate the task to the appropriate agent
      const taskResult = await this.delegateTask(agentType, { query });
      
      return {
        ...taskResult,
        agentUsed: agentType
      };
    } catch (error) {
      console.error('Error processing query:', error);
      return {
        response: 'Sorry, I encountered an error while processing your request.',
        error: error.message
      };
    }
  }
}

module.exports = { OrchestratorAgent }; 