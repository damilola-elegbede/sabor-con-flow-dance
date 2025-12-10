/**
 * Webpack Manifest Plugin
 * Generates manifest.json for Django template integration
 */

const fs = require('fs');
const path = require('path');

class WebpackManifestPlugin {
  constructor(options = {}) {
    this.options = {
      fileName: 'manifest.json',
      publicPath: '/static/js/dist/',
      writeToFileEmit: true,
      seed: {},
      filter: null,
      map: null,
      generate: null,
      sort: null,
      ...options
    };
  }

  apply(compiler) {
    const emit = (compilation, callback) => {
      const manifest = this.generateManifest(compilation);
      const manifestJson = JSON.stringify(manifest, null, 2);
      
      // Write to output directory
      const outputPath = path.join(compilation.outputOptions.path, this.options.fileName);
      fs.writeFileSync(outputPath, manifestJson);
      
      // Also write to Django static directory for development
      const djangoStaticPath = path.join(__dirname, '../static/js/dist', this.options.fileName);
      const djangoStaticDir = path.dirname(djangoStaticPath);
      
      if (!fs.existsSync(djangoStaticDir)) {
        fs.mkdirSync(djangoStaticDir, { recursive: true });
      }
      
      fs.writeFileSync(djangoStaticPath, manifestJson);
      
      console.log('✅ Webpack manifest generated:', this.options.fileName);
      callback();
    };

    if (compiler.hooks) {
      // Webpack 4+
      compiler.hooks.emit.tapAsync('WebpackManifestPlugin', emit);
    } else {
      // Webpack 3
      compiler.plugin('emit', emit);
    }
  }

  generateManifest(compilation) {
    const manifest = { ...this.options.seed };
    const stats = compilation.getStats().toJson({
      hash: true,
      publicPath: true,
      assets: true,
      chunks: false,
      modules: false,
      source: false,
      errorDetails: false,
      timings: false
    });

    // Process main assets
    stats.assets.forEach(asset => {
      if (asset.name.endsWith('.js') || asset.name.endsWith('.css')) {
        const chunkName = this.getChunkName(asset.name);
        if (chunkName) {
          manifest[chunkName] = asset.name;
        }
      }
    });

    // Add chunk relationships for better loading
    manifest._chunks = this.getChunkRelationships(compilation);
    
    // Add bundle sizes for performance monitoring
    manifest._sizes = this.getBundleSizes(stats.assets);
    
    // Add webpack hash for cache busting
    manifest._hash = stats.hash;
    
    // Add timestamp
    manifest._timestamp = Date.now();

    return manifest;
  }

  getChunkName(fileName) {
    // Extract chunk name from filename
    // e.g., "main.abc123.bundle.js" -> "main"
    const match = fileName.match(/^(.+?)\..*?\.bundle\.(js|css)$/) || 
                  fileName.match(/^(.+?)\.bundle\.(js|css)$/) ||
                  fileName.match(/^(.+?)\.(js|css)$/);
    
    return match ? match[1] : null;
  }

  getChunkRelationships(compilation) {
    const chunks = {};
    
    compilation.chunks.forEach(chunk => {
      chunks[chunk.name] = {
        id: chunk.id,
        names: chunk.names,
        files: chunk.files,
        parents: Array.from(chunk.getAllAsyncChunks()).map(c => c.name),
        children: Array.from(chunk.getAllInitialChunks()).map(c => c.name)
      };
    });

    return chunks;
  }

  getBundleSizes(assets) {
    const sizes = {};
    
    assets.forEach(asset => {
      const chunkName = this.getChunkName(asset.name);
      if (chunkName) {
        sizes[chunkName] = asset.size;
      }
    });

    return sizes;
  }
}

module.exports = WebpackManifestPlugin;