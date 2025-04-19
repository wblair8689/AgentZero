// This file provides Jest mocking functionality to Cucumber step definitions

// Import actual jest module
const jestFn = require('jest-mock');

// Store mocked modules
const mockedModules = new Map();

// Create jest object with mocking functionality
global.jest = {
  fn: function(implementation) {
    const mockFn = jestFn.fn(implementation);
    
    // Add mockImplementation method to match Jest's API
    mockFn.mockImplementation = function(implementation) {
      return jestFn.fn(implementation);
    };
    
    // Add mockReturnValue method
    mockFn.mockReturnValue = function(value) {
      return jestFn.fn(() => value);
    };
    
    return mockFn;
  },
  
  mock: function(moduleName, factory) {
    // Store the mock factory
    mockedModules.set(moduleName, factory);
    
    // Intercept subsequent requires of this module
    // This approach is simplified; real Jest does more sophisticated module interception
    const originalModule = require.cache[require.resolve(moduleName)];
    if (originalModule) {
      // Module was already loaded, we'll update its exports
      const mockExports = factory();
      for (const key in mockExports) {
        if (Object.prototype.hasOwnProperty.call(mockExports, key)) {
          originalModule.exports[key] = mockExports[key];
        }
      }
      return originalModule.exports;
    } else {
      // Module hasn't been loaded yet, mock will be applied on first require
      // Real implementation would need to monkey-patch require
      console.log(`Module ${moduleName} not yet loaded, mock will apply on require`);
      return factory();
    }
  },
  
  clearAllMocks: function() {
    // This function would reset all mocks
    // In a simple implementation, we'll just log this action
    console.log('Clearing all mocks');
  },
  
  resetAllMocks: function() {
    // This function would reset all mocks
    console.log('Resetting all mocks');
  }
};

// Monkey patch require to handle mocked modules
const originalRequire = module.constructor.prototype.require;
module.constructor.prototype.require = function(path) {
  if (mockedModules.has(path)) {
    console.log(`Using mocked module for: ${path}`);
    return mockedModules.get(path)();
  }
  return originalRequire.apply(this, arguments);
};

// Export jest object for importing in step files
module.exports = global.jest; 