module.exports = {
  default: {
    paths: ['features/**/*.feature'],
    require: ['features/step_definitions/**/*.js'],
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
    tags: 'not @wip',
    publishQuiet: true
  }
}; 