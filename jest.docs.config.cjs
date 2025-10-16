module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', { tsconfig: 'tsconfig.jest.json' }],
  },
  testMatch: ['**/docs-site/src/**/__tests__/**/*.test.(ts|tsx)'],
  moduleNameMapper: {
    '\\.(css|less|scss)$': '<rootDir>/__mocks__/styleMock.js',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  // Map Docusaurus @site alias used in tests to the docs-site source folder
  moduleNameMapper: Object.assign({
    // @site/src/... -> docs-site/src/... so map to docs-site/$1 to avoid double 'src'
    '^@site\/(.*)$': '<rootDir>/docs-site/$1'
  ,
    // Map Docusaurus package imports to local lightweight mocks for tests
    '^@docusaurus\/(.*)$': '<rootDir>/__mocks__/docusaurus/$1.js'
  }, {
    '\\.(css|less|scss)$': '<rootDir>/__mocks__/styleMock.js',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  }),
  // Ensure Docusaurus packages in node_modules are transformed (they use ESM syntax)
  transformIgnorePatterns: ['/node_modules/(?!(?:@docusaurus)/)'],
  // Transform JS as well as TS so ESM packages in node_modules are handled by ts-jest
  transform: {
    '^.+\\.(ts|tsx|js|jsx)$': ['ts-jest', { tsconfig: 'tsconfig.jest.json' }],
  },
  setupFilesAfterEnv: ['<rootDir>/docs-site/tests/jest-setup.js'],
};
