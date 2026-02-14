module.exports = {
  presets: ['module:metro-react-native-babel-preset'],
  plugins: [
    [
      'module:react-native-dotenv',
      {
        moduleName: '@env',
        path: '.env',
        blacklist: null,
        whitelist: [
          'API_URL',
          'API_KEY',
          'FIREBASE_API_KEY',
          'FIREBASE_PROJECT_ID',
          'FIREBASE_APP_ID',
        ],
        safe: false,
        allowUndefined: true,
      },
    ],
    [
      'module-resolver',
      {
        alias: {
          '@screens': './src/screens',
          '@components': './src/components',
          '@types': './src/types',
          '@theme': './src/theme',
          '@api': './src/api',
          '@store': './src/store',
          '@hooks': './src/hooks',
          '@navigation': './src/navigation',
        },
      },
    ],
    'react-native-reanimated/plugin',
  ],
};
