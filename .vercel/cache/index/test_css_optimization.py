#!/usr/bin/env python3
"""
CSS Optimization Test Suite
SPEC_06 Group A Task 2

Tests for validating critical CSS extraction and optimization implementation.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Mock Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabor_con_flow.settings')


class TestCriticalCSSExtraction(unittest.TestCase):
    """Test critical CSS extraction functionality"""
    
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.static_dir = self.test_dir / 'static'
        self.css_dir = self.static_dir / 'css'
    
    def test_critical_css_exists(self):
        """Test that critical.css file exists"""
        critical_css_path = self.css_dir / 'critical.css'
        self.assertTrue(critical_css_path.exists(), "Critical CSS file should exist")
    
    def test_critical_css_size(self):
        """Test that critical CSS is within performance budget"""
        critical_css_path = self.css_dir / 'critical.css'
        if critical_css_path.exists():
            size = critical_css_path.stat().st_size
            budget = 14000  # 14KB budget
            self.assertLessEqual(size, budget, 
                f"Critical CSS ({size} bytes) exceeds budget ({budget} bytes)")
    
    def test_critical_css_content(self):
        """Test that critical CSS contains required selectors"""
        critical_css_path = self.css_dir / 'critical.css'
        if critical_css_path.exists():
            with open(critical_css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_selectors = [
                ':root',           # CSS variables
                'body',            # Base element
                '.navbar',         # Navigation
                '.hero-section',   # Hero section
                '.container',      # Layout
                '@media'           # Responsive design
            ]
            
            for selector in required_selectors:
                self.assertIn(selector, content, 
                    f"Critical CSS should contain {selector}")
    
    def test_css_file_structure(self):
        """Test that CSS files are properly organized"""
        expected_files = [
            'critical.css',
            'navigation.css',
            'hero.css',
            'styles.css'
        ]
        
        for filename in expected_files:
            file_path = self.css_dir / filename
            self.assertTrue(file_path.exists(), 
                f"Expected CSS file {filename} should exist")


class TestCSSLoader(unittest.TestCase):
    """Test CSS async loader functionality"""
    
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.js_dir = self.test_dir / 'static' / 'js'
    
    def test_css_async_loader_exists(self):
        """Test that CSS async loader exists"""
        loader_path = self.js_dir / 'css-async-loader.js'
        self.assertTrue(loader_path.exists(), "CSS async loader should exist")
    
    def test_performance_monitor_exists(self):
        """Test that performance monitor exists"""
        monitor_path = self.js_dir / 'css-performance-monitor.js'
        self.assertTrue(monitor_path.exists(), "Performance monitor should exist")
    
    def test_loader_functionality(self):
        """Test that loader contains required functionality"""
        loader_path = self.js_dir / 'css-async-loader.js'
        if loader_path.exists():
            with open(loader_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_functions = [
                'loadCSS',
                'loadWithPriority',
                'performance.now',
                'CustomEvent'
            ]
            
            for func in required_functions:
                self.assertIn(func, content, 
                    f"CSS loader should contain {func}")


class TestTemplateIntegration(unittest.TestCase):
    """Test Django template integration"""
    
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.template_dir = self.test_dir / 'templates'
        self.templatetags_dir = self.test_dir / 'core' / 'templatetags'
    
    def test_template_tags_exist(self):
        """Test that template tags file exists"""
        tags_path = self.templatetags_dir / 'critical_css_tags.py'
        self.assertTrue(tags_path.exists(), "Template tags should exist")
    
    def test_base_template_updated(self):
        """Test that base template has been updated"""
        base_template = self.template_dir / 'base.html'
        if base_template.exists():
            with open(base_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_elements = [
                'critical_css_tags',
                'get_critical_css',
                'get_async_css_loader',
                'get_performance_script'
            ]
            
            for element in required_elements:
                self.assertIn(element, content, 
                    f"Base template should contain {element}")


class TestBuildSystem(unittest.TestCase):
    """Test CSS build system"""
    
    def setUp(self):
        self.test_dir = Path(__file__).parent
    
    def test_build_script_exists(self):
        """Test that build script exists"""
        build_script = self.test_dir / 'build_css.py'
        self.assertTrue(build_script.exists(), "Build script should exist")
    
    def test_deployment_script_exists(self):
        """Test that deployment script exists"""
        deploy_script = self.test_dir / 'deploy_css_optimization.py'
        self.assertTrue(deploy_script.exists(), "Deployment script should exist")
    
    def test_utils_module_exists(self):
        """Test that utilities module exists"""
        utils_module = self.test_dir / 'core' / 'utils' / 'critical_css.py'
        self.assertTrue(utils_module.exists(), "Utilities module should exist")


class TestPerformanceBudgets(unittest.TestCase):
    """Test performance budget validation"""
    
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.css_dir = self.test_dir / 'static' / 'css'
        
        # Performance budgets (bytes)
        self.critical_budget = 14000  # 14KB
        self.total_budget = 50000     # 50KB
    
    def test_critical_css_budget(self):
        """Test critical CSS size against budget"""
        critical_css_path = self.css_dir / 'critical.css'
        if critical_css_path.exists():
            size = critical_css_path.stat().st_size
            self.assertLessEqual(size, self.critical_budget,
                f"Critical CSS ({size}B) exceeds budget ({self.critical_budget}B)")
    
    def test_total_css_budget(self):
        """Test total CSS size against budget"""
        if self.css_dir.exists():
            total_size = sum(f.stat().st_size for f in self.css_dir.glob('*.css'))
            self.assertLessEqual(total_size, self.total_budget,
                f"Total CSS ({total_size}B) exceeds budget ({self.total_budget}B)")
    
    def test_individual_file_sizes(self):
        """Test individual CSS files aren't too large"""
        max_file_size = 10000  # 10KB max for individual files
        
        if self.css_dir.exists():
            for css_file in self.css_dir.glob('*.css'):
                if css_file.name == 'critical.css':
                    continue  # Critical CSS has its own budget
                
                size = css_file.stat().st_size
                self.assertLessEqual(size, max_file_size,
                    f"{css_file.name} ({size}B) exceeds individual file limit ({max_file_size}B)")


