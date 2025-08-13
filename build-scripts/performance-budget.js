/**
 * Performance Budget Enforcement
 * Webpack plugin to enforce bundle size limits and performance budgets
 */

const chalk = require('chalk');
const gzipSize = require('gzip-size');
const fs = require('fs');

class PerformanceBudgetPlugin {
  constructor(options = {}) {
    this.options = {
      // Bundle size limits (in bytes)
      budgets: {
        main: 250000, // 250KB for main bundle
        vendor: 300000, // 300KB for vendor bundle
        critical: 150000, // 150KB for critical path bundles
        page: 100000, // 100KB for page-specific bundles
        feature: 75000, // 75KB for feature bundles
      },

      // Gzip size limits (typically 3-4x smaller)
      gzipBudgets: {
        main: 80000, // 80KB gzipped
        vendor: 100000, // 100KB gzipped
        critical: 50000, // 50KB gzipped
        page: 30000, // 30KB gzipped
        feature: 25000, // 25KB gzipped
      },

      // Failure thresholds
      warnThreshold: 0.9, // Warn at 90% of budget
      errorThreshold: 1.0, // Error at 100% of budget

      // Output options
      showSizes: true,
      showGzipSizes: true,
      showBudgetStatus: true,
      generateReport: true,
      reportPath: './performance-budget-report.json',

      ...options,
    };

    this.warnings = [];
    this.errors = [];
  }

  apply(compiler) {
    compiler.hooks.afterEmit.tapAsync('PerformanceBudgetPlugin', (compilation, callback) => {
      this.checkBudgets(compilation)
        .then(() => {
          this.displayResults();
          this.generateReport();
          callback();
        })
        .catch(callback);
    });
  }

  async checkBudgets(compilation) {
    const { assets } = compilation.getStats().toJson({ assets: true });
    const results = [];

    for (const asset of assets) {
      if (asset.name.endsWith('.js')) {
        const result = await this.analyzeAsset(asset, compilation);
        results.push(result);
        this.checkBudget(result);
      }
    }

    this.results = results;
    return results;
  }

  async analyzeAsset(asset, compilation) {
    const assetPath = `${compilation.outputOptions.path}/${asset.name}`;
    const content = fs.readFileSync(assetPath);
    const gzipped = await gzipSize(content);

    const bundleType = this.getBundleType(asset.name);
    const budget = this.options.budgets[bundleType] || this.options.budgets.feature;
    const gzipBudget = this.options.gzipBudgets[bundleType] || this.options.gzipBudgets.feature;

    return {
      name: asset.name,
      type: bundleType,
      size: asset.size,
      gzipSize: gzipped,
      budget,
      gzipBudget,
      budgetUsage: asset.size / budget,
      gzipBudgetUsage: gzipped / gzipBudget,
      isOverBudget: asset.size > budget,
      isOverGzipBudget: gzipped > gzipBudget,
    };
  }

  getBundleType(fileName) {
    if (fileName.includes('vendor')) return 'vendor';
    if (fileName.includes('main')) return 'main';
    if (fileName.includes('critical')) return 'critical';
    if (fileName.includes('home') || fileName.includes('contact') || fileName.includes('pricing')) {
      return 'page';
    }
    return 'feature';
  }

  checkBudget(result) {
    const { name, size, gzipSize, budget, gzipBudget, budgetUsage, gzipBudgetUsage } = result;

    // Check raw size budget
    if (budgetUsage >= this.options.errorThreshold) {
      this.errors.push({
        type: 'budget_exceeded',
        bundle: name,
        size,
        budget,
        usage: budgetUsage,
        message: `Bundle ${name} exceeds size budget: ${this.formatSize(size)} / ${this.formatSize(budget)}`,
      });
    } else if (budgetUsage >= this.options.warnThreshold) {
      this.warnings.push({
        type: 'budget_warning',
        bundle: name,
        size,
        budget,
        usage: budgetUsage,
        message: `Bundle ${name} approaching size budget: ${this.formatSize(size)} / ${this.formatSize(budget)}`,
      });
    }

    // Check gzip size budget
    if (gzipBudgetUsage >= this.options.errorThreshold) {
      this.errors.push({
        type: 'gzip_budget_exceeded',
        bundle: name,
        size: gzipSize,
        budget: gzipBudget,
        usage: gzipBudgetUsage,
        message: `Bundle ${name} exceeds gzip budget: ${this.formatSize(gzipSize)} / ${this.formatSize(gzipBudget)}`,
      });
    } else if (gzipBudgetUsage >= this.options.warnThreshold) {
      this.warnings.push({
        type: 'gzip_budget_warning',
        bundle: name,
        size: gzipSize,
        budget: gzipBudget,
        usage: gzipBudgetUsage,
        message: `Bundle ${name} approaching gzip budget: ${this.formatSize(gzipSize)} / ${this.formatSize(gzipBudget)}`,
      });
    }
  }

