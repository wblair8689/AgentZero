module.exports = {
  default: {
    requireModule: [
      'ts-node/register'
    ],
    require: [
      'features/step_definitions/**/*.ts' // Path to your step definitions
    ],
    paths: [
      'features/**/*.feature' // Path to your feature files
    ],
    format: [
      'progress-bar'
    ],
    publishQuiet: true
  }
}; 