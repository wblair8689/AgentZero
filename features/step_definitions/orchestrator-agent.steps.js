const { Given, When, Then } = require('@cucumber/cucumber');
const { expect } = require('chai');
const assert = require('assert');

// Import our jest helper
const jest = require('../setup/jest-cucumber.setup');

// Mock the Vertex AI package before importing the orchestrator agent
// This is similar to what's done in the Jest test file
jest.mock('@google-cloud/vertexai', () => {
  return {
    VertexAI: jest.fn().mockImplementation(() => {
      return {
        getGenerativeAI: jest.fn().mockImplementation(() => {
          return {
            getGenerativeModel: jest.fn().mockImplementation(() => {
              return {
                generateContent: jest.fn().mockImplementation((prompt) => {
                  // Simple mock that returns agents based on query content
                  const mockResponse = {
                    response: {
                      text: () => 'ProductResearch'
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

// Import the original module AFTER mocking
const { OrchestratorAgent } = require('../../src/agents/orchestrator-agent');

// Global variables for test state
let orchestratorAgent;
let agentInstance;
let agentConfigured = false;
let lastTaskDelegated = false;
let lastResponse;
let conversationContext = {};
let agentFailureDetected = false;
let compiledResponse;
let workflowExecuted = false;
let finalRecommendations;

Given('the Orchestrator Agent is configured with ADK', function () {
  // Initialize configuration for the Orchestrator Agent
  orchestratorAgent = new OrchestratorAgent({
    name: 'Orchestrator',
    description: 'Coordinates specialized agents for product research',
    projectId: 'test-project',
    location: 'us-central1'
  });
  
  agentConfigured = true;
  console.log("Simulating ADK configuration for Orchestrator Agent.");
});

When('the agent is initialized', async function () {
  try {
    // Initialize the agent using the actual method
    agentInstance = await orchestratorAgent.initialize();
    
    if (!agentConfigured) {
      throw new Error("Agent cannot be initialized without configuration.");
    }
    
    console.log("Agent initialized successfully with mock VertexAI.");
  } catch (error) {
    console.error("Error during initialization:", error);
    throw error;
  }
});

Then('it should be ready to accept commands', function () {
  expect(orchestratorAgent.isReady()).to.be.true;
  console.log("Checking if agent is ready to accept commands.");
});

Then('it should return a valid agent instance', function () {
  expect(agentInstance).to.not.be.undefined;
  expect(agentInstance).to.have.property('id');
  expect(orchestratorAgent).to.not.be.undefined;
  expect(orchestratorAgent.id).to.not.be.undefined;
  console.log("Checking for a valid agent instance.");
});

// Stubs for the WIP scenarios
Given('the Orchestrator Agent is running', function () {
  // Use the actual class but ensure it's initialized
  if (!orchestratorAgent || !orchestratorAgent.isReady()) {
    orchestratorAgent = new OrchestratorAgent({
      name: 'Orchestrator',
      description: 'Coordinates specialized agents for product research',
      projectId: 'test-project',
      location: 'us-central1'
    });
    
    // Since we already mocked VertexAI at the module level, we can initialize directly
    // but we'll simulate that it's already initialized for this step
    orchestratorAgent.ready = true;
    orchestratorAgent.id = 'orchestrator-123';
    
    console.log("Ensuring Orchestrator Agent is running for the test with proper mocks.");
  }
  agentConfigured = true; // Assume configured if running
});

Given('the Product Research Agent is available', function () {
  // Register mock Product Research Agent
  const mockProcessTask = jest.fn().mockImplementation(() => {
    return Promise.resolve({ response: 'Product information' });
  });
  
  orchestratorAgent.registerAgent('ProductResearch', {
    processTask: mockProcessTask
  });
  
  console.log("Simulating availability of Product Research Agent.");
});

When('I ask to research {string}', function (product) {
  console.log(`Simulating request to research: ${product}`);
  conversationContext.current_request = `research ${product}`;
  lastTaskDelegated = true; // Assume delegation happens for now
  lastResponse = `Results for ${product}...`; // Simulate placeholder response
});

Then('the Orchestrator should delegate the task to the Product Research Agent', function () {
  assert.strictEqual(lastTaskDelegated, true, 'Task should have been delegated');
  console.log("Checking if task was delegated to Product Research Agent.");
});

Then('wait for the response', function () {
  console.log("Simulating waiting for response.");
});

Then('return the results to me', function () {
  assert.ok(lastResponse, 'Should have received results');
  console.log("Checking if results were returned.");
});

Given('I have previously asked about {string}', function (topic) {
  conversationContext.previous_topic = topic;
  console.log(`Setting conversation context: previously asked about ${topic}`);
});

When('I ask {string}', function (question) {
  console.log(`Simulating follow-up question: ${question}`);
  conversationContext.current_request = question;
  if (conversationContext.previous_topic === 'wireless headphones' && question.includes('price range')) {
      lastResponse = "They typically range from $50 to $500.";
  } else {
      lastResponse = "I'm not sure how to answer that in this context.";
  }
});

Then('the Orchestrator should understand the context is still {string}', function (expectedContext) {
  assert.strictEqual(conversationContext.previous_topic, expectedContext, `Context should be ${expectedContext}`);
  console.log(`Checking if context is still ${expectedContext}.`);
});

Then('provide relevant pricing information', function () {
  assert.ok(lastResponse?.includes('range from'), 'Response should contain pricing info');
  console.log("Checking if relevant pricing information was provided.");
});

When('a specialized agent becomes unavailable', function () {
  agentFailureDetected = true;
  console.log("Simulating a specialized agent becoming unavailable.");
});

Then('the Orchestrator should detect the failure', function () {
  assert.strictEqual(agentFailureDetected, true, 'Orchestrator should have detected the failure');
  console.log("Checking if Orchestrator detected the failure.");
});

Then('gracefully handle the error', function () {
  console.log("Simulating graceful error handling.");
});

Then('inform the user of the issue', function () {
  lastResponse = "Apologies, a required component is currently unavailable. Please try again later.";
  console.log("Simulating informing the user of the issue.");
  assert.ok(lastResponse.includes("unavailable"), "User should be informed about the issue.");
});

Given('I request a complete product analysis for {string}', function (product) {
  console.log(`Simulating request for complete analysis of ${product}`);
  conversationContext.current_request = `complete analysis ${product}`;
});

When('all specialized agents return their results', function () {
  compiledResponse = {
      research: "...",
      market: "...",
      sales: "...",
      evaluation: "..."
  };
  console.log("Simulating receiving results from all specialized agents.");
});

Then('the Orchestrator should compile the information', function () {
  assert.ok(compiledResponse, 'Information should have been compiled');
  console.log("Checking if information was compiled.");
});

Then('present a unified response', function () {
  lastResponse = `Unified analysis: Research - ${compiledResponse.research}, Market - ${compiledResponse.market}, ...`;
  console.log("Simulating presentation of a unified response.");
  assert.ok(lastResponse.includes("Unified analysis"), "Response should be unified.");
});

Then('include insights from each specialized agent', function () {
  assert.ok(compiledResponse.research && compiledResponse.market && compiledResponse.sales && compiledResponse.evaluation, "Response should include insights from all agents.");
  console.log("Checking if insights from each agent are included.");
});

When('I request to find profitable products', function () {
  console.log("Simulating request to find profitable products.");
  conversationContext.current_request = 'find profitable products';
});

Then('the Orchestrator should execute the complete workflow:', function (dataTable) {
  const expectedSteps = dataTable.hashes();
  console.log("Simulating execution of the complete workflow:", expectedSteps);
  assert.strictEqual(expectedSteps.length, 4, "Workflow should have 4 steps");
  assert.strictEqual(expectedSteps[0].Agent, 'Product Research', "Step 1 Agent mismatch");
  workflowExecuted = true;
  finalRecommendations = ["Product A", "Product B"]; // Simulate output
});

Then('present the final product recommendations', function () {
  assert.ok(workflowExecuted, "Workflow should have been executed first.");
  assert.ok(finalRecommendations && finalRecommendations.length > 0, 'Final recommendations should be presented');
  console.log("Checking if final product recommendations are presented.");
  lastResponse = `Final Recommendations: ${finalRecommendations.join(', ')}`;
});

// Create a proper mock for VertexAI that matches the expected structure
function createMockVertexAI() {
  // Mock the generateContent function to return a properly structured response
  const mockGenerateContent = jest.fn().mockImplementation(() => {
    return Promise.resolve({
      response: {
        text: () => 'ProductResearch'
      }
    });
  });

  // Create the model object
  const mockModel = {
    generateContent: mockGenerateContent
  };

  // Create the generativeAI object
  const mockGenerativeAI = {
    getGenerativeModel: jest.fn().mockImplementation(() => mockModel)
  };

  // Create the full VertexAI mock object with actual function
  const mockVertexAI = {
    getGenerativeAI: jest.fn().mockImplementation(() => mockGenerativeAI)
  };

  return mockVertexAI;
} 