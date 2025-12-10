/**
 * Pricing Calculator for Sabor Con Flow Dance
 * Calculates savings between drop-in classes and packages
 */

class PricingCalculator {
    constructor() {
        this.dropInPrice = 20;
        this.package4Price = 70;
        this.package8Price = 120;
        
        this.elements = {
            input: document.getElementById('classes-per-month'),
            dropInCost: document.getElementById('drop-in-cost'),
            packageCost: document.getElementById('package-cost'),
            savingsAmount: document.getElementById('savings-amount'),
            savingsPercentage: document.getElementById('savings-percentage'),
            recommendationText: document.getElementById('recommendation-text')
        };
        
        this.init();
    }
    
    init() {
        // Check if all elements exist
        if (!this.validateElements()) {
            console.warn('Pricing calculator elements not found. Calculator may not function properly.');
            return;
        }
        
        // Add event listeners
        this.elements.input.addEventListener('input', () => this.calculate());
        this.elements.input.addEventListener('change', () => this.calculate());
        
        // Calculate initial values
        this.calculate();
        
        // Add keyboard support
        this.elements.input.addEventListener('keydown', (e) => this.handleKeydown(e));
    }
    
    validateElements() {
        return Object.values(this.elements).every(element => element !== null);
    }
    
    handleKeydown(event) {
        // Allow: backspace, delete, tab, escape, enter
        if ([46, 8, 9, 27, 13].indexOf(event.keyCode) !== -1 ||
            // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
            (event.keyCode === 65 && event.ctrlKey === true) ||
            (event.keyCode === 67 && event.ctrlKey === true) ||
            (event.keyCode === 86 && event.ctrlKey === true) ||
            (event.keyCode === 88 && event.ctrlKey === true) ||
            // Allow: home, end, left, right, down, up
            (event.keyCode >= 35 && event.keyCode <= 40)) {
            return;
        }
        // Ensure that it is a number and stop the keypress
        if ((event.shiftKey || (event.keyCode < 48 || event.keyCode > 57)) && (event.keyCode < 96 || event.keyCode > 105)) {
            event.preventDefault();
        }
    }
    
    calculate() {
        const classesPerMonth = parseInt(this.elements.input.value) || 0;
        
        if (classesPerMonth < 1) {
            this.resetDisplay();
            return;
        }
        
        const dropInCost = classesPerMonth * this.dropInPrice;
        const bestPackage = this.getBestPackage(classesPerMonth);
        const packageCost = bestPackage.cost;
        const savings = Math.max(0, dropInCost - packageCost);
        const savingsPercentage = dropInCost > 0 ? ((savings / dropInCost) * 100) : 0;
        
        this.updateDisplay({
            dropInCost,
            packageCost,
            savings,
            savingsPercentage,
            packageName: bestPackage.name,
            recommendation: this.getRecommendation(classesPerMonth, savings)
        });
    }
    
    getBestPackage(classesPerMonth) {
        // Calculate how many packages needed for the month
        const packages4Needed = Math.ceil(classesPerMonth / 4);
        const packages8Needed = Math.ceil(classesPerMonth / 8);
        
        const cost4 = packages4Needed * this.package4Price;
        const cost8 = packages8Needed * this.package8Price;
        
        // Return the cheaper option
        if (cost4 <= cost8) {
            return {
                name: '4-Class Package',
                cost: cost4,
                packagesNeeded: packages4Needed
            };
        } else {
            return {
                name: '8-Class Package',
                cost: cost8,
                packagesNeeded: packages8Needed
            };
        }
    }
    
    getRecommendation(classesPerMonth, savings) {
        if (classesPerMonth === 1) {
            return "Drop-in classes are perfect for occasional dancers!";
        } else if (classesPerMonth <= 4) {
            if (savings > 0) {
                return "The 4-Class Package is perfect for you!";
            } else {
                return "Drop-in classes work well for your schedule.";
            }
        } else if (classesPerMonth <= 8) {
            return savings > 20 ? "Great savings with our 8-Class Package!" : "The 4-Class Package offers good value.";
        } else {
            return "Maximum savings with multiple 8-Class Packages!";
        }
    }
    
