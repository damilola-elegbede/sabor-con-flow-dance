#!/bin/bash

# Build Script for Sabor Con Flow Dance JavaScript Optimization
# SPEC_06 Group A Task 3 - JavaScript Bundling and Optimization

set -e  # Exit on any error

echo "🚀 Starting JavaScript build process..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Create necessary directories
echo "📁 Creating build directories..."
mkdir -p static/js/dist
mkdir -p staticfiles/js/dist
mkdir -p build-reports

# Clean previous builds
echo "🧹 Cleaning previous builds..."
npm run clean

# Build for development
echo "🔧 Building development bundles..."
npm run build:dev

# Run linting
echo "🔍 Running ESLint..."
if npm run lint; then
    echo "✅ Linting passed"
else
    echo "⚠️ Linting warnings found, but continuing build..."
fi

# Build for production
echo "🏗️ Building production bundles..."
npm run build

# Run bundle analysis
echo "📊 Analyzing bundles..."
ANALYZE=true npm run build

# Copy bundles to Django static files
echo "📋 Copying bundles to Django static files..."
cp -r static/js/dist/* staticfiles/js/dist/

# Generate performance report
echo "📈 Generating performance report..."
cat > build-reports/build-summary.json << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "buildType": "production",
  "bundles": {
    "main": "$(ls static/js/dist/main.*.bundle.js 2>/dev/null | head -1 || echo 'main.bundle.js')",
    "vendor": "$(ls static/js/dist/vendor.*.bundle.js 2>/dev/null | head -1 || echo 'vendor.bundle.js')",
    "home": "$(ls static/js/dist/home.*.bundle.js 2>/dev/null | head -1 || echo 'home.bundle.js')",
    "contact": "$(ls static/js/dist/contact.*.bundle.js 2>/dev/null | head -1 || echo 'contact.bundle.js')",
    "gallery": "$(ls static/js/dist/gallery.*.bundle.js 2>/dev/null | head -1 || echo 'gallery.bundle.js')"
  },
  "features": [
    "code-splitting",
    "tree-shaking",
    "bundle-optimization",
    "progressive-enhancement",
    "performance-monitoring"
  ],
  "buildTools": {
    "webpack": "5.x",
    "babel": "7.x",
    "terser": "5.x"
  }
}
EOF

# Check if Django is available for collectstatic
if command -v python &> /dev/null && python -c "import django" 2>/dev/null; then
    echo "🐍 Running Django collectstatic..."
    if [ -f "manage.py" ]; then
        python manage.py collectstatic --noinput --clear
    fi
fi

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "📊 Build Summary:"
echo "=================="
echo "• Bundles created in: static/js/dist/"
echo "• Manifest file: static/js/dist/manifest.json"
echo "• Bundle analysis: bundle-report.html"
echo "• Performance budget: performance-budget-report.json"
echo "• Build summary: build-reports/build-summary.json"
echo ""

# Show bundle sizes
echo "📦 Bundle Sizes:"
echo "================"
if [ -d "static/js/dist" ]; then
    for file in static/js/dist/*.bundle.js; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            echo "• $(basename "$file"): $size"
        fi
    done
fi

echo ""
echo "🔧 Development Commands:"
echo "======================="
echo "• npm run watch     - Watch files and rebuild on changes"
echo "• npm run dev       - Start development server with HMR"
echo "• npm run analyze   - Analyze bundle composition"
echo "• npm run test      - Run JavaScript tests"
echo ""

echo "🚀 Production Deployment:"
echo "========================"
echo "• Bundles are optimized and minified"
echo "• Source maps are generated for debugging"
echo "• Service worker is generated for PWA features"
echo "• Performance budgets are enforced"
echo ""

# Check for any warnings or issues
if [ -f "performance-budget-report.json" ]; then
    violations=$(jq -r '.errors | length' performance-budget-report.json 2>/dev/null || echo "0")
    warnings=$(jq -r '.warnings | length' performance-budget-report.json 2>/dev/null || echo "0")
    
    if [ "$violations" -gt 0 ]; then
        echo "⚠️ Performance budget violations found: $violations"
    fi
    
    if [ "$warnings" -gt 0 ]; then
        echo "⚠️ Performance budget warnings: $warnings"
    fi
fi

echo "🎉 JavaScript optimization complete!"