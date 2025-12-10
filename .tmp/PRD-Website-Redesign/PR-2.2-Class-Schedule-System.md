# PR 2.2: Class Schedule System Implementation

## PR Metadata

**Title:** feat: Implement dynamic class schedule system with booking  
**Branch:** `feature/class-schedule`  
**Base:** `feature/homepage-navigation`  
**Dependencies:**
- PR 1.1 (Project Setup)
- PR 1.4 (Database Schema)
- PR 2.1 (Homepage & Navigation)

## Overview

This PR implements a comprehensive class schedule system with real-time availability, filtering, booking capabilities, and calendar integration using semantic HTML5, CSS3, vanilla JavaScript, and Vercel Serverless Functions.

## File Structure

```
/
├── schedule.html
├── classes/
│   ├── salsa.html
│   ├── bachata.html
│   └── private.html
├── api/
│   ├── schedule/
│   │   ├── index.js
│   │   ├── classes.js
│   │   ├── availability.js
│   │   └── booking.js
│   └── calendar/
│       └── export.js
├── static/
│   ├── css/
│   │   ├── schedule.css
│   │   ├── calendar.css
│   │   └── booking-modal.css
│   ├── js/
│   │   ├── schedule.js
│   │   ├── calendar.js
│   │   ├── filters.js
│   │   └── booking.js
└── tests/
    ├── schedule.test.js
    └── booking.test.js
```

## Implementation Details

### 1. Schedule Page HTML (`schedule.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Class schedule for Salsa, Bachata, and Latin dance classes at Sabor con Flow Dance">
    <title>Class Schedule - Sabor con Flow Dance</title>
    
    <!-- Critical CSS -->
    <style>
        :root {
            --schedule-gap: 1rem;
            --card-radius: 12px;
            --filter-height: 60px;
        }
        
        .schedule-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .schedule-grid {
            display: grid;
            gap: var(--schedule-gap);
            min-height: 400px;
        }
        
        @media (min-width: 768px) {
            .schedule-grid {
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            }
        }
    </style>
    
    <!-- Async CSS -->
    <link rel="preload" href="/static/css/schedule.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <link rel="preload" href="/static/css/calendar.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript>
        <link rel="stylesheet" href="/static/css/schedule.css">
        <link rel="stylesheet" href="/static/css/calendar.css">
    </noscript>
