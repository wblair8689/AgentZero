// Mock the Vertex AI package
jest.mock('@google-cloud/vertexai', () => {
  // Mock implementation
  return {
    VertexAI: jest.fn().mockImplementation(() => {
      return {
        getGenerativeAI: jest.fn().mockImplementation(() => {
          return {
            getGenerativeModel: jest.fn().mockImplementation(() => {
              return {
                generateContent: jest.fn().mockImplementation((prompt) => {
                  // Simple mock that returns agents based on query content
                  let agentType;
                  
                  if (prompt.includes('wireless headphones products')) {
                    agentType = 'ProductResearch';
                  } else if (prompt.includes('smart watches')) {
                    agentType = 'MarketAnalysis';
                  } else {
                    agentType = 'ProductEvaluation';
                  }
                  
                  const mockResponse = {
                    response: {
                      text: () => agentType
                    }
                  };
                  return Promise.resolve(mockResponse);
                })
              };
            })
          };
        })
      };
    })
  };
});

const { OrchestratorAgent } = require('../src/agents/orchestrator-agent');

describe('OrchestratorAgent', () => {
  let agent;
  
  beforeEach(() => {
    agent = new OrchestratorAgent({
      name: 'TestOrchestrator',
      description: 'Test orchestrator agent',
      projectId: 'test-project',
      location: 'test-location'
    });
  });
  
  describe('initialization', () => {
    it('should create an agent with the specified name', () => {
      expect(agent.name).toBe('TestOrchestrator');
      expect(agent.description).toBe('Test orchestrator agent');
      expect(agent.projectId).toBe('test-project');
      expect(agent.location).toBe('test-location');
    });
    
    it('should not be ready initially', () => {
      expect(agent.isReady()).toBe(false);
    });
    
    it('should be ready after initialization', async () => {
      const instance = await agent.initialize();
      expect(agent.isReady()).toBe(true);
      expect(instance).toHaveProperty('id');
      expect(instance.name).toBe('TestOrchestrator');
    });
  });
  
  describe('specialized agent registration', () => {
    it('should register a specialized agent', () => {
      const mockAgent = { 
        processTask: () => ({ result: 'success' }) 
      };
      
      agent.registerAgent('ProductResearch', mockAgent);
      expect(agent.specializedAgents).toHaveProperty('ProductResearch');
      expect(agent.specializedAgents.ProductResearch).toBe(mockAgent);
    });
    
    it('should throw an error when delegating to non-existent agent', async () => {
      await expect(
        agent.delegateTask('NonExistentAgent', { query: 'test' })
      ).rejects.toThrow(/not registered/);
    });
    
    it('should delegate tasks to specialized agents', async () => {
      const mockAgent = { 
        processTask: (task) => Promise.resolve({ 
          result: 'processed', 
          query: task.query 
        }) 
      };
      
      agent.registerAgent('ProductResearch', mockAgent);
      
      const result = await agent.delegateTask('ProductResearch', { 
        query: 'wireless headphones' 
      });
      
      expect(result).toHaveProperty('result', 'processed');
      expect(result).toHaveProperty('query', 'wireless headphones');
    });
  });

  describe('query processing', () => {
    beforeEach(async () => {
      // Initialize the agent before testing
      await agent.initialize();
      
      // Register mock specialized agents
      agent.registerAgent('ProductResearch', { 
        processTask: (task) => Promise.resolve({ 
          response: `Product research results for: ${task.query}` 
        }) 
      });
      
      agent.registerAgent('MarketAnalysis', { 
        processTask: (task) => Promise.resolve({ 
          response: `Market analysis results for: ${task.query}` 
        }) 
      });
    });
    
    it('should route product queries to the ProductResearch agent', async () => {
      const result = await agent.processQuery('Tell me about wireless headphones products');
      expect(result).toHaveProperty('response', 'Product research results for: Tell me about wireless headphones products');
      expect(result).toHaveProperty('agentUsed', 'ProductResearch');
    });
    
    it('should route market queries to the MarketAnalysis agent', async () => {
      const result = await agent.processQuery('What is the market like for smart watches?');
      expect(result).toHaveProperty('response', 'Market analysis results for: What is the market like for smart watches?');
      expect(result).toHaveProperty('agentUsed', 'MarketAnalysis');
    });
    
    it('should handle queries for non-existing agent types', async () => {
      // Our mock will return ProductEvaluation for this query, but we haven't registered that agent
      const result = await agent.processQuery('Evaluate this gadget');
      expect(result).toHaveProperty('response', expect.stringContaining('don\'t have a specialized agent'));
      expect(result).toHaveProperty('agentUsed', 'None');
    });
  });
}); 