#!/bin/bash

# Installation Script for JavaScript Bundling and Optimization
# SPEC_06 Group A Task 3 - Sabor Con Flow Dance

echo "🎯 Installing JavaScript Bundling and Optimization..."
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js (v14 or higher) and try again."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 14 ]; then
    echo "❌ Node.js version 14 or higher is required."
    echo "Current version: $(node --version)"
    echo "Please upgrade Node.js and try again."
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Install npm dependencies
echo "📦 Installing npm dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install npm dependencies"
    exit 1
fi

# Create necessary directories
echo "📁 Creating build directories..."
mkdir -p static/js/dist
mkdir -p staticfiles/js/dist
mkdir -p build-reports

# Make build script executable
chmod +x build.sh

# Run initial build
echo "🔧 Running initial build..."
./build.sh

if [ $? -ne 0 ]; then
    echo "❌ Initial build failed"
    exit 1
fi

# Update Django settings if needed
echo "⚙️ Checking Django configuration..."

# Check if STATICFILES_DIRS includes the new dist directory
if ! grep -q "static/js/dist" sabor_con_flow/settings.py; then
    echo "ℹ️ Note: You may need to update STATICFILES_DIRS in Django settings"
    echo "   to include the dist directory for development."
fi

# Create development script
cat > dev-server.sh << 'EOF'
#!/bin/bash
# Development server with webpack watch

echo "Starting development environment..."
echo "- Django server: http://localhost:8000"
echo "- Webpack dev server: http://localhost:9000"
echo ""

# Start webpack in watch mode
npm run watch &
WEBPACK_PID=$!

# Start Django development server
python manage.py runserver &
DJANGO_PID=$!

echo "Development servers started!"
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $WEBPACK_PID $DJANGO_PID; exit" INT
wait
EOF

chmod +x dev-server.sh

echo ""
echo "✅ JavaScript optimization installation complete!"
echo ""
echo "📋 What was installed:"
echo "===================="
echo "• Webpack bundling configuration"
echo "• Progressive enhancement utilities"
echo "• Performance monitoring tools"
echo "• Django template integration"
echo "• Build automation scripts"
echo "• Test environment setup"
echo ""
echo "🚀 Getting Started:"
echo "=================="
echo "• Run builds: ./build.sh"
echo "• Development: ./dev-server.sh"
echo "• Watch mode: npm run watch"
echo "• Production: npm run build"
echo "• Testing: npm run test"
echo "• Analysis: npm run analyze"
echo ""
echo "📊 Bundle Information:"
echo "===================="
echo "• Bundles created in: static/js/dist/"
echo "• Manifest file: static/js/dist/manifest.json"
echo "• Performance reports: build-reports/"
echo ""
echo "📚 Key Features:"
echo "==============="
echo "• ✅ Code splitting by route and feature"
echo "• ✅ Tree shaking for unused code removal"
echo "• ✅ Progressive enhancement (works without JS)"
echo "• ✅ Performance budget enforcement"
echo "• ✅ Modern ES6+ with Babel transpilation"
echo "• ✅ Django template integration"
echo "• ✅ Comprehensive testing setup"
echo ""
echo "📖 Documentation:"
echo "================="
echo "• Implementation details: JAVASCRIPT_OPTIMIZATION_SUMMARY.md"
echo "• Webpack config: webpack.config.js"
echo "• Build scripts: build-scripts/"
echo ""

# Show current bundle sizes if they exist
if [ -d "static/js/dist" ] && [ "$(ls -A static/js/dist/*.js 2>/dev/null)" ]; then
    echo "📦 Current Bundle Sizes:"
    echo "======================="
    for file in static/js/dist/*.bundle.js; do
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            echo "• $(basename "$file"): $size"
        fi
    done
    echo ""
fi

echo "🎉 Ready to optimize your JavaScript performance!"
echo ""
echo "💡 Next Steps:"
echo "============="
echo "1. Update templates to use: {% include 'components/js_bundles.html' %}"
echo "2. Add bundle requirements to elements: data-requires-bundle='feature'"
echo "3. Run performance audits: npm run performance"
echo "4. Monitor bundle sizes: npm run analyze"
echo ""
echo "🆘 Need Help?"
echo "============"
echo "• Check JAVASCRIPT_OPTIMIZATION_SUMMARY.md for detailed documentation"
echo "• Run npm run test to verify everything is working"
echo "• Use ./dev-server.sh for development with hot reloading"