</head>
<body>
    <!-- Navigation (included from PR 2.1) -->
    <nav class="main-nav"><!-- ... --></nav>
    
    <main id="main-content">
        <!-- Page Header -->
        <header class="page-header">
            <div class="container">
                <h1>Class Schedule</h1>
                <p>Find the perfect dance class for your schedule and skill level</p>
            </div>
        </header>
        
        <!-- Schedule Controls -->
        <section class="schedule-controls" aria-label="Schedule filters and view options">
            <div class="container">
                <!-- View Toggle -->
                <div class="view-toggle" role="tablist" aria-label="Schedule view">
                    <button role="tab" 
                            aria-selected="true" 
                            aria-controls="week-view"
                            data-view="week"
                            class="view-btn active">
                        Week View
                    </button>
                    <button role="tab" 
                            aria-selected="false" 
                            aria-controls="month-view"
                            data-view="month"
                            class="view-btn">
                        Month View
                    </button>
                    <button role="tab" 
                            aria-selected="false" 
                            aria-controls="list-view"
                            data-view="list"
                            class="view-btn">
                        List View
                    </button>
                </div>
                
                <!-- Filters -->
                <div class="schedule-filters">
                    <!-- Dance Style Filter -->
                    <div class="filter-group">
                        <label for="style-filter" class="sr-only">Filter by dance style</label>
                        <select id="style-filter" class="filter-select" aria-label="Dance style">
                            <option value="">All Styles</option>
                            <option value="salsa">Salsa</option>
                            <option value="bachata">Bachata</option>
                            <option value="latin">Latin Mix</option>
                            <option value="private">Private Lessons</option>
                        </select>
                    </div>
                    
                    <!-- Level Filter -->
                    <div class="filter-group">
                        <label for="level-filter" class="sr-only">Filter by level</label>
                        <select id="level-filter" class="filter-select" aria-label="Skill level">
                            <option value="">All Levels</option>
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                            <option value="all-levels">All Levels Welcome</option>
                        </select>
                    </div>
                    
                    <!-- Instructor Filter -->
                    <div class="filter-group">
                        <label for="instructor-filter" class="sr-only">Filter by instructor</label>
                        <select id="instructor-filter" class="filter-select" aria-label="Instructor">
                            <option value="">All Instructors</option>
                            <!-- Populated dynamically -->
                        </select>
                    </div>
                    
                    <!-- Time Filter -->
                    <div class="filter-group">
                        <label for="time-filter" class="sr-only">Filter by time</label>
                        <select id="time-filter" class="filter-select" aria-label="Time of day">
                            <option value="">Any Time</option>
                            <option value="morning">Morning (6am-12pm)</option>
                            <option value="afternoon">Afternoon (12pm-6pm)</option>
                            <option value="evening">Evening (6pm-10pm)</option>
                        </select>
                    </div>
                    
                    <!-- Clear Filters -->
                    <button class="clear-filters-btn" aria-label="Clear all filters">
                        Clear Filters
                    </button>
                </div>
                
                <!-- Calendar Export -->
                <div class="calendar-actions">
                    <button class="btn-secondary" id="export-calendar">
                        <svg width="20" height="20" aria-hidden="true">
                            <use href="#icon-calendar"></use>
                        </svg>
                        Export to Calendar
                    </button>
                </div>
            </div>
        </section>
        
        <!-- Schedule Views -->
        <section class="schedule-container">
            <!-- Week View -->
            <div id="week-view" role="tabpanel" class="schedule-view active">
                <div class="week-calendar">
                    <!-- Days of Week -->
                    <div class="week-header">
                        <div class="time-column"></div>
                        <div class="day-column" data-day="monday">
                            <h3>Monday</h3>
                            <time datetime="2024-01-15">Jan 15</time>
                        </div>
                        <div class="day-column" data-day="tuesday">
                            <h3>Tuesday</h3>
                            <time datetime="2024-01-16">Jan 16</time>
                        </div>
                        <div class="day-column" data-day="wednesday">
                            <h3>Wednesday</h3>
                            <time datetime="2024-01-17">Jan 17</time>
                        </div>
                        <div class="day-column" data-day="thursday">
                            <h3>Thursday</h3>
                            <time datetime="2024-01-18">Jan 18</time>
                        </div>
                        <div class="day-column" data-day="friday">
                            <h3>Friday</h3>
                            <time datetime="2024-01-19">Jan 19</time>
                        </div>
                        <div class="day-column" data-day="saturday">
                            <h3>Saturday</h3>
                            <time datetime="2024-01-20">Jan 20</time>
                        </div>
                        <div class="day-column" data-day="sunday">
                            <h3>Sunday</h3>
                            <time datetime="2024-01-21">Jan 21</time>
                        </div>
                    </div>
                    
                    <!-- Time Slots -->
                    <div class="week-body">
                        <!-- Generated by JavaScript -->
                    </div>
                </div>
            </div>
            
            <!-- Month View -->
            <div id="month-view" role="tabpanel" class="schedule-view" hidden>
                <div class="month-calendar">
                    <!-- Month navigation -->
                    <div class="month-nav">
                        <button class="month-prev" aria-label="Previous month">
                            <svg><use href="#icon-chevron-left"></use></svg>
                        </button>
                        <h2 class="month-title">January 2024</h2>
                        <button class="month-next" aria-label="Next month">
                            <svg><use href="#icon-chevron-right"></use></svg>
                        </button>
                    </div>
                    
                    <!-- Calendar Grid -->
                    <div class="month-grid">
                        <!-- Generated by JavaScript -->
                    </div>
                </div>
            </div>
            
            <!-- List View -->
            <div id="list-view" role="tabpanel" class="schedule-view" hidden>
                <div class="schedule-list">
                    <!-- Loading State -->
                    <div class="loading-state" aria-live="polite" aria-busy="true">
                        <div class="spinner"></div>
                        <p>Loading schedule...</p>
                    </div>
                    
                    <!-- Schedule Cards (populated by JS) -->
                    <div class="schedule-grid" role="list">
                        <!-- Class cards will be inserted here -->
                    </div>
                    
                    <!-- Empty State -->
                    <div class="empty-state" hidden>
                        <svg class="empty-icon" width="100" height="100">
                            <use href="#icon-calendar-empty"></use>
                        </svg>
                        <h3>No classes found</h3>
                        <p>Try adjusting your filters or check back later for new classes.</p>
                        <button class="btn-primary" onclick="location.href='/contact'">
                            Contact Us
                        </button>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Class Card Template -->
        <template id="class-card-template">
            <article class="class-card" role="listitem">
                <div class="class-header">
                    <span class="class-style badge"></span>
                    <span class="class-level badge"></span>
                </div>
                
                <h3 class="class-title"></h3>
                
                <div class="class-meta">
                    <div class="class-time">
                        <svg width="16" height="16" aria-hidden="true">
                            <use href="#icon-clock"></use>
                        </svg>
                        <time></time>
                    </div>
                    
                    <div class="class-instructor">
                        <svg width="16" height="16" aria-hidden="true">
                            <use href="#icon-user"></use>
                        </svg>
                        <span></span>
                    </div>
                    
                    <div class="class-duration">
                        <svg width="16" height="16" aria-hidden="true">
                            <use href="#icon-timer"></use>
                        </svg>
                        <span></span>
                    </div>
                </div>
                
                <div class="class-availability">
                    <div class="availability-bar">
                        <div class="availability-fill"></div>
                    </div>
                    <span class="availability-text"></span>
                </div>
                
                <div class="class-actions">
                    <button class="btn-primary book-btn" data-class-id="">
                        Book Now
                    </button>
                    <button class="btn-secondary details-btn" data-class-id="">
                        Details
                    </button>
                </div>
            </article>
        </template>
    </main>
    
    <!-- Booking Modal -->
    <dialog id="booking-modal" class="modal" aria-labelledby="modal-title">
        <div class="modal-content">
            <header class="modal-header">
                <h2 id="modal-title">Book Class</h2>
                <button class="modal-close" aria-label="Close modal">&times;</button>
            </header>
            
            <div class="modal-body">
                <!-- Class details -->
                <div class="booking-class-info">
                    <h3 class="booking-class-title"></h3>
                    <p class="booking-class-datetime"></p>
                    <p class="booking-class-instructor"></p>
                </div>
                
                <!-- Booking form -->
                <form id="booking-form" class="booking-form">
                    <div class="form-group">
                        <label for="booking-name">Full Name *</label>
                        <input type="text" 
                               id="booking-name" 
                               name="name" 
                               required
                               aria-required="true">
                    </div>
                    
                    <div class="form-group">
                        <label for="booking-email">Email *</label>
                        <input type="email" 
                               id="booking-email" 
                               name="email" 
                               required
                               aria-required="true">
                    </div>
                    
                    <div class="form-group">
                        <label for="booking-phone">Phone Number</label>
                        <input type="tel" 
                               id="booking-phone" 
                               name="phone">
                    </div>
                    
                    <div class="form-group">
                        <label for="booking-experience">Experience Level</label>
                        <select id="booking-experience" name="experience">
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="booking-notes">Special Requests or Notes</label>
                        <textarea id="booking-notes" 
                                  name="notes" 
                                  rows="3"></textarea>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn-secondary" data-close-modal>
                            Cancel
                        </button>
                        <button type="submit" class="btn-primary">
                            Confirm Booking
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </dialog>
    
    <!-- SVG Icons -->
    <svg style="display: none;">
        <defs>
            <symbol id="icon-calendar" viewBox="0 0 24 24">
                <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
            </symbol>
            <!-- More icons... -->
        </defs>
    </svg>
    
    <!-- JavaScript Modules -->
    <script type="module" src="/static/js/schedule.js"></script>
    <script type="module" src="/static/js/calendar.js"></script>
    <script type="module" src="/static/js/filters.js"></script>
    <script type="module" src="/static/js/booking.js"></script>