    updateDisplay(data) {
        // Add animation class
        const resultItems = document.querySelectorAll('.calculator-result-item');
        resultItems.forEach(item => {
            item.classList.add('updated');
            setTimeout(() => item.classList.remove('updated'), 600);
        });
        
        // Update values
        this.elements.dropInCost.textContent = `$${data.dropInCost}`;
        this.elements.packageCost.textContent = `$${data.packageCost}`;
        this.elements.savingsAmount.textContent = `$${data.savings}`;
        this.elements.savingsPercentage.textContent = `(${data.savingsPercentage.toFixed(1)}%)`;
        this.elements.recommendationText.textContent = data.recommendation;
        
        // Update savings highlight
        const savingsHighlight = document.querySelector('.savings-highlight');
        if (data.savings > 0) {
            savingsHighlight.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)';
            savingsHighlight.style.color = 'white';
        } else {
            savingsHighlight.style.background = 'linear-gradient(135deg, #f3f4f6, #e5e7eb)';
            savingsHighlight.style.color = 'var(--color-gray-dark)';
        }
        
        // Announce changes for screen readers
        this.announceChanges(data);
    }
    
    announceChanges(data) {
        // Create announcement for screen readers
        const announcement = `Updated calculation: Drop-in cost $${data.dropInCost}, Package cost $${data.packageCost}, Savings $${data.savings}`;
        
        // Create or update aria-live region
        let liveRegion = document.getElementById('calculator-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'calculator-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
        
        liveRegion.textContent = announcement;
    }
    
    resetDisplay() {
        this.elements.dropInCost.textContent = '$0';
        this.elements.packageCost.textContent = '$0';
        this.elements.savingsAmount.textContent = '$0';
        this.elements.savingsPercentage.textContent = '(0%)';
        this.elements.recommendationText.textContent = 'Enter number of classes to see savings!';
    }
}

// Graceful degradation - provide basic functionality without JavaScript
function initializeFallback() {
    const form = document.createElement('form');
    form.method = 'GET';
    form.style.display = 'none';
    
    const input = document.getElementById('classes-per-month');
    if (input) {
        input.addEventListener('change', function() {
            const classes = parseInt(this.value) || 0;
            const dropIn = classes * 20;
            const package4 = Math.ceil(classes / 4) * 70;
            const package8 = Math.ceil(classes / 8) * 120;
            const bestPackage = package4 <= package8 ? package4 : package8;
            const savings = Math.max(0, dropIn - bestPackage);
            
            // Update display elements if they exist
            const elements = {
                dropInCost: document.getElementById('drop-in-cost'),
                packageCost: document.getElementById('package-cost'),
                savingsAmount: document.getElementById('savings-amount'),
                savingsPercentage: document.getElementById('savings-percentage')
            };
            
            if (elements.dropInCost) elements.dropInCost.textContent = `$${dropIn}`;
            if (elements.packageCost) elements.packageCost.textContent = `$${bestPackage}`;
            if (elements.savingsAmount) elements.savingsAmount.textContent = `$${savings}`;
            if (elements.savingsPercentage) {
                const percentage = dropIn > 0 ? ((savings / dropIn) * 100).toFixed(1) : 0;
                elements.savingsPercentage.textContent = `(${percentage}%)`;
            }
        });
    }
}

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we have the required elements
    const hasCalculatorElements = document.getElementById('classes-per-month') && 
                                 document.getElementById('drop-in-cost') &&
                                 document.getElementById('package-cost') &&
                                 document.getElementById('savings-amount');
    
    if (hasCalculatorElements) {
        try {
            new PricingCalculator();
        } catch (error) {
            console.warn('Failed to initialize advanced calculator, falling back to basic functionality:', error);
            initializeFallback();
        }
    }
});

// Export for potential testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PricingCalculator;
}