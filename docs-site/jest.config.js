/** @type {import("jest").Config} **/
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', { tsconfig: '<rootDir>/tsconfig.jest.json' }],
  },
  moduleNameMapper: {
    '^@site/src/components/UniversalHeader(\\/index)?$': '<rootDir>/tests/jest-mocks/components/UniversalHeader.js',
    // map Docusaurus '@site/...' path alias to the project src folder
    '^@site/(.*)$': '<rootDir>/$1',
    '^@docusaurus/Link$': '<rootDir>/tests/jest-mocks/docusaurus/Link.js',
    '^@docusaurus/router$': '<rootDir>/tests/jest-mocks/docusaurus/router.js',
    '^@docusaurus/theme-common$': '<rootDir>/tests/jest-mocks/docusaurus/theme-common.js',
    '\\.(css|less|scss)$': '<rootDir>/tests/jest-mocks/styleMock.js',
    '^react-plotly.js$': '<rootDir>/tests/jest-mocks/plotlyMock.js',
    '^plotly.js$': '<rootDir>/tests/jest-mocks/plotlyMock.js',

  },
  setupFiles: ['<rootDir>/tests/jest-setup.js'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  testPathIgnorePatterns: ['/tests/e2e/'],
};