</body>
</html>
```

### 2. Schedule JavaScript Module (`static/js/schedule.js`)

```javascript
/**
 * Schedule Management Module
 * Handles class schedule display, filtering, and interactions
 */

class ScheduleManager {
    constructor() {
        this.classes = [];
        this.filteredClasses = [];
        this.currentView = 'list';
        this.filters = {
            style: '',
            level: '',
            instructor: '',
            time: ''
        };
        
        this.elements = {
            container: document.querySelector('.schedule-container'),
            grid: document.querySelector('.schedule-grid'),
            loadingState: document.querySelector('.loading-state'),
            emptyState: document.querySelector('.empty-state'),
            viewButtons: document.querySelectorAll('.view-btn'),
            filterSelects: document.querySelectorAll('.filter-select'),
            clearFiltersBtn: document.querySelector('.clear-filters-btn'),
            exportBtn: document.getElementById('export-calendar')
        };
        
        this.init();
    }
    
    async init() {
        // Load classes from API
        await this.loadClasses();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize view
        this.renderView();
        
        // Set up real-time updates
        this.setupRealtimeUpdates();
    }
    
    async loadClasses() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/schedule/classes', {
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.classes = data.classes;
            this.filteredClasses = [...this.classes];
            
            // Populate instructor filter
            this.populateInstructorFilter();
            
        } catch (error) {
            console.error('Error loading classes:', error);
            this.showError('Failed to load schedule. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    setupEventListeners() {
        // View toggle
        this.elements.viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });
        
        // Filters
        this.elements.filterSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.applyFilters();
            });
        });
        
        // Clear filters
        if (this.elements.clearFiltersBtn) {
            this.elements.clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }
        
        // Export calendar
        if (this.elements.exportBtn) {
            this.elements.exportBtn.addEventListener('click', () => {
                this.exportToCalendar();
            });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.activeElement.tagName === 'SELECT') {
                document.activeElement.blur();
            }
        });
    }
    
    switchView(view) {
        this.currentView = view;
        
        // Update buttons
        this.elements.viewButtons.forEach(btn => {
            const isActive = btn.dataset.view === view;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-selected', isActive);
        });
        
        // Update view panels
        document.querySelectorAll('.schedule-view').forEach(panel => {
            const isActive = panel.id === `${view}-view`;
            panel.hidden = !isActive;
            if (isActive) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
        
        // Render appropriate view
        this.renderView();
    }
    
    renderView() {
        switch (this.currentView) {
            case 'week':
                this.renderWeekView();
                break;
            case 'month':
                this.renderMonthView();
                break;
            case 'list':
            default:
                this.renderListView();
        }
    }
    
    renderListView() {
        const grid = document.querySelector('#list-view .schedule-grid');
        if (!grid) return;
        
        // Clear existing content
        grid.innerHTML = '';
        
        if (this.filteredClasses.length === 0) {
            this.showEmptyState(true);
            return;
        }
        
        this.showEmptyState(false);
        
        // Get template
        const template = document.getElementById('class-card-template');
        
        // Render each class
        this.filteredClasses.forEach(classData => {
            const card = this.createClassCard(classData, template);
            grid.appendChild(card);
        });
        
        // Animate cards
        this.animateCards();
    }
    
    renderWeekView() {
        const weekBody = document.querySelector('.week-body');
        if (!weekBody) return;
        
        // Clear existing content
        weekBody.innerHTML = '';
        
        // Create time slots (6am to 10pm)
        const startHour = 6;
        const endHour = 22;
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        
        // Create grid structure
        for (let hour = startHour; hour < endHour; hour++) {
            const row = document.createElement('div');
            row.className = 'time-row';
            
            // Time label
            const timeLabel = document.createElement('div');
            timeLabel.className = 'time-label';
            timeLabel.textContent = this.formatHour(hour);
            row.appendChild(timeLabel);
            
            // Day cells
            days.forEach(day => {
                const cell = document.createElement('div');
                cell.className = 'day-cell';
                cell.dataset.day = day;
                cell.dataset.hour = hour;
                
                // Find classes for this time slot
                const classesInSlot = this.filteredClasses.filter(c => {
                    const classDate = new Date(c.datetime);
                    const classDay = this.getDayName(classDate.getDay());
                    const classHour = classDate.getHours();
                    return classDay === day && classHour === hour;
                });
                
                // Add class blocks
                classesInSlot.forEach(classData => {
                    const block = this.createClassBlock(classData);
                    cell.appendChild(block);
                });
                
                row.appendChild(cell);
            });
            
            weekBody.appendChild(row);
        }
    }
    
    renderMonthView() {
        const monthGrid = document.querySelector('.month-grid');
        if (!monthGrid) return;
        
        // Clear existing content
        monthGrid.innerHTML = '';
        
        // Get current month and year
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth();
        
        // Get first day of month
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // Create day headers
        const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        dayHeaders.forEach(day => {
            const header = document.createElement('div');
            header.className = 'month-day-header';
            header.textContent = day;
            monthGrid.appendChild(header);
        });
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay.getDay(); i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'month-day empty';
            monthGrid.appendChild(emptyCell);
        }
        
        // Add days of month
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'month-day';
            
            const dayNumber = document.createElement('div');
            dayNumber.className = 'day-number';
            dayNumber.textContent = day;
            dayCell.appendChild(dayNumber);
            
            // Find classes for this day
            const dayClasses = this.filteredClasses.filter(c => {
                const classDate = new Date(c.datetime);
                return classDate.getDate() === day && 
                       classDate.getMonth() === month && 
                       classDate.getFullYear() === year;
            });
            
            // Add class count indicator
            if (dayClasses.length > 0) {
                const indicator = document.createElement('div');
                indicator.className = 'day-classes';
                indicator.textContent = `${dayClasses.length} class${dayClasses.length > 1 ? 'es' : ''}`;
                dayCell.appendChild(indicator);
                
                // Make clickable
                dayCell.classList.add('has-classes');
                dayCell.addEventListener('click', () => {
                    this.showDayClasses(day, month, year, dayClasses);
                });
            }
            
            monthGrid.appendChild(dayCell);
        }
    }
    
    createClassCard(classData, template) {
        const card = template.content.cloneNode(true);
        
        // Fill in class data
        card.querySelector('.class-style').textContent = classData.style;
        card.querySelector('.class-style').classList.add(`badge-${classData.style.toLowerCase()}`);
        
        card.querySelector('.class-level').textContent = classData.level;
        card.querySelector('.class-title').textContent = classData.title;
        
        const datetime = new Date(classData.datetime);
        card.querySelector('.class-time time').textContent = this.formatTime(datetime);
        card.querySelector('.class-time time').setAttribute('datetime', classData.datetime);
        
        card.querySelector('.class-instructor span').textContent = classData.instructor;
        card.querySelector('.class-duration span').textContent = `${classData.duration} min`;
        
        // Availability
        const availabilityPercent = ((classData.capacity - classData.enrolled) / classData.capacity) * 100;
        card.querySelector('.availability-fill').style.width = `${100 - availabilityPercent}%`;
        card.querySelector('.availability-text').textContent = 
            `${classData.capacity - classData.enrolled} spots available`;
        
        // Add warning if almost full
        if (availabilityPercent < 20) {
            card.querySelector('.class-availability').classList.add('low-availability');
        }
        
        // Set data attributes for booking
        const bookBtn = card.querySelector('.book-btn');
        bookBtn.dataset.classId = classData.id;
        bookBtn.addEventListener('click', () => this.handleBooking(classData));
        
        const detailsBtn = card.querySelector('.details-btn');
        detailsBtn.dataset.classId = classData.id;
        detailsBtn.addEventListener('click', () => this.showClassDetails(classData));
        
        return card;
    }
    
    createClassBlock(classData) {
        const block = document.createElement('div');
        block.className = `class-block style-${classData.style.toLowerCase()}`;
        block.dataset.classId = classData.id;
        
        const title = document.createElement('div');
        title.className = 'block-title';
        title.textContent = classData.title;
        block.appendChild(title);
        
        const time = document.createElement('div');
        time.className = 'block-time';
        time.textContent = this.formatTime(new Date(classData.datetime));
        block.appendChild(time);
        
        block.addEventListener('click', () => this.showClassDetails(classData));
        
        return block;
    }
    
    applyFilters() {
        // Get filter values
        this.filters.style = document.getElementById('style-filter')?.value || '';
        this.filters.level = document.getElementById('level-filter')?.value || '';
        this.filters.instructor = document.getElementById('instructor-filter')?.value || '';
        this.filters.time = document.getElementById('time-filter')?.value || '';
        
        // Filter classes
        this.filteredClasses = this.classes.filter(classData => {
            // Style filter
            if (this.filters.style && classData.style.toLowerCase() !== this.filters.style) {
                return false;
            }
            
            // Level filter
            if (this.filters.level && classData.level.toLowerCase() !== this.filters.level) {
                return false;
            }
            
            // Instructor filter
            if (this.filters.instructor && classData.instructor !== this.filters.instructor) {
                return false;
            }
            
            // Time filter
            if (this.filters.time) {
                const hour = new Date(classData.datetime).getHours();
                switch (this.filters.time) {
                    case 'morning':
                        if (hour < 6 || hour >= 12) return false;
                        break;
                    case 'afternoon':
                        if (hour < 12 || hour >= 18) return false;
                        break;
                    case 'evening':
                        if (hour < 18 || hour >= 22) return false;
                        break;
                }
            }
            
            return true;
        });
        
        // Re-render view
        this.renderView();
        
        // Update filter button state
        const hasFilters = Object.values(this.filters).some(v => v !== '');
        if (this.elements.clearFiltersBtn) {
            this.elements.clearFiltersBtn.disabled = !hasFilters;
        }
    }
    
    clearFilters() {
        // Reset filter values
        this.elements.filterSelects.forEach(select => {
            select.value = '';
        });
        
        // Reset filter object
        this.filters = {
            style: '',
            level: '',
            instructor: '',
            time: ''
        };
        
        // Reset filtered classes
        this.filteredClasses = [...this.classes];
        
        // Re-render
        this.renderView();
        
        // Disable clear button
        if (this.elements.clearFiltersBtn) {
            this.elements.clearFiltersBtn.disabled = true;
        }
    }
    
    populateInstructorFilter() {
        const instructorFilter = document.getElementById('instructor-filter');
        if (!instructorFilter) return;
        
        // Get unique instructors
        const instructors = [...new Set(this.classes.map(c => c.instructor))].sort();
        
        // Clear existing options (except first)
        while (instructorFilter.options.length > 1) {
            instructorFilter.remove(1);
        }
        
        // Add instructor options
        instructors.forEach(instructor => {
            const option = document.createElement('option');
            option.value = instructor;
            option.textContent = instructor;
            instructorFilter.appendChild(option);
        });
    }
    
    async handleBooking(classData) {
        // Import booking module dynamically
        const { BookingModal } = await import('./booking.js');
        const modal = new BookingModal();
        modal.open(classData);
    }
    
    async showClassDetails(classData) {
        // Could open a modal or navigate to detail page
        console.log('Show details for class:', classData);
    }
    
    async exportToCalendar() {
        try {
            const response = await fetch('/api/calendar/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    classes: this.filteredClasses.map(c => c.id)
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to export calendar');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'sabor-con-flow-schedule.ics';
            a.click();
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting calendar:', error);
            alert('Failed to export calendar. Please try again.');
        }
    }
    
    setupRealtimeUpdates() {
        // Poll for updates every 30 seconds
        setInterval(() => {
            this.checkForUpdates();
        }, 30000);
        
        // Listen for visibility change to refresh when tab becomes active
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkForUpdates();
            }
        });
    }
    
    async checkForUpdates() {
        try {
            const response = await fetch('/api/schedule/availability');
            if (!response.ok) return;
            
            const updates = await response.json();
            
            // Update availability for each class
            updates.forEach(update => {
                const classIndex = this.classes.findIndex(c => c.id === update.id);
                if (classIndex !== -1) {
                    this.classes[classIndex].enrolled = update.enrolled;
                    
                    // Re-render if this class is visible
                    if (this.filteredClasses.some(c => c.id === update.id)) {
                        this.renderView();
                    }
                }
            });
            
        } catch (error) {
            console.error('Error checking for updates:', error);
        }
    }
    
    // Utility methods
    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
    
    formatHour(hour) {
        const period = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour > 12 ? hour - 12 : hour;
        return `${displayHour}:00 ${period}`;
    }
    
    getDayName(dayIndex) {
        const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        return days[dayIndex];
    }
    
    showLoading(show) {
        if (this.elements.loadingState) {
            this.elements.loadingState.hidden = !show;
            this.elements.loadingState.setAttribute('aria-busy', show);
        }
    }
    
    showEmptyState(show) {
        if (this.elements.emptyState) {
            this.elements.emptyState.hidden = !show;
        }
        if (this.elements.grid) {
            this.elements.grid.hidden = show;
        }
    }
    
    showError(message) {
        // Create error message element
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        error.setAttribute('role', 'alert');
        
        this.elements.container.prepend(error);
        
        // Remove after 5 seconds
        setTimeout(() => {
            error.remove();
        }, 5000);
    }
    
    animateCards() {
        const cards = this.elements.grid.querySelectorAll('.class-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.05}s`;
            card.classList.add('fade-in');
        });
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new ScheduleManager());
} else {
    new ScheduleManager();
}

