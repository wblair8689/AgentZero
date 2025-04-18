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
  }
}; 