class TestCSSContent(unittest.TestCase):
    """Test CSS content quality"""
    
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.css_dir = self.test_dir / 'static' / 'css'
    
    def test_css_syntax_validity(self):
        """Test that CSS files have valid syntax"""
        if not self.css_dir.exists():
            self.skipTest("CSS directory not found")
        
        for css_file in self.css_dir.glob('*.css'):
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            open_braces = content.count('{')
            close_braces = content.count('}')
            self.assertEqual(open_braces, close_braces,
                f"{css_file.name} has mismatched braces")
    
    def test_css_variables_defined(self):
        """Test that CSS variables are properly defined"""
        critical_css_path = self.css_dir / 'critical.css'
        if critical_css_path.exists():
            with open(critical_css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_variables = [
                '--color-gold',
                '--color-black', 
                '--color-white',
                '--font-heading',
                '--font-body'
            ]
            
            for var in required_variables:
                self.assertIn(var, content,
                    f"Critical CSS should define {var}")
    
    def test_responsive_design_included(self):
        """Test that responsive design rules are included"""
        critical_css_path = self.css_dir / 'critical.css'
        if critical_css_path.exists():
            with open(critical_css_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should contain media queries
            self.assertIn('@media', content,
                "Critical CSS should contain responsive rules")
            
            # Should contain mobile-first breakpoints
            self.assertIn('min-width', content,
                "Critical CSS should use mobile-first approach")


def run_performance_tests():
    """Run performance-specific tests"""
    print("🧪 Running CSS optimization tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCriticalCSSExtraction,
        TestCSSLoader,
        TestTemplateIntegration,
        TestBuildSystem,
        TestPerformanceBudgets,
        TestCSSContent
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError: ')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split('Exception: ')[-1].strip()}")
    
    if result.wasSuccessful():
        print(f"\n✅ All tests passed!")
        return True
    else:
        print(f"\n❌ Some tests failed!")
        return False


def main():
    """Main test entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CSS Optimization Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--specific', '-s', type=str, help='Run specific test class')
    
    args = parser.parse_args()
    
    if args.specific:
        # Run specific test class
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f'__main__.{args.specific}')
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)
    else:
        # Run all tests
        success = run_performance_tests()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()