export default ScheduleManager;
```

### 3. Vercel Serverless API (`api/schedule/classes.js`)

```javascript
/**
 * Schedule Classes API Endpoint
 * Returns class schedule data with real-time availability
 */

import { getClasses, getInstructors } from '../../lib/database';

export default async function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    try {
        // Get query parameters
        const { 
            date = new Date().toISOString().split('T')[0],
            days = 7,
            style = '',
            level = '',
            instructor = ''
        } = req.query;
        
        // Mock data - replace with actual database query
        const classes = [
            {
                id: 'cls_001',
                title: 'Beginner Salsa',
                style: 'Salsa',
                level: 'Beginner',
                instructor: 'Maria Rodriguez',
                datetime: '2024-01-15T18:00:00',
                duration: 60,
                capacity: 20,
                enrolled: 12,
                price: 25,
                description: 'Perfect for those new to salsa dancing. Learn basic steps and timing.',
                location: 'Studio A',
                image: '/static/images/classes/salsa-beginner.jpg'
            },
            {
                id: 'cls_002',
                title: 'Intermediate Bachata',
                style: 'Bachata',
                level: 'Intermediate',
                instructor: 'Carlos Mendez',
                datetime: '2024-01-15T19:30:00',
                duration: 90,
                capacity: 15,
                enrolled: 14,
                price: 30,
                description: 'Build on your bachata foundation with more complex patterns and musicality.',
                location: 'Studio B',
                image: '/static/images/classes/bachata-intermediate.jpg'
            },
            {
                id: 'cls_003',
                title: 'Advanced Salsa Styling',
                style: 'Salsa',
                level: 'Advanced',
                instructor: 'Maria Rodriguez',
                datetime: '2024-01-16T18:00:00',
                duration: 75,
                capacity: 12,
                enrolled: 8,
                price: 35,
                description: 'Focus on styling, body movement, and advanced turn patterns.',
                location: 'Studio A',
                image: '/static/images/classes/salsa-advanced.jpg'
            },
            {
                id: 'cls_004',
                title: 'Latin Mix Party',
                style: 'Latin',
                level: 'All Levels',
                instructor: 'Team',
                datetime: '2024-01-17T20:00:00',
                duration: 120,
                capacity: 50,
                enrolled: 32,
                price: 15,
                description: 'Social dance party with a mix of salsa, bachata, and merengue.',
                location: 'Main Hall',
                image: '/static/images/classes/latin-party.jpg'
            },
            {
                id: 'cls_005',
                title: 'Private Lesson',
                style: 'Private',
                level: 'Customized',
                instructor: 'Available Instructors',
                datetime: '2024-01-16T15:00:00',
                duration: 60,
                capacity: 2,
                enrolled: 0,
                price: 80,
                description: 'One-on-one or couple instruction tailored to your needs.',
                location: 'Studio C',
                image: '/static/images/classes/private-lesson.jpg'
            }
        ];
        
        // Filter classes based on parameters
        let filteredClasses = classes;
        
        if (style) {
            filteredClasses = filteredClasses.filter(c => 
                c.style.toLowerCase() === style.toLowerCase()
            );
        }
        
        if (level) {
            filteredClasses = filteredClasses.filter(c => 
                c.level.toLowerCase() === level.toLowerCase()
            );
        }
        
        if (instructor) {
            filteredClasses = filteredClasses.filter(c => 
                c.instructor.toLowerCase().includes(instructor.toLowerCase())
            );
        }
        
        // Sort by datetime
        filteredClasses.sort((a, b) => 
            new Date(a.datetime) - new Date(b.datetime)
        );
        
        res.status(200).json({
            success: true,
            classes: filteredClasses,
            meta: {
                total: filteredClasses.length,
                date: date,
                days: days
            }
        });
        
    } catch (error) {
        console.error('Error fetching classes:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch class schedule'
        });
    }
}
```

### 4. Booking API (`api/schedule/booking.js`)

```javascript
/**
 * Class Booking API Endpoint
 * Handles class reservations and confirmations
 */

