import postcssImport from 'postcss-import';
import postcssPresetEnv from 'postcss-preset-env';
import autoprefixer from 'autoprefixer';
import cssnano from 'cssnano';
import { buildConfig } from './build.config.js';

export default {
  plugins: [
    postcssImport(),
    postcssPresetEnv({
      stage: 1,
      features: {
        'custom-properties': false, // Preserve CSS custom properties
        'nesting-rules': true
      }
    }),
    autoprefixer(buildConfig.css.autoprefixer),
    ...(process.env.NODE_ENV === 'production' ? [
      cssnano(buildConfig.css.cssnano)
    ] : [])
  ]
};