  displayResults() {
    if (!this.options.showBudgetStatus) return;

    console.log(`\n${chalk.bold('Performance Budget Report')}`);
    console.log('═'.repeat(60));

    if (this.options.showSizes) {
      this.displaySizeTable();
    }

    if (this.warnings.length > 0) {
      console.log(`\n${chalk.yellow.bold('⚠️  WARNINGS:')}`);
      this.warnings.forEach(warning => {
        console.log(chalk.yellow(`  • ${warning.message}`));
      });
    }

    if (this.errors.length > 0) {
      console.log(`\n${chalk.red.bold('❌ ERRORS:')}`);
      this.errors.forEach(error => {
        console.log(chalk.red(`  • ${error.message}`));
      });
    }

    if (this.warnings.length === 0 && this.errors.length === 0) {
      console.log(`\n${chalk.green.bold('✅ All bundles within performance budget!')}`);
    }

    console.log('');
  }

  displaySizeTable() {
    console.log(`\n${chalk.bold('Bundle Sizes:')}`);
    console.log('─'.repeat(80));

    const header = `${
      'Bundle'.padEnd(25) +
      'Raw Size'.padEnd(12) +
      'Gzip Size'.padEnd(12) +
      'Budget'.padEnd(12) +
      'Usage'.padEnd(10)
    }Status`;
    console.log(chalk.gray(header));
    console.log('─'.repeat(80));

    this.results.forEach(result => {
      const name = result.name.padEnd(25);
      const rawSize = this.formatSize(result.size).padEnd(12);
      const gzipSize = this.formatSize(result.gzipSize).padEnd(12);
      const budget = this.formatSize(result.budget).padEnd(12);
      const usage = `${(result.budgetUsage * 100).toFixed(1)}%`.padEnd(10);

      let status = '✅ OK';
      let color = chalk.green;

      if (result.budgetUsage >= this.options.errorThreshold || result.isOverBudget) {
        status = '❌ OVER';
        color = chalk.red;
      } else if (result.budgetUsage >= this.options.warnThreshold) {
        status = '⚠️ WARN';
        color = chalk.yellow;
      }

      console.log(color(`${name}${rawSize}${gzipSize}${budget}${usage}${status}`));
    });
  }

  generateReport() {
    if (!this.options.generateReport) return;

    const report = {
      timestamp: new Date().toISOString(),
      budgets: this.options.budgets,
      gzipBudgets: this.options.gzipBudgets,
      results: this.results,
      warnings: this.warnings,
      errors: this.errors,
      summary: {
        totalBundles: this.results.length,
        totalSize: this.results.reduce((sum, r) => sum + r.size, 0),
        totalGzipSize: this.results.reduce((sum, r) => sum + r.gzipSize, 0),
        budgetViolations: this.errors.length,
        budgetWarnings: this.warnings.length,
        overallStatus:
          this.errors.length > 0 ? 'FAILED' : this.warnings.length > 0 ? 'WARNING' : 'PASSED',
      },
    };

    fs.writeFileSync(this.options.reportPath, JSON.stringify(report, null, 2));
    console.log(chalk.blue(`📊 Performance budget report saved to: ${this.options.reportPath}`));
  }

  formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  // Static method to get recommended budgets
  static getRecommendedBudgets() {
    return {
      // Conservative budgets for good performance
      conservative: {
        main: 200000, // 200KB
        vendor: 250000, // 250KB
        critical: 100000, // 100KB
        page: 75000, // 75KB
        feature: 50000, // 50KB
      },

      // Moderate budgets for balanced performance
      moderate: {
        main: 300000, // 300KB
        vendor: 400000, // 400KB
        critical: 150000, // 150KB
        page: 100000, // 100KB
        feature: 75000, // 75KB
      },

      // Aggressive budgets for feature-rich apps
      aggressive: {
        main: 400000, // 400KB
        vendor: 500000, // 500KB
        critical: 200000, // 200KB
        page: 150000, // 150KB
        feature: 100000, // 100KB
      },
    };
  }
}

module.exports = PerformanceBudgetPlugin;
