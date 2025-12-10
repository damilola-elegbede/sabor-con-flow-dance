/**
 * Performance Measurement Dashboard
 * SPEC_04 Group D Implementation - Real-time performance monitoring UI
 */

class PerformanceDashboard {
    constructor(options = {}) {
        this.options = {
            autoShow: false,
            position: 'bottom-right',
            updateInterval: 5000,
            enableKeyboardShortcut: true,
            keyboardShortcut: 'Ctrl+Shift+P',
            enableDebugMode: false,
            ...options
        };

        this.metrics = {};
        this.isVisible = false;
        this.updateTimer = null;
        this.dashboard = null;

        this.init();
    }

    init() {
        // Only initialize in development or when explicitly enabled
        if (!this.shouldInitialize()) return;

        this.createDashboard();
        this.setupEventListeners();
        
        if (this.options.autoShow) {
            this.show();
        }

        if (this.options.enableKeyboardShortcut) {
            this.setupKeyboardShortcut();
        }

        console.log('📊 Performance Dashboard initialized');
    }

    shouldInitialize() {
        // Show in development mode or when debug parameter is present
        return window.location.hostname.includes('localhost') ||
               window.location.hostname.includes('127.0.0.1') ||
               window.location.search.includes('debug=true') ||
               localStorage.getItem('performance-dashboard-enabled') === 'true' ||
               this.options.enableDebugMode;
    }

    createDashboard() {
        this.dashboard = document.createElement('div');
        this.dashboard.id = 'performance-dashboard';
        this.dashboard.innerHTML = this.getDashboardHTML();
        
        // Apply styles
        this.applyStyles();
        
        document.body.appendChild(this.dashboard);
        
        // Setup event handlers
        this.setupDashboardEvents();
    }

