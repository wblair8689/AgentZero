module.exports = {
  // Transform ESM modules in node_modules
  transformIgnorePatterns: [
    "/node_modules/(?!chai)"
  ],
  transform: {
    "^.+\\.js$": "babel-jest"
  },
  // Set test environment
  testEnvironment: "node",
  // Specify test match pattern
  testMatch: [
    "**/test/**/*.test.js"
  ],
  preset: 'ts-jest',
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/types/**/*'
  ],
  coverageDirectory: './test-reports/coverage',
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: './test-reports',
        outputName: 'jest-junit.xml',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
        ancestorSeparator: ' › ',
        usePathForSuiteName: true
      }
    ]
  ]
}; 