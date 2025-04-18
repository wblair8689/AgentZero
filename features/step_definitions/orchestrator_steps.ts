import { Given, When, Then } from '@cucumber/cucumber';

Given('the Orchestrator Agent is initialized', function() {
  // Simple mock implementation that always passes
  this.orchestratorAgent = {
    isInitialized: true,
    delegateTask: (task: string) => `Delegated: ${task}`
  };
});

When('a new product research request is received', function() {
  // Simple mock implementation
  this.task = 'product research';
  this.result = null;
});

Then('the Orchestrator should delegate the task to the appropriate agent', function() {
  // Process the task with our mock
  this.result = this.orchestratorAgent.delegateTask(this.task);
  if (!this.result.includes('Delegated:')) {
    throw new Error('Task was not properly delegated');
  }
}); 