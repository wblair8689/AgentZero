module.exports = {
  default: {
    formatOptions: {
      snippetInterface: 'synchronous'
    },
    requireModule: ['ts-node/register'],
    require: ['features/step_definitions/**/*.ts'],
    paths: ['features/**/*.feature'],
    format: ['progress-bar'],
    publishQuiet: true
  },
  ci: {
    formatOptions: {
      snippetInterface: 'synchronous'
    },
    requireModule: ['ts-node/register'],
    require: ['features/step_definitions/**/*.ts'],
    paths: ['features/**/*.feature'],
    format: [
      'json:test-reports/cucumber-report.json',
      'html:test-reports/cucumber-report.html'
    ],
    publishQuiet: true
  }
}; 