import { createBooking, checkAvailability, sendConfirmationEmail } from '../../lib/booking';

export default async function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'POST') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    try {
        const {
            classId,
            name,
            email,
            phone,
            experience,
            notes
        } = req.body;
        
        // Validate required fields
        if (!classId || !name || !email) {
            res.status(400).json({
                success: false,
                error: 'Missing required fields'
            });
            return;
        }
        
        // Check class availability
        const isAvailable = await checkAvailability(classId);
        
        if (!isAvailable) {
            res.status(400).json({
                success: false,
                error: 'This class is full. Please choose another time.'
            });
            return;
        }
        
        // Create booking
        const booking = await createBooking({
            classId,
            name,
            email,
            phone,
            experience,
            notes,
            createdAt: new Date().toISOString()
        });
        
        // Send confirmation email
        await sendConfirmationEmail({
            to: email,
            name: name,
            booking: booking
        });
        
        res.status(200).json({
            success: true,
            booking: {
                id: booking.id,
                confirmationCode: booking.confirmationCode,
                classDetails: booking.classDetails
            },
            message: 'Booking confirmed! Check your email for details.'
        });
        
    } catch (error) {
        console.error('Booking error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to process booking. Please try again.'
        });
    }
}
```

### 5. Schedule CSS (`static/css/schedule.css`)

```css
/* Schedule Page Styles */