    getDashboardHTML() {
        return `
            <div class="perf-dashboard-header">
                <h3>Performance Monitor</h3>
                <div class="perf-dashboard-controls">
                    <button id="perf-refresh" title="Refresh Metrics">🔄</button>
                    <button id="perf-export" title="Export Data">📊</button>
                    <button id="perf-toggle" title="Toggle Detailed View">📋</button>
                    <button id="perf-close" title="Close Dashboard">✕</button>
                </div>
            </div>
            
            <div class="perf-dashboard-content">
                <!-- Core Web Vitals -->
                <div class="perf-section">
                    <h4>Core Web Vitals</h4>
                    <div class="perf-metrics-grid">
                        <div class="perf-metric" id="lcp-metric">
                            <span class="perf-label">LCP</span>
                            <span class="perf-value" id="lcp-value">-</span>
                            <span class="perf-status" id="lcp-status">🔄</span>
                        </div>
                        <div class="perf-metric" id="fid-metric">
                            <span class="perf-label">FID</span>
                            <span class="perf-value" id="fid-value">-</span>
                            <span class="perf-status" id="fid-status">🔄</span>
                        </div>
                        <div class="perf-metric" id="cls-metric">
                            <span class="perf-label">CLS</span>
                            <span class="perf-value" id="cls-value">-</span>
                            <span class="perf-status" id="cls-status">🔄</span>
                        </div>
                        <div class="perf-metric" id="ttfb-metric">
                            <span class="perf-label">TTFB</span>
                            <span class="perf-value" id="ttfb-value">-</span>
                            <span class="perf-status" id="ttfb-status">🔄</span>
                        </div>
                    </div>
                </div>

                <!-- Load Performance -->
                <div class="perf-section">
                    <h4>Load Performance</h4>
                    <div class="perf-info-grid">
                        <div class="perf-info">
                            <span class="perf-info-label">Page Load Time:</span>
                            <span class="perf-info-value" id="page-load-time">-</span>
                        </div>
                        <div class="perf-info">
                            <span class="perf-info-label">DOM Ready:</span>
                            <span class="perf-info-value" id="dom-ready-time">-</span>
                        </div>
                        <div class="perf-info">
                            <span class="perf-info-label">Resources Loaded:</span>
                            <span class="perf-info-value" id="resources-count">-</span>
                        </div>
                        <div class="perf-info">
                            <span class="perf-info-label">Total Size:</span>
                            <span class="perf-info-value" id="total-size">-</span>
                        </div>
                    </div>
                </div>

                <!-- Optimizations Status -->
                <div class="perf-section">
                    <h4>Optimizations</h4>
                    <div class="perf-optimizations">
                        <div class="perf-opt-item" id="lazy-loading-status">
                            <span class="perf-opt-label">Lazy Loading:</span>
                            <span class="perf-opt-status">🔄</span>
                            <span class="perf-opt-value">-</span>
                        </div>
                        <div class="perf-opt-item" id="caching-status">
                            <span class="perf-opt-label">Caching:</span>
                            <span class="perf-opt-status">🔄</span>
                            <span class="perf-opt-value">-</span>
                        </div>
                        <div class="perf-opt-item" id="compression-status">
                            <span class="perf-opt-label">Compression:</span>
                            <span class="perf-opt-status">🔄</span>
                            <span class="perf-opt-value">-</span>
                        </div>
                        <div class="perf-opt-item" id="preloading-status">
                            <span class="perf-opt-label">Preloading:</span>
                            <span class="perf-opt-status">🔄</span>
                            <span class="perf-opt-value">-</span>
                        </div>
                    </div>
                </div>

                <!-- Network & Device Info -->
                <div class="perf-section" id="technical-details" style="display: none;">
                    <h4>Technical Details</h4>
                    <div class="perf-technical">
                        <div class="perf-tech-item">
                            <span class="perf-tech-label">Connection:</span>
                            <span class="perf-tech-value" id="connection-type">-</span>
                        </div>
                        <div class="perf-tech-item">
                            <span class="perf-tech-label">Device Memory:</span>
                            <span class="perf-tech-value" id="device-memory">-</span>
                        </div>
                        <div class="perf-tech-item">
                            <span class="perf-tech-label">CPU Cores:</span>
                            <span class="perf-tech-value" id="cpu-cores">-</span>
                        </div>
                        <div class="perf-tech-item">
                            <span class="perf-tech-label">Viewport:</span>
                            <span class="perf-tech-value" id="viewport-size">-</span>
                        </div>
                    </div>
                </div>

                <!-- Performance Score -->
                <div class="perf-section">
                    <h4>Performance Score</h4>
                    <div class="perf-score-container">
                        <div class="perf-score-circle" id="perf-score-circle">
                            <span class="perf-score-value" id="perf-score-value">-</span>
                        </div>
                        <div class="perf-score-details">
                            <div class="perf-score-breakdown" id="perf-score-breakdown"></div>
                        </div>
                    </div>
                </div>

                <!-- Recommendations -->
                <div class="perf-section" id="recommendations-section" style="display: none;">
                    <h4>Recommendations</h4>
                    <div class="perf-recommendations" id="perf-recommendations">
                        <p>Analyzing performance...</p>
                    </div>
                </div>
            </div>
        `;
    }

