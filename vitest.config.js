export default {
  test: {
    environment: 'node',
    include: ['tests/**/*.test.js'],
    globals: true,
    testTimeout: 10000,
    reporters: ['verbose']
  }
};