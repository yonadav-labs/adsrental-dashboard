exports.config = {
  tests: './*_test.js',
  output: './output',
  helpers: {
    ErrorHandler: {
      require: "./error_handler.js",
    },
    Puppeteer: {
      url: 'http://localhost',
      show: true,
      windowSize: '1920x1080',
      getPageTimeout: 60000,
      waitForNavigation: "networkidle0",
      chrome: {
        args: ['--no-sandbox', '--window-size=1920,1080'],
        prefs: {
          'download.default_directory': 'downloads',
        }
      },
    }
  },
  include: {
    I: './steps_file.js'
  },
  bootstrap: null,
  mocha: {},
  name: 'example_test',
}