    applyStyles() {
        const styles = `
            #performance-dashboard {
                position: fixed;
                ${this.options.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
                ${this.options.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
                width: 320px;
                max-height: 80vh;
                background: rgba(0, 0, 0, 0.95);
                color: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                font-family: 'Courier New', monospace;
                font-size: 12px;
                z-index: 10000;
                overflow: hidden;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(199, 179, 117, 0.3);
                display: none;
            }

            .perf-dashboard-header {
                background: linear-gradient(135deg, #C7B375, #9C8E5A);
                padding: 12px 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: move;
            }

            .perf-dashboard-header h3 {
                margin: 0;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }

            .perf-dashboard-controls {
                display: flex;
                gap: 8px;
            }

            .perf-dashboard-controls button {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: background 0.2s;
            }

            .perf-dashboard-controls button:hover {
                background: rgba(255, 255, 255, 0.3);
            }

            .perf-dashboard-content {
                padding: 16px;
                max-height: calc(80vh - 60px);
                overflow-y: auto;
            }

            .perf-section {
                margin-bottom: 20px;
            }

            .perf-section h4 {
                margin: 0 0 12px 0;
                font-size: 13px;
                color: #C7B375;
                border-bottom: 1px solid rgba(199, 179, 117, 0.3);
                padding-bottom: 4px;
            }

            .perf-metrics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }

            .perf-metric {
                background: rgba(255, 255, 255, 0.05);
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .perf-label {
                display: block;
                font-size: 11px;
                color: #ccc;
                margin-bottom: 4px;
            }

            .perf-value {
                display: block;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 4px;
            }

            .perf-status {
                font-size: 14px;
            }

            .perf-info-grid {
                display: grid;
                gap: 8px;
            }

            .perf-info {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .perf-info-label {
                color: #ccc;
                font-size: 11px;
            }

            .perf-info-value {
                font-weight: bold;
                font-size: 11px;
            }

            .perf-optimizations, .perf-technical {
                display: grid;
                gap: 8px;
            }

            .perf-opt-item, .perf-tech-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }

            .perf-opt-label, .perf-tech-label {
                color: #ccc;
                font-size: 11px;
                flex: 1;
            }

            .perf-opt-status {
                margin: 0 8px;
            }

            .perf-opt-value, .perf-tech-value {
                font-size: 11px;
                font-weight: bold;
                text-align: right;
            }

            .perf-score-container {
                display: flex;
                align-items: center;
                gap: 16px;
            }

            .perf-score-circle {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: conic-gradient(#4CAF50 0deg, #4CAF50 0deg, #333 0deg, #333 360deg);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            }

            .perf-score-circle::before {
                content: '';
                position: absolute;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: rgba(0, 0, 0, 0.95);
            }

            .perf-score-value {
                position: relative;
                z-index: 1;
                font-weight: bold;
                font-size: 14px;
            }

            .perf-score-details {
                flex: 1;
            }

            .perf-score-breakdown {
                font-size: 10px;
                line-height: 1.4;
                color: #ccc;
            }

            .perf-recommendations {
                font-size: 11px;
                line-height: 1.4;
            }

            .perf-recommendations ul {
                margin: 0;
                padding-left: 16px;
            }

            .perf-recommendations li {
                margin-bottom: 4px;
                color: #ccc;
            }

            /* Status colors */
            .status-good { color: #4CAF50; }
            .status-needs-improvement { color: #FF9800; }
            .status-poor { color: #F44336; }

            /* Scrollbar styling */
            .perf-dashboard-content::-webkit-scrollbar {
                width: 4px;
            }

            .perf-dashboard-content::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
            }

            .perf-dashboard-content::-webkit-scrollbar-thumb {
                background: #C7B375;
                border-radius: 2px;
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    setupDashboardEvents() {
        // Close button
        const closeBtn = this.dashboard.querySelector('#perf-close');
        closeBtn.addEventListener('click', () => this.hide());

        // Refresh button
        const refreshBtn = this.dashboard.querySelector('#perf-refresh');
        refreshBtn.addEventListener('click', () => this.updateMetrics());

        // Export button
        const exportBtn = this.dashboard.querySelector('#perf-export');
        exportBtn.addEventListener('click', () => this.exportData());

        // Toggle detailed view
        const toggleBtn = this.dashboard.querySelector('#perf-toggle');
        toggleBtn.addEventListener('click', () => this.toggleDetailedView());

        // Make dashboard draggable
        this.makeDraggable();
    }

    setupEventListeners() {
        // Listen for performance updates from other components
        window.addEventListener('performanceMetricsUpdated', (event) => {
            this.metrics = { ...this.metrics, ...event.detail };
            if (this.isVisible) {
                this.updateDisplay();
            }
        });

        // Listen for Core Web Vitals updates
        window.addEventListener('core-web-vitals-updated', (event) => {
            this.metrics.coreWebVitals = event.detail;
            if (this.isVisible) {
                this.updateCoreWebVitals();
            }
        });
    }

    setupKeyboardShortcut() {
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.shiftKey && event.key === 'P') {
                event.preventDefault();
                this.toggle();
            }
        });
    }

    makeDraggable() {
        const header = this.dashboard.querySelector('.perf-dashboard-header');
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = this.dashboard.offsetLeft;
            startTop = this.dashboard.offsetTop;
            
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        const onMouseMove = (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            this.dashboard.style.left = (startLeft + deltaX) + 'px';
            this.dashboard.style.top = (startTop + deltaY) + 'px';
            this.dashboard.style.right = 'auto';
            this.dashboard.style.bottom = 'auto';
        };

        const onMouseUp = () => {
            isDragging = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
    }

    show() {
        this.dashboard.style.display = 'block';
        this.isVisible = true;
        this.startUpdating();
        this.updateMetrics();
    }

    hide() {
        this.dashboard.style.display = 'none';
        this.isVisible = false;
        this.stopUpdating();
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    startUpdating() {
        this.updateTimer = setInterval(() => {
            this.updateMetrics();
        }, this.options.updateInterval);
    }

    stopUpdating() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    async updateMetrics() {
        try {
            // Collect metrics from various sources
            await this.collectNavigationMetrics();
            await this.collectResourceMetrics();
            await this.collectOptimizationMetrics();
            await this.collectTechnicalMetrics();
            
            this.updateDisplay();
            this.calculatePerformanceScore();
            this.generateRecommendations();
            
        } catch (error) {
            console.error('Failed to update performance metrics:', error);
        }
    }

    async collectNavigationMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            this.metrics.navigation = {
                pageLoadTime: navigation.loadEventEnd - navigation.navigationStart,
                domReadyTime: navigation.domContentLoadedEventEnd - navigation.navigationStart,
                ttfb: navigation.responseStart - navigation.requestStart
            };
        }
    }

    async collectResourceMetrics() {
        const resources = performance.getEntriesByType('resource');
        const totalSize = resources.reduce((sum, resource) => {
            return sum + (resource.transferSize || resource.encodedBodySize || 0);
        }, 0);

        this.metrics.resources = {
            count: resources.length,
            totalSize: totalSize,
            slowResources: resources.filter(r => r.duration > 2000).length
        };
    }

    async collectOptimizationMetrics() {
        this.metrics.optimizations = {
            lazyLoading: window.lazyLoader ? window.lazyLoader.getMetrics() : null,
            caching: this.checkCachingStatus(),
            compression: this.checkCompressionStatus(),
            preloading: window.resourceOptimizer ? window.resourceOptimizer.getOptimizationStatus() : null
        };
    }

    async collectTechnicalMetrics() {
        this.metrics.technical = {
            connection: navigator.connection?.effectiveType || 'unknown',
            memory: navigator.deviceMemory || 'unknown',
            cores: navigator.hardwareConcurrency || 'unknown',
            viewport: `${window.innerWidth}x${window.innerHeight}`
        };
    }

    checkCachingStatus() {
        // Check if resources are being cached
        const cachedResources = performance.getEntriesByType('resource')
            .filter(r => r.transferSize === 0).length;
        
        const totalResources = performance.getEntriesByType('resource').length;
        const cacheHitRate = totalResources > 0 ? (cachedResources / totalResources) * 100 : 0;
        
        return {
            enabled: cacheHitRate > 0,
            hitRate: cacheHitRate
        };
    }

    checkCompressionStatus() {
        // Check if resources are compressed by comparing transfer vs encoded size
        const resources = performance.getEntriesByType('resource');
        const compressedResources = resources.filter(r => 
            r.transferSize > 0 && r.encodedBodySize > 0 && 
            r.transferSize < r.encodedBodySize
        ).length;
        
        return {
            enabled: compressedResources > 0,
            percentage: resources.length > 0 ? (compressedResources / resources.length) * 100 : 0
        };
    }

    updateDisplay() {
        this.updateNavigationMetrics();
        this.updateResourceMetrics();
        this.updateOptimizationStatus();
        this.updateTechnicalDetails();
    }

    updateNavigationMetrics() {
        const nav = this.metrics.navigation;
        if (nav) {
            this.setElementText('page-load-time', this.formatDuration(nav.pageLoadTime));
            this.setElementText('dom-ready-time', this.formatDuration(nav.domReadyTime));
            this.setElementText('ttfb-value', this.formatDuration(nav.ttfb));
            this.setElementClass('ttfb-status', this.getRatingClass(this.rateTTFB(nav.ttfb)));
            this.setElementText('ttfb-status', this.getRatingEmoji(this.rateTTFB(nav.ttfb)));
        }
    }

    updateResourceMetrics() {
        const res = this.metrics.resources;
        if (res) {
            this.setElementText('resources-count', res.count.toString());
            this.setElementText('total-size', this.formatBytes(res.totalSize));
        }
    }

    updateOptimizationStatus() {
        const opt = this.metrics.optimizations;
        if (opt) {
            // Lazy loading
            if (opt.lazyLoading) {
                const ll = opt.lazyLoading;
                this.setElementText('lazy-loading-status .perf-opt-status', '✅');
                this.setElementText('lazy-loading-status .perf-opt-value', 
                    `${ll.loadedImages}/${ll.totalImages} images`);
            }

            // Caching
            if (opt.caching) {
                const cache = opt.caching;
                this.setElementText('caching-status .perf-opt-status', 
                    cache.enabled ? '✅' : '❌');
                this.setElementText('caching-status .perf-opt-value', 
                    `${cache.hitRate.toFixed(1)}% hit rate`);
            }

            // Compression
            if (opt.compression) {
                const comp = opt.compression;
                this.setElementText('compression-status .perf-opt-status', 
                    comp.enabled ? '✅' : '❌');
                this.setElementText('compression-status .perf-opt-value', 
                    `${comp.percentage.toFixed(1)}% compressed`);
            }

            // Preloading
            if (opt.preloading) {
                const preload = opt.preloading;
                this.setElementText('preloading-status .perf-opt-status', '✅');
                this.setElementText('preloading-status .perf-opt-value', 
                    `${preload.preloadedResources} resources`);
            }
        }
    }

    updateTechnicalDetails() {
        const tech = this.metrics.technical;
        if (tech) {
            this.setElementText('connection-type', tech.connection);
            this.setElementText('device-memory', tech.memory + ' GB');
            this.setElementText('cpu-cores', tech.cores.toString());
            this.setElementText('viewport-size', tech.viewport);
        }
    }

    updateCoreWebVitals() {
        const cwv = this.metrics.coreWebVitals;
        if (cwv) {
            if (cwv.lcp) {
                this.setElementText('lcp-value', this.formatDuration(cwv.lcp.value));
                this.setElementClass('lcp-status', this.getRatingClass(cwv.lcp.rating));
                this.setElementText('lcp-status', this.getRatingEmoji(cwv.lcp.rating));
            }

            if (cwv.fid) {
                this.setElementText('fid-value', this.formatDuration(cwv.fid.value));
                this.setElementClass('fid-status', this.getRatingClass(cwv.fid.rating));
                this.setElementText('fid-status', this.getRatingEmoji(cwv.fid.rating));
            }

            if (cwv.cls) {
                this.setElementText('cls-value', cwv.cls.value.toFixed(3));
                this.setElementClass('cls-status', this.getRatingClass(cwv.cls.rating));
                this.setElementText('cls-status', this.getRatingEmoji(cwv.cls.rating));
            }
        }
    }

    calculatePerformanceScore() {
        let score = 100;
        let factors = [];

        // Core Web Vitals impact (60% of score)
        const cwv = this.metrics.coreWebVitals;
        if (cwv) {
            if (cwv.lcp) {
                const lcpScore = this.scoreLCP(cwv.lcp.value);
                score -= (100 - lcpScore) * 0.25;
                factors.push(`LCP: ${lcpScore}%`);
            }

            if (cwv.fid) {
                const fidScore = this.scoreFID(cwv.fid.value);
                score -= (100 - fidScore) * 0.15;
                factors.push(`FID: ${fidScore}%`);
            }

            if (cwv.cls) {
                const clsScore = this.scoreCLS(cwv.cls.value);
                score -= (100 - clsScore) * 0.20;
                factors.push(`CLS: ${clsScore}%`);
            }
        }

        // Resource optimization impact (40% of score)
        const opt = this.metrics.optimizations;
        if (opt) {
            if (opt.caching && opt.caching.hitRate < 50) {
                score -= 10;
                factors.push('Low cache hit rate');
            }

            if (opt.compression && opt.compression.percentage < 70) {
                score -= 10;
                factors.push('Poor compression');
            }

            if (this.metrics.resources?.slowResources > 0) {
                score -= this.metrics.resources.slowResources * 5;
                factors.push(`${this.metrics.resources.slowResources} slow resources`);
            }
        }

        score = Math.max(0, Math.min(100, score));

        this.updatePerformanceScore(score, factors);
    }

    updatePerformanceScore(score, factors) {
        const scoreElement = this.dashboard.querySelector('#perf-score-value');
        const circleElement = this.dashboard.querySelector('#perf-score-circle');
        const breakdownElement = this.dashboard.querySelector('#perf-score-breakdown');

        scoreElement.textContent = Math.round(score);

        // Update circle color based on score
        let color;
        if (score >= 90) color = '#4CAF50'; // Green
        else if (score >= 70) color = '#FF9800'; // Orange
        else color = '#F44336'; // Red

        const percentage = score / 100 * 360;
        circleElement.style.background = `conic-gradient(${color} ${percentage}deg, #333 ${percentage}deg)`;

        // Update breakdown
        breakdownElement.innerHTML = factors.map(factor => `• ${factor}`).join('<br>');
    }

    generateRecommendations() {
        const recommendations = [];
        const cwv = this.metrics.coreWebVitals;
        const opt = this.metrics.optimizations;

        if (cwv?.lcp?.rating !== 'good') {
            recommendations.push('Optimize images and critical resources to improve LCP');
        }

        if (cwv?.fid?.rating !== 'good') {
            recommendations.push('Reduce JavaScript execution time to improve FID');
        }

        if (cwv?.cls?.rating !== 'good') {
            recommendations.push('Add size attributes to images to improve CLS');
        }

        if (opt?.caching?.hitRate < 50) {
            recommendations.push('Implement better caching strategies');
        }

        if (opt?.compression?.percentage < 70) {
            recommendations.push('Enable compression for more resources');
        }

        if (this.metrics.resources?.slowResources > 0) {
            recommendations.push('Optimize slow-loading resources');
        }

        this.updateRecommendations(recommendations);
    }

    updateRecommendations(recommendations) {
        const recSection = this.dashboard.querySelector('#recommendations-section');
        const recElement = this.dashboard.querySelector('#perf-recommendations');

        if (recommendations.length > 0) {
            recSection.style.display = 'block';
            recElement.innerHTML = `
                <ul>
                    ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            `;
        } else {
            recSection.style.display = 'none';
        }
    }

    toggleDetailedView() {
        const techDetails = this.dashboard.querySelector('#technical-details');
        const recSection = this.dashboard.querySelector('#recommendations-section');
        
        if (techDetails.style.display === 'none') {
            techDetails.style.display = 'block';
            recSection.style.display = 'block';
        } else {
            techDetails.style.display = 'none';
            recSection.style.display = 'none';
        }
    }

    exportData() {
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            metrics: this.metrics,
            userAgent: navigator.userAgent
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `performance-metrics-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Utility methods
    setElementText(selector, text) {
        const element = this.dashboard.querySelector(`#${selector}`) || 
                       this.dashboard.querySelector(selector);
        if (element) element.textContent = text;
    }

    setElementClass(selector, className) {
        const element = this.dashboard.querySelector(`#${selector}`) || 
                       this.dashboard.querySelector(selector);
        if (element) {
            element.className = element.className.replace(/status-\w+/g, '');
            element.classList.add(className);
        }
    }

    formatDuration(ms) {
        if (ms < 1000) return `${Math.round(ms)}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
    }

    getRatingClass(rating) {
        return `status-${rating.replace('-', '-')}`;
    }

    getRatingEmoji(rating) {
        const emojis = {
            'good': '✅',
            'needs-improvement': '⚠️',
            'poor': '❌'
        };
        return emojis[rating] || '🔄';
    }

    rateTTFB(value) {
        if (value <= 800) return 'good';
        if (value <= 1800) return 'needs-improvement';
        return 'poor';
    }

    scoreLCP(value) {
        if (value <= 2500) return 100;
        if (value <= 4000) return 75;
        return 50;
    }

    scoreFID(value) {
        if (value <= 100) return 100;
        if (value <= 300) return 75;
        return 50;
    }

    scoreCLS(value) {
        if (value <= 0.1) return 100;
        if (value <= 0.25) return 75;
        return 50;
    }
}

// Initialize Performance Dashboard
window.addEventListener('DOMContentLoaded', () => {
    window.performanceDashboard = new PerformanceDashboard({
        autoShow: false,
        position: 'bottom-right',
        updateInterval: 5000,
        enableKeyboardShortcut: true,
        enableDebugMode: window.location.search.includes('debug=true')
    });

    // Show dashboard if debug parameter is present
    if (window.location.search.includes('perf=true')) {
        window.performanceDashboard.show();
    }
});