.page-header {
    background: linear-gradient(135deg, var(--primary-color), var(--dark-color));
    color: var(--white);
    padding: 4rem 0 2rem;
    margin-top: var(--nav-height);
}

.page-header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

/* Schedule Controls */
.schedule-controls {
    background: var(--white);
    border-bottom: 1px solid var(--secondary-color);
    padding: 1.5rem 0;
    position: sticky;
    top: var(--nav-height);
    z-index: 100;
}

.view-toggle {
    display: inline-flex;
    gap: 0.5rem;
    background: var(--secondary-color);
    padding: 0.25rem;
    border-radius: 25px;
    margin-bottom: 1rem;
}

.view-btn {
    padding: 0.5rem 1.5rem;
    background: transparent;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}

.view-btn.active {
    background: var(--white);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Filters */
.schedule-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
}

.filter-group {
    flex: 1;
    min-width: 150px;
}

.filter-select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: var(--white);
    font-size: 0.95rem;
    cursor: pointer;
}

.filter-select:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(230, 57, 70, 0.1);
}

.clear-filters-btn {
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.clear-filters-btn:hover:not(:disabled) {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.clear-filters-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Schedule Views */
.schedule-view {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* List View */
.schedule-grid {
    display: grid;
    gap: 1.5rem;
    padding: 2rem 0;
}

@media (min-width: 768px) {
    .schedule-grid {
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    }
}

/* Class Card */
.class-card {
    background: var(--white);
    border-radius: var(--card-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    padding: 1.5rem;
    transition: all 0.3s ease;
    animation: slideUp 0.4s ease backwards;
}

.class-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.class-header {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-salsa {
    background: #FFE5E5;
    color: #D32F2F;
}

.badge-bachata {
    background: #E8F5E9;
    color: #388E3C;
}

.badge-latin {
    background: #FFF3E0;
    color: #F57C00;
}

.badge-private {
    background: #F3E5F5;
    color: #7B1FA2;
}

.class-title {
    font-size: 1.25rem;
    margin-bottom: 1rem;
    color: var(--dark-color);
}

.class-meta {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
    color: #666;
    font-size: 0.9rem;
}

.class-meta > div {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.class-meta svg {
    fill: currentColor;
    opacity: 0.6;
}

/* Availability Bar */
.class-availability {
    margin: 1rem 0;
}

.availability-bar {
    height: 8px;
    background: #E0E0E0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.availability-fill {
    height: 100%;
    background: var(--accent-color);
    transition: width 0.3s ease;
}

.low-availability .availability-fill {
    background: var(--primary-color);
}

.availability-text {
    font-size: 0.85rem;
    color: #666;
}

.low-availability .availability-text {
    color: var(--primary-color);
    font-weight: 600;
}

/* Class Actions */
.class-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1.5rem;
}

.class-actions button {
    flex: 1;
}

/* Week View */
.week-calendar {
    overflow-x: auto;
    background: var(--white);
    border-radius: var(--card-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.week-header {
    display: grid;
    grid-template-columns: 80px repeat(7, 1fr);
    border-bottom: 2px solid var(--secondary-color);
    background: #FAFAFA;
}

.day-column {
    padding: 1rem;
    text-align: center;
    border-right: 1px solid #E0E0E0;
}

.day-column:last-child {
    border-right: none;
}

.day-column h3 {
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.day-column time {
    font-size: 0.8rem;
    color: #666;
}

.week-body {
    min-height: 600px;
}

.time-row {
    display: grid;
    grid-template-columns: 80px repeat(7, 1fr);
    border-bottom: 1px solid #E0E0E0;
    min-height: 60px;
}

.time-label {
    padding: 0.5rem;
    font-size: 0.85rem;
    color: #666;
    text-align: right;
    background: #FAFAFA;
    border-right: 1px solid #E0E0E0;
}

.day-cell {
    border-right: 1px solid #E0E0E0;
    padding: 0.25rem;
    position: relative;
}

.day-cell:last-child {
    border-right: none;
}

.class-block {
    padding: 0.5rem;
    border-radius: 6px;
    margin: 0.25rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.85rem;
}

.class-block:hover {
    transform: scale(1.02);
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.style-salsa {
    background: #FFCDD2;
    color: #B71C1C;
}

.style-bachata {
    background: #C8E6C9;
    color: #1B5E20;
}

.style-latin {
    background: #FFE082;
    color: #E65100;
}

.style-private {
    background: #E1BEE7;
    color: #4A148C;
}

.block-title {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.block-time {
    font-size: 0.75rem;
    opacity: 0.8;
}

/* Month View */
.month-calendar {
    background: var(--white);
    border-radius: var(--card-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    padding: 1.5rem;
}

.month-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.month-nav button {
    background: transparent;
    border: 1px solid #ddd;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.month-nav button:hover {
    background: var(--secondary-color);
    border-color: var(--primary-color);
}

.month-title {
    font-size: 1.5rem;
    color: var(--dark-color);
}

.month-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 1px;
    background: #E0E0E0;
    border: 1px solid #E0E0E0;
}

.month-day-header {
    background: var(--secondary-color);
    padding: 0.75rem;
    text-align: center;
    font-weight: 600;
    font-size: 0.9rem;
}

.month-day {
    background: var(--white);
    min-height: 80px;
    padding: 0.5rem;
    position: relative;
}

.month-day.empty {
    background: #FAFAFA;
}

.month-day.has-classes {
    cursor: pointer;
}

.month-day.has-classes:hover {
    background: var(--secondary-color);
}

.day-number {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.day-classes {
    font-size: 0.75rem;
    color: var(--primary-color);
    font-weight: 500;
}

/* Loading & Empty States */
.loading-state {
    text-align: center;
    padding: 4rem 2rem;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 3px solid var(--secondary-color);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.empty-state {
    text-align: center;
    padding: 4rem 2rem;
}

.empty-icon {
    fill: #E0E0E0;
    margin-bottom: 1.5rem;
}

.empty-state h3 {
    color: var(--dark-color);
    margin-bottom: 0.5rem;
}

.empty-state p {
    color: #666;
    margin-bottom: 1.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .page-header h1 {
        font-size: 2rem;
    }
    
    .schedule-filters {
        flex-direction: column;
    }
    
    .filter-group {
        width: 100%;
    }
    
    .view-toggle {
        width: 100%;
        justify-content: center;
    }
    
    .week-header,
    .time-row {
        grid-template-columns: 60px repeat(7, minmax(100px, 1fr));
    }
    
    .month-grid {
        font-size: 0.85rem;
    }
    
    .month-day {
        min-height: 60px;
    }
}

/* Print Styles */
@media print {
    .schedule-controls {
        display: none;
    }
    
    .class-card {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #ddd;
    }
    
    .class-actions {
        display: none;
    }
}

/* Accessibility */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* Focus styles */
button:focus-visible,
a:focus-visible,
select:focus-visible {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Animation classes */
.fade-in {
    animation: fadeIn 0.4s ease backwards;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}