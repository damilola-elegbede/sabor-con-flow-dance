# PR 3.1: Booking System & Calendly Integration

## PR Metadata
- **Title**: Implement Booking System with Calendly Integration
- **Type**: Feature Implementation
- **Priority**: High
- **Dependencies**: 
  - PR 1.1: Core Navigation & Header (base layout)
  - PR 1.2: Hero Section & CTA (booking buttons)
  - PR 2.1: Contact Forms (form validation patterns)
- **Target Branch**: `feature/booking-system-calendly`
- **Estimated Effort**: 16 hours
- **Testing Requirements**: API mocks, fallback scenarios, mobile testing

## Implementation Overview

### Core Features
1. **Calendly Widget Integration** with fallback booking form
2. **Multi-instructor booking** system with availability checking
3. **Class type selection** with dynamic pricing
4. **Booking confirmation** with email notifications
5. **Admin dashboard** for booking management
6. **Real-time availability** updates via webhooks

### Technical Architecture

```
Frontend (Vanilla JS)
├── BookingWidget.js       // Main booking interface
├── CalendlyIntegration.js // External service wrapper
├── AvailabilityChecker.js // Real-time slot checking
└── BookingForm.js        // Fallback form system

Backend (Vercel Functions)
├── /api/bookings        // CRUD operations
├── /api/availability    // Real-time availability
├── /api/calendly-webhook // Webhook handler
└── /api/send-confirmation // Email notifications
```

## File Structure

```
api/
├── bookings.js              // Main booking API
├── availability.js          // Availability checker
├── calendly-webhook.js      // Webhook handler
├── send-confirmation.js     // Email service
└── admin/booking-management.js

static/js/
├── booking-widget.js        // Main booking component
├── calendly-integration.js  // Calendly wrapper
├── availability-checker.js  // Real-time updates
└── booking-form.js         // Fallback system

static/css/
├── booking-widget.css       // Booking UI styles
└── calendly-custom.css     // Calendly overrides

templates/
├── booking/
│   ├── booking-widget.html
│   ├── booking-success.html
│   └── booking-error.html
└── admin/
    └── booking-dashboard.html
```

## Implementation Details

### 1. Calendly Integration with Fallback

**File: `static/js/calendly-integration.js`**
```javascript
class CalendlyIntegration {
  constructor(config) {
    this.calendlyUrl = config.calendlyUrl;
    this.fallbackForm = config.fallbackForm;
    this.retryAttempts = 3;
    this.timeout = 10000;
  }

  async initialize() {
    // Check if Calendly is available
    if (await this.isCalendlyAvailable()) {
      return this.loadCalendlyWidget();
    } else {
      console.warn('Calendly unavailable, using fallback booking form');
      return this.showFallbackForm();
    }
  }

  async isCalendlyAvailable() {
    try {
      const response = await fetch('https://calendly.com/api/health', {
        method: 'HEAD',
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch (error) {
      console.error('Calendly health check failed:', error);
      return false;
    }
  }

  loadCalendlyWidget() {
    return new Promise((resolve, reject) => {
      // Load Calendly script dynamically
      const script = document.createElement('script');
      script.src = 'https://assets.calendly.com/assets/external/widget.js';
      script.async = true;
      
      script.onload = () => {
        this.initializeWidget();
        resolve(true);
      };
      
      script.onerror = () => {
        console.error('Failed to load Calendly widget');
        this.showFallbackForm();
        resolve(false);
      };
      
      document.head.appendChild(script);
    });
  }

  initializeWidget() {
    Calendly.initializeWidget({
      url: this.calendlyUrl,
      parentElement: document.getElementById('calendly-widget'),
      prefill: this.getPrefillData(),
      utm: this.getUTMParameters()
    });

    // Listen for Calendly events
    this.setupCalendlyEventListeners();
  }

  setupCalendlyEventListeners() {
    window.addEventListener('message', (e) => {
      if (this.isCalendlyEvent(e)) {
        this.handleCalendlyEvent(e.data);
      }
    });
  }

  isCalendlyEvent(e) {
    return e.data.event && 
           e.data.event.indexOf('calendly') === 0 &&
           e.origin === 'https://calendly.com';
  }

  handleCalendlyEvent(data) {
    switch (data.event) {
      case 'calendly.event_scheduled':
        this.handleBookingSuccess(data.payload);
        break;
      case 'calendly.date_and_time_selected':
        this.handleSlotSelection(data.payload);
        break;
      case 'calendly.event_type_viewed':
        this.trackEventView(data.payload);
        break;
    }
  }

  async handleBookingSuccess(payload) {
    try {
      // Save booking to local database
      await fetch('/api/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          calendlyEventUri: payload.event.uri,
          inviteeUri: payload.invitee.uri,
          eventStartTime: payload.event.start_time,
          eventEndTime: payload.event.end_time,
          inviteeEmail: payload.invitee.email,
          inviteeName: payload.invitee.name,
          bookingSource: 'calendly'
        })
      });

      // Show success message
      this.showBookingConfirmation(payload);
      
      // Track conversion
      this.trackBookingConversion(payload);
      
    } catch (error) {
      console.error('Error processing booking:', error);
      this.showBookingError();
    }
  }

  showFallbackForm() {
    const fallbackForm = new BookingForm({
      container: '#booking-container',
      onSubmit: this.handleFallbackBooking.bind(this)
    });
    fallbackForm.render();
  }

  async handleFallbackBooking(formData) {
    try {
      const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          bookingSource: 'fallback_form'
        })
      });

      if (response.ok) {
        const booking = await response.json();
        this.showBookingConfirmation(booking);
      } else {
        throw new Error('Booking submission failed');
      }
    } catch (error) {
      console.error('Fallback booking error:', error);
      this.showBookingError();
    }
  }

  getPrefillData() {
    // Get user data from localStorage or URL params
    const urlParams = new URLSearchParams(window.location.search);
    return {
      email: urlParams.get('email') || localStorage.getItem('userEmail'),
      firstName: urlParams.get('firstName') || localStorage.getItem('firstName'),
      lastName: urlParams.get('lastName') || localStorage.getItem('lastName'),
      a1: urlParams.get('classType') || 'salsa' // Custom question
    };
  }

  getUTMParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
      utmCampaign: urlParams.get('utm_campaign'),
      utmSource: urlParams.get('utm_source'),
      utmMedium: urlParams.get('utm_medium'),
      utmContent: urlParams.get('utm_content'),
      utmTerm: urlParams.get('utm_term')
    };
  }
}
```

### 2. Booking Widget with Real-time Availability

**File: `static/js/booking-widget.js`**
```javascript
class BookingWidget {
  constructor(container, options = {}) {
    this.container = document.querySelector(container);
    this.instructors = options.instructors || [];
    this.classTypes = options.classTypes || [];
    this.availabilityEndpoint = '/api/availability';
    this.bookingEndpoint = '/api/bookings';
    this.eventSource = null;
    this.selectedSlots = new Set();
  }

  async render() {
    this.container.innerHTML = this.getWidgetHTML();
    await this.loadInitialData();
    this.setupEventListeners();
    this.startRealTimeUpdates();
  }

  getWidgetHTML() {
    return `
      <div class="booking-widget">
        <div class="booking-header">
          <h2>Book Your Dance Lesson</h2>
          <p>Select your preferred instructor, class type, and time slot</p>
        </div>
        
        <form class="booking-form" id="booking-form">
          <!-- Step 1: Class Type Selection -->
          <div class="booking-step active" id="step-class-type">
            <h3>Choose Class Type</h3>
            <div class="class-type-grid" id="class-type-grid">
              ${this.renderClassTypes()}
            </div>
          </div>
          
          <!-- Step 2: Instructor Selection -->
          <div class="booking-step" id="step-instructor">
            <h3>Select Instructor</h3>
            <div class="instructor-grid" id="instructor-grid">
              ${this.renderInstructors()}
            </div>
          </div>
          
          <!-- Step 3: Time Slot Selection -->
          <div class="booking-step" id="step-time-slot">
            <h3>Available Time Slots</h3>
            <div class="calendar-container">
              <div class="calendar-header">
                <button type="button" class="nav-btn" id="prev-week">&lt;</button>
                <span class="current-week" id="current-week"></span>
                <button type="button" class="nav-btn" id="next-week">&gt;</button>
              </div>
              <div class="calendar-grid" id="calendar-grid"></div>
            </div>
          </div>
          
          <!-- Step 4: Personal Information -->
          <div class="booking-step" id="step-personal-info">
            <h3>Your Information</h3>
            <div class="form-row">
              <input type="text" name="firstName" placeholder="First Name" required>
              <input type="text" name="lastName" placeholder="Last Name" required>
            </div>
            <div class="form-row">
              <input type="email" name="email" placeholder="Email Address" required>
              <input type="tel" name="phone" placeholder="Phone Number">
            </div>
            <textarea name="notes" placeholder="Special requests or notes (optional)"></textarea>
          </div>
          
          <!-- Navigation -->
          <div class="booking-navigation">
            <button type="button" class="btn-secondary" id="prev-step" style="display: none;">Previous</button>
            <button type="button" class="btn-primary" id="next-step">Next</button>
            <button type="submit" class="btn-primary" id="submit-booking" style="display: none;">Book Lesson</button>
          </div>
        </form>
        
        <!-- Booking Summary -->
        <div class="booking-summary" id="booking-summary">
          <h3>Booking Summary</h3>
          <div class="summary-content" id="summary-content"></div>
          <div class="summary-total" id="summary-total"></div>
        </div>
      </div>
    `;
  }

  renderClassTypes() {
    return this.classTypes.map(classType => `
      <div class="class-type-card" data-class-type="${classType.id}">
        <div class="class-icon">${classType.icon}</div>
        <h4>${classType.name}</h4>
        <p>${classType.description}</p>
        <div class="class-price">$${classType.price}</div>
        <div class="class-duration">${classType.duration} minutes</div>
      </div>
    `).join('');
  }

  renderInstructors() {
    return this.instructors.map(instructor => `
      <div class="instructor-card" data-instructor="${instructor.id}">
        <div class="instructor-photo">
          <img src="${instructor.photo}" alt="${instructor.name}" loading="lazy">
        </div>
        <h4>${instructor.name}</h4>
        <p>${instructor.specialties.join(', ')}</p>
        <div class="instructor-rating">
          ${'★'.repeat(instructor.rating)}
          <span class="rating-count">(${instructor.reviewCount})</span>
        </div>
        <div class="instructor-availability" id="availability-${instructor.id}">
          Loading availability...
        </div>
      </div>
    `).join('');
  }

  async loadInitialData() {
    try {
      // Load class types and instructors from API
      const [classTypesRes, instructorsRes] = await Promise.all([
        fetch('/api/class-types'),
        fetch('/api/instructors')
      ]);
      
      this.classTypes = await classTypesRes.json();
      this.instructors = await instructorsRes.json();
      
      // Update the DOM with loaded data
      this.updateClassTypeGrid();
      this.updateInstructorGrid();
      
    } catch (error) {
      console.error('Error loading initial data:', error);
      this.showError('Failed to load booking data');
    }
  }

  setupEventListeners() {
    // Class type selection
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.class-type-card')) {
        this.handleClassTypeSelection(e.target.closest('.class-type-card'));
      }
    });

    // Instructor selection
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.instructor-card')) {
        this.handleInstructorSelection(e.target.closest('.instructor-card'));
      }
    });

    // Calendar navigation
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'prev-week') {
        this.navigateWeek(-1);
      } else if (e.target.id === 'next-week') {
        this.navigateWeek(1);
      }
    });

    // Time slot selection
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('.time-slot')) {
        this.handleTimeSlotSelection(e.target.closest('.time-slot'));
      }
    });

    // Step navigation
    this.container.addEventListener('click', (e) => {
      if (e.target.id === 'next-step') {
        this.nextStep();
      } else if (e.target.id === 'prev-step') {
        this.prevStep();
      }
    });

    // Form submission
    this.container.addEventListener('submit', (e) => {
      if (e.target.id === 'booking-form') {
        e.preventDefault();
        this.handleBookingSubmission();
      }
    });
  }

  async handleClassTypeSelection(card) {
    // Remove previous selection
    this.container.querySelectorAll('.class-type-card').forEach(c => 
      c.classList.remove('selected'));
    
    // Add selection
    card.classList.add('selected');
    
    // Store selection
    this.selectedClassType = card.dataset.classType;
    
    // Update availability for instructors
    await this.updateInstructorAvailability();
    
    // Update summary
    this.updateBookingSummary();
  }

  async handleInstructorSelection(card) {
    // Remove previous selection
    this.container.querySelectorAll('.instructor-card').forEach(c => 
      c.classList.remove('selected'));
    
    // Add selection
    card.classList.add('selected');
    
    // Store selection
    this.selectedInstructor = card.dataset.instructor;
    
    // Load calendar for selected instructor
    await this.loadCalendar();
    
    // Update summary
    this.updateBookingSummary();
  }

  async loadCalendar() {
    if (!this.selectedInstructor || !this.selectedClassType) {
      return;
    }

    try {
      const response = await fetch(`${this.availabilityEndpoint}?instructor=${this.selectedInstructor}&classType=${this.selectedClassType}&week=${this.currentWeek}`);
      const availability = await response.json();
      
      this.renderCalendar(availability);
    } catch (error) {
      console.error('Error loading calendar:', error);
      this.showError('Failed to load available time slots');
    }
  }

  renderCalendar(availability) {
    const calendarGrid = this.container.querySelector('#calendar-grid');
    const days = this.getWeekDays();
    
    let calendarHTML = '<div class="calendar-days">';
    
    days.forEach(day => {
      calendarHTML += `
        <div class="calendar-day">
          <div class="day-header">
            <div class="day-name">${day.name}</div>
            <div class="day-date">${day.date}</div>
          </div>
          <div class="day-slots">
            ${this.renderDaySlots(day, availability[day.dateString] || [])}
          </div>
        </div>
      `;
    });
    
    calendarHTML += '</div>';
    calendarGrid.innerHTML = calendarHTML;
  }

  renderDaySlots(day, slots) {
    return slots.map(slot => `
      <div class="time-slot ${slot.available ? 'available' : 'unavailable'}" 
           data-slot-id="${slot.id}"
           data-start-time="${slot.startTime}"
           data-end-time="${slot.endTime}">
        <div class="slot-time">${this.formatTime(slot.startTime)}</div>
        <div class="slot-status">${slot.available ? 'Available' : 'Booked'}</div>
      </div>
    `).join('');
  }

  startRealTimeUpdates() {
    // Close existing connection
    if (this.eventSource) {
      this.eventSource.close();
    }

    // Start SSE connection for real-time updates
    this.eventSource = new EventSource('/api/availability/stream');
    
    this.eventSource.onmessage = (event) => {
      const update = JSON.parse(event.data);
      this.handleAvailabilityUpdate(update);
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      // Implement exponential backoff for reconnection
      setTimeout(() => {
        this.startRealTimeUpdates();
      }, Math.min(1000 * Math.pow(2, this.reconnectAttempts || 0), 30000));
      this.reconnectAttempts = (this.reconnectAttempts || 0) + 1;
    };
  }

  handleAvailabilityUpdate(update) {
    // Update specific time slot availability
    const slot = this.container.querySelector(`[data-slot-id="${update.slotId}"]`);
    if (slot) {
      slot.className = `time-slot ${update.available ? 'available' : 'unavailable'}`;
      slot.querySelector('.slot-status').textContent = update.available ? 'Available' : 'Booked';
    }

    // Remove from selected slots if no longer available
    if (!update.available && this.selectedSlots.has(update.slotId)) {
      this.selectedSlots.delete(update.slotId);
      this.updateBookingSummary();
    }
  }

  async handleBookingSubmission() {
    try {
      this.showLoadingState(true);
      
      const formData = new FormData(this.container.querySelector('#booking-form'));
      const bookingData = {
        classType: this.selectedClassType,
        instructor: this.selectedInstructor,
        slots: Array.from(this.selectedSlots),
        personalInfo: Object.fromEntries(formData),
        totalAmount: this.calculateTotal()
      };

      const response = await fetch(this.bookingEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookingData)
      });

      if (response.ok) {
        const booking = await response.json();
        this.showBookingSuccess(booking);
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Booking failed');
      }
      
    } catch (error) {
      console.error('Booking submission error:', error);
      this.showError(error.message || 'Failed to process booking');
    } finally {
      this.showLoadingState(false);
    }
  }

  cleanup() {
    if (this.eventSource) {
      this.eventSource.close();
    }
  }
}

// Initialize booking widget
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('#booking-widget')) {
    const bookingWidget = new BookingWidget('#booking-widget');
    bookingWidget.render();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      bookingWidget.cleanup();
    });
  }
});
```

### 3. Vercel Serverless Functions

**File: `api/bookings.js`**
```javascript
import { kv } from '@vercel/kv';
import { sendEmail } from '../lib/email-service.js';
import { validateBookingData } from '../lib/validation.js';

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    switch (req.method) {
      case 'GET':
        return await getBookings(req, res);
      case 'POST':
        return await createBooking(req, res);
      case 'PUT':
        return await updateBooking(req, res);
      case 'DELETE':
        return await cancelBooking(req, res);
      default:
        return res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    console.error('Booking API error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      message: error.message
    });
  }
}

async function createBooking(req, res) {
  const bookingData = req.body;

  // Validate booking data
  const validation = validateBookingData(bookingData);
  if (!validation.valid) {
    return res.status(400).json({ 
      error: 'Validation failed',
      details: validation.errors
    });
  }

  // Generate booking ID
  const bookingId = `booking_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Check slot availability (atomic operation)
  const slotKeys = bookingData.slots.map(slotId => `slot:${slotId}`);
  const pipeline = kv.pipeline();
  
  // Check all slots
  slotKeys.forEach(key => pipeline.get(key));
  const slotStates = await pipeline.exec();

  // Verify all slots are available
  const unavailableSlots = slotStates
    .map((state, index) => ({ state, slotId: bookingData.slots[index] }))
    .filter(({ state }) => state !== null);

  if (unavailableSlots.length > 0) {
    return res.status(409).json({
      error: 'Slots no longer available',
      unavailableSlots: unavailableSlots.map(({ slotId }) => slotId)
    });
  }

  // Create booking record
  const booking = {
    id: bookingId,
    ...bookingData,
    status: 'confirmed',
    createdAt: new Date().toISOString(),
    paymentStatus: 'pending'
  };

  // Atomic booking creation
  const bookingPipeline = kv.pipeline();
  
  // Reserve slots
  slotKeys.forEach(key => {
    bookingPipeline.set(key, bookingId, { ex: 3600 }); // 1 hour expiry
  });
  
  // Save booking
  bookingPipeline.set(`booking:${bookingId}`, booking);
  
  // Add to user bookings
  bookingPipeline.sadd(`user_bookings:${bookingData.personalInfo.email}`, bookingId);
  
  // Add to instructor bookings
  bookingPipeline.sadd(`instructor_bookings:${bookingData.instructor}`, bookingId);

  await bookingPipeline.exec();

  // Send confirmation email
  try {
    await sendConfirmationEmail(booking);
  } catch (emailError) {
    console.error('Failed to send confirmation email:', emailError);
    // Don't fail booking if email fails
  }

  // Trigger real-time availability updates
  await broadcastAvailabilityUpdate(bookingData.slots, false);

  return res.status(201).json({
    success: true,
    booking: {
      id: bookingId,
      status: booking.status,
      confirmationNumber: bookingId.substr(-8).toUpperCase()
    }
  });
}

async function getBookings(req, res) {
  const { email, instructor, status, startDate, endDate } = req.query;

  let bookingIds = [];

  if (email) {
    bookingIds = await kv.smembers(`user_bookings:${email}`);
  } else if (instructor) {
    bookingIds = await kv.smembers(`instructor_bookings:${instructor}`);
  } else {
    // Admin view - get all recent bookings
    const keys = await kv.keys('booking:*');
    bookingIds = keys.map(key => key.replace('booking:', ''));
  }

  if (bookingIds.length === 0) {
    return res.json({ bookings: [] });
  }

  // Get booking details
  const pipeline = kv.pipeline();
  bookingIds.forEach(id => pipeline.get(`booking:${id}`));
  const bookings = await pipeline.exec();

  // Filter and sort bookings
  let filteredBookings = bookings
    .filter(booking => booking !== null)
    .filter(booking => {
      if (status && booking.status !== status) return false;
      if (startDate && new Date(booking.createdAt) < new Date(startDate)) return false;
      if (endDate && new Date(booking.createdAt) > new Date(endDate)) return false;
      return true;
    })
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  return res.json({ bookings: filteredBookings });
}

async function sendConfirmationEmail(booking) {
  const emailData = {
    to: booking.personalInfo.email,
    subject: 'Dance Lesson Booking Confirmation - Sabor con Flow',
    template: 'booking-confirmation',
    data: {
      customerName: `${booking.personalInfo.firstName} ${booking.personalInfo.lastName}`,
      bookingId: booking.id,
      confirmationNumber: booking.id.substr(-8).toUpperCase(),
      classType: booking.classType,
      instructor: booking.instructor,
      slots: booking.slots,
      totalAmount: booking.totalAmount
    }
  };

  return await sendEmail(emailData);
}

async function broadcastAvailabilityUpdate(slotIds, available) {
  // This would integrate with a real-time service like Pusher or WebSockets
  // For now, we'll use a simple notification system
  const updates = slotIds.map(slotId => ({
    slotId,
    available,
    timestamp: new Date().toISOString()
  }));

  // Store updates for SSE endpoint to pick up
  await kv.lpush('availability_updates', ...updates.map(u => JSON.stringify(u)));
  await kv.expire('availability_updates', 300); // 5 minutes TTL
}
```

**File: `api/availability.js`**
```javascript
import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { instructor, classType, week, date } = req.query;

    if (date) {
      // Get availability for specific date
      return await getDayAvailability(req, res, date, instructor, classType);
    } else if (week) {
      // Get availability for week
      return await getWeekAvailability(req, res, week, instructor, classType);
    } else {
      // Get general availability
      return await getGeneralAvailability(req, res, instructor, classType);
    }
  } catch (error) {
    console.error('Availability API error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

async function getWeekAvailability(req, res, week, instructor, classType) {
  const weekStart = new Date(week);
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 7);

  const availability = {};
  const currentDate = new Date(weekStart);

  // Generate availability for each day of the week
  while (currentDate < weekEnd) {
    const dateString = currentDate.toISOString().split('T')[0];
    availability[dateString] = await generateDaySlots(dateString, instructor, classType);
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return res.json(availability);
}

async function generateDaySlots(dateString, instructor, classType) {
  // Get instructor's working hours for the day
  const instructorSchedule = await getInstructorSchedule(instructor, dateString);
  
  if (!instructorSchedule || !instructorSchedule.workingHours) {
    return [];
  }

  const slots = [];
  const { startTime, endTime, breakTimes } = instructorSchedule.workingHours;
  
  // Get class duration
  const classDuration = await getClassDuration(classType);
  
  // Generate time slots
  let currentSlot = new Date(`${dateString}T${startTime}`);
  const endSlot = new Date(`${dateString}T${endTime}`);

  while (currentSlot < endSlot) {
    const slotEnd = new Date(currentSlot.getTime() + classDuration * 60000);
    
    // Check if slot conflicts with break times
    const hasBreakConflict = breakTimes.some(breakTime => {
      const breakStart = new Date(`${dateString}T${breakTime.start}`);
      const breakEnd = new Date(`${dateString}T${breakTime.end}`);
      return (currentSlot < breakEnd && slotEnd > breakStart);
    });

    if (!hasBreakConflict) {
      const slotId = `${instructor}_${dateString}_${currentSlot.getHours()}_${currentSlot.getMinutes()}`;
      const isAvailable = await checkSlotAvailability(slotId);
      
      slots.push({
        id: slotId,
        startTime: currentSlot.toTimeString().substr(0, 5),
        endTime: slotEnd.toTimeString().substr(0, 5),
        available: isAvailable,
        instructor: instructor,
        date: dateString
      });
    }

    // Move to next slot (with buffer time)
    currentSlot = new Date(slotEnd.getTime() + 15 * 60000); // 15 min buffer
  }

  return slots;
}

async function checkSlotAvailability(slotId) {
  // Check if slot is booked
  const booking = await kv.get(`slot:${slotId}`);
  return booking === null;
}

async function getInstructorSchedule(instructor, date) {
  // Get instructor's schedule from cache or database
  const schedule = await kv.get(`instructor_schedule:${instructor}`);
  
  if (!schedule) {
    // Default schedule if not found
    return {
      workingHours: {
        startTime: '09:00',
        endTime: '21:00',
        breakTimes: [
          { start: '12:00', end: '13:00' },
          { start: '17:00', end: '17:30' }
        ]
      }
    };
  }

  return schedule;
}

async function getClassDuration(classType) {
  const classInfo = await kv.get(`class_type:${classType}`);
  return classInfo?.duration || 60; // Default 60 minutes
}
```

**File: `api/calendly-webhook.js`**
```javascript
import { kv } from '@vercel/kv';
import crypto from 'crypto';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Verify Calendly webhook signature
    if (!verifyCalendlySignature(req)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const payload = req.body;
    
    switch (payload.event) {
      case 'invitee.created':
        await handleBookingCreated(payload);
        break;
      case 'invitee.canceled':
        await handleBookingCanceled(payload);
        break;
      case 'invitee_no_show.created':
        await handleNoShow(payload);
        break;
      default:
        console.log(`Unhandled Calendly event: ${payload.event}`);
    }

    return res.status(200).json({ received: true });
    
  } catch (error) {
    console.error('Calendly webhook error:', error);
    return res.status(500).json({ error: 'Webhook processing failed' });
  }
}

function verifyCalendlySignature(req) {
  const signature = req.headers['calendly-webhook-signature'];
  const timestamp = req.headers['calendly-webhook-timestamp'];
  
  if (!signature || !timestamp) {
    return false;
  }

  // Check timestamp (prevent replay attacks)
  const currentTime = Math.floor(Date.now() / 1000);
  if (Math.abs(currentTime - parseInt(timestamp)) > 300) { // 5 minutes tolerance
    return false;
  }

  // Verify signature
  const expectedSignature = crypto
    .createHmac('sha256', process.env.CALENDLY_WEBHOOK_SECRET)
    .update(timestamp + JSON.stringify(req.body))
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}

async function handleBookingCreated(payload) {
  const { event, invitee } = payload.payload;
  
  // Extract booking information
  const bookingData = {
    calendlyEventUri: event.uri,
    inviteeUri: invitee.uri,
    eventStartTime: event.start_time,
    eventEndTime: event.end_time,
    inviteeEmail: invitee.email,
    inviteeName: invitee.name,
    eventType: event.event_type,
    location: event.location,
    status: 'confirmed',
    source: 'calendly',
    createdAt: new Date().toISOString()
  };

  // Generate internal booking ID
  const bookingId = `calendly_${event.uuid}`;

  // Store booking in our system
  await kv.set(`booking:${bookingId}`, bookingData);
  await kv.sadd(`user_bookings:${invitee.email}`, bookingId);

  // Extract instructor from event type
  const instructor = extractInstructorFromEvent(event);
  if (instructor) {
    await kv.sadd(`instructor_bookings:${instructor}`, bookingId);
  }

  // Update slot availability
  const slotId = generateSlotId(event, instructor);
  await kv.set(`slot:${slotId}`, bookingId);

  // Broadcast availability update
  await broadcastAvailabilityUpdate([slotId], false);

  console.log(`Calendly booking created: ${bookingId}`);
}

async function handleBookingCanceled(payload) {
  const { event, invitee } = payload.payload;
  
  const bookingId = `calendly_${event.uuid}`;
  const booking = await kv.get(`booking:${bookingId}`);
  
  if (booking) {
    // Update booking status
    booking.status = 'canceled';
    booking.canceledAt = new Date().toISOString();
    
    await kv.set(`booking:${bookingId}`, booking);

    // Free up the slot
    const instructor = extractInstructorFromEvent(event);
    const slotId = generateSlotId(event, instructor);
    await kv.del(`slot:${slotId}`);

    // Broadcast availability update
    await broadcastAvailabilityUpdate([slotId], true);

    console.log(`Calendly booking canceled: ${bookingId}`);
  }
}

function extractInstructorFromEvent(event) {
  // Extract instructor from event type URL or custom fields
  const eventTypeUri = event.event_type;
  
  // Parse instructor from URL pattern: /instructor-name/class-type
  const match = eventTypeUri.match(/\/([^\/]+)\/[^\/]*$/);
  return match ? match[1] : 'default';
}

function generateSlotId(event, instructor) {
  const startTime = new Date(event.start_time);
  const date = startTime.toISOString().split('T')[0];
  const hours = startTime.getHours();
  const minutes = startTime.getMinutes();
  
  return `${instructor}_${date}_${hours}_${minutes}`;
}

async function broadcastAvailabilityUpdate(slotIds, available) {
  const updates = slotIds.map(slotId => ({
    slotId,
    available,
    timestamp: new Date().toISOString()
  }));

  await kv.lpush('availability_updates', ...updates.map(u => JSON.stringify(u)));
  await kv.expire('availability_updates', 300);
}
```

### 4. CSS Styling

**File: `static/css/booking-widget.css`**
```css
/* Booking Widget Styles */
.booking-widget {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--surface-color);
  border-radius: 12px;
  box-shadow: var(--shadow-medium);
}

.booking-header {
  text-align: center;
  margin-bottom: 2rem;
}

.booking-header h2 {
  color: var(--primary-color);
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.booking-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

/* Booking Steps */
.booking-step {
  display: none;
  padding: 1.5rem 0;
}

.booking-step.active {
  display: block;
}

.booking-step h3 {
  color: var(--text-primary);
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

/* Class Type Grid */
.class-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.class-type-card {
  background: var(--background-color);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.class-type-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-medium);
}

.class-type-card.selected {
  border-color: var(--primary-color);
  background: var(--primary-color-light);
}

.class-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.class-type-card h4 {
  color: var(--primary-color);
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.class-price {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--accent-color);
  margin: 0.5rem 0;
}

.class-duration {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Instructor Grid */
.instructor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.instructor-card {
  background: var(--background-color);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.instructor-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.instructor-card.selected {
  border-color: var(--primary-color);
  background: var(--primary-color-light);
}

.instructor-photo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 1rem;
  overflow: hidden;
}

.instructor-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.instructor-card h4 {
  color: var(--primary-color);
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.instructor-rating {
  color: var(--accent-color);
  margin: 0.5rem 0;
}

.rating-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.instructor-availability {
  margin-top: 1rem;
  padding: 0.5rem;
  background: var(--surface-color);
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Calendar Styles */
.calendar-container {
  background: var(--background-color);
  border-radius: 8px;
  padding: 1.5rem;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.nav-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s ease;
}

.nav-btn:hover {
  background: var(--primary-color-dark);
}

.current-week {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--text-primary);
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1rem;
}

.calendar-day {
  min-height: 200px;
}

.day-header {
  text-align: center;
  padding: 0.5rem;
  background: var(--surface-color);
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.day-name {
  font-weight: bold;
  color: var(--primary-color);
}

.day-date {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.day-slots {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.time-slot {
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.time-slot.available {
  background: var(--success-color);
  color: white;
  border: 2px solid transparent;
}

.time-slot.available:hover {
  background: var(--success-color-dark);
  transform: scale(1.02);
}

.time-slot.available.selected {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px var(--accent-color-light);
}

.time-slot.unavailable {
  background: var(--muted-color);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.slot-time {
  font-weight: bold;
}

.slot-status {
  font-size: 0.7rem;
  margin-top: 0.25rem;
}

/* Form Styles */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.booking-form input,
.booking-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.booking-form input:focus,
.booking-form textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.booking-form textarea {
  resize: vertical;
  min-height: 100px;
  grid-column: 1 / -1;
}

/* Navigation */
.booking-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

/* Booking Summary */
.booking-summary {
  background: var(--surface-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 2rem;
  border: 2px solid var(--border-color);
}

.booking-summary h3 {
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.summary-content {
  margin-bottom: 1rem;
}

.summary-total {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--accent-color);
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

/* Loading States */
.loading {
  opacity: 0.7;
  pointer-events: none;
}

.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .booking-widget {
    padding: 1rem;
    margin: 1rem;
  }
  
  .class-type-grid,
  .instructor-grid {
    grid-template-columns: 1fr;
  }
  
  .calendar-days {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .booking-navigation {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .booking-header h2 {
    font-size: 1.5rem;
  }
  
  .nav-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .time-slot {
    padding: 0.4rem;
    font-size: 0.7rem;
  }
}
```

## Testing Strategy

### 1. API Mock Testing with Vitest

**File: `tests/booking-integration.test.js`**
```javascript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BookingWidget } from '../static/js/booking-widget.js';
import { CalendlyIntegration } from '../static/js/calendly-integration.js';

// Mock external APIs
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('Booking System Integration', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="booking-widget"></div>';
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Calendly Integration', () => {
    it('should fall back to native form when Calendly is unavailable', async () => {
      // Mock Calendly health check failure
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503
      });

      const calendly = new CalendlyIntegration({
        calendlyUrl: 'https://calendly.com/test',
        fallbackForm: true
      });

      const result = await calendly.initialize();
      expect(result).toBe(false);
      expect(document.querySelector('.fallback-form')).toBeTruthy();
    });

    it('should handle booking success events', async () => {
      mockFetch
        .mockResolvedValueOnce({ ok: true }) // Health check
        .mockResolvedValueOnce({ // Booking API
          ok: true,
          json: () => Promise.resolve({ success: true, id: 'booking_123' })
        });

      const calendly = new CalendlyIntegration({
        calendlyUrl: 'https://calendly.com/test'
      });

      await calendly.initialize();

      // Simulate Calendly success event
      const mockEvent = {
        origin: 'https://calendly.com',
        data: {
          event: 'calendly.event_scheduled',
          payload: {
            event: {
              uri: 'https://calendly.com/events/test',
              start_time: '2024-01-15T10:00:00Z',
              end_time: '2024-01-15T11:00:00Z'
            },
            invitee: {
              uri: 'https://calendly.com/invitees/test',
              email: 'test@example.com',
              name: 'Test User'
            }
          }
        }
      };

      window.dispatchEvent(new MessageEvent('message', mockEvent));

      // Verify API call was made
      expect(mockFetch).toHaveBeenCalledWith('/api/bookings', 
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('test@example.com')
        })
      );
    });
  });

  describe('Booking Widget', () => {
    it('should handle real-time availability updates', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          'instructor_1': [
            { id: 'slot_1', startTime: '10:00', available: true },
            { id: 'slot_2', startTime: '11:00', available: false }
          ]
        })
      });

      const widget = new BookingWidget('#booking-widget');
      await widget.render();

      // Simulate availability update
      const updateEvent = {
        data: JSON.stringify({
          slotId: 'slot_1',
          available: false,
          timestamp: new Date().toISOString()
        })
      };

      widget.handleAvailabilityUpdate(JSON.parse(updateEvent.data));

      const slot = document.querySelector('[data-slot-id="slot_1"]');
      expect(slot.classList.contains('unavailable')).toBe(true);
    });

    it('should validate booking data before submission', async () => {
      const widget = new BookingWidget('#booking-widget');
      await widget.render();

      // Set up form with invalid data
      widget.selectedClassType = null; // Missing selection
      widget.selectedInstructor = 'instructor_1';

      const formData = new FormData();
      formData.append('email', 'invalid-email'); // Invalid email

      const result = await widget.handleBookingSubmission();
      expect(result).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('should handle API failures gracefully', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const widget = new BookingWidget('#booking-widget');
      
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      await widget.loadInitialData();
      
      expect(consoleError).toHaveBeenCalledWith('Error loading initial data:', expect.any(Error));
      
      consoleError.mockRestore();
    });

    it('should retry failed requests with exponential backoff', async () => {
      let attempts = 0;
      mockFetch.mockImplementation(() => {
        attempts++;
        if (attempts < 3) {
          return Promise.reject(new Error('Temporary failure'));
        }
        return Promise.resolve({ ok: true, json: () => ({}) });
      });

      // This would be part of a retry utility
      const retryFetch = async (url, options, maxRetries = 3) => {
        for (let i = 0; i < maxRetries; i++) {
          try {
            return await fetch(url, options);
          } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
          }
        }
      };

      const result = await retryFetch('/api/test');
      expect(result.ok).toBe(true);
      expect(attempts).toBe(3);
    });
  });
});
```

## Deployment Considerations

### Environment Variables
```bash
# Calendly Configuration
CALENDLY_API_TOKEN=your_calendly_token
CALENDLY_WEBHOOK_SECRET=your_webhook_secret
CALENDLY_CLIENT_ID=your_client_id
CALENDLY_CLIENT_SECRET=your_client_secret

# Database
KV_REST_API_URL=your_vercel_kv_url
KV_REST_API_TOKEN=your_vercel_kv_token

# Email Service
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=noreply@saborconflow.com

# Security
JWT_SECRET=your_jwt_secret
WEBHOOK_SIGNATURE_SECRET=your_signature_secret
```

### Vercel Configuration

**File: `vercel.json`**
```json
{
  "functions": {
    "api/bookings.js": {
      "maxDuration": 10
    },
    "api/calendly-webhook.js": {
      "maxDuration": 5
    },
    "api/availability.js": {
      "maxDuration": 8
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        }
      ]
    }
  ]
}
```

## Success Metrics

- **Booking Conversion**: 15% increase in lesson bookings
- **User Experience**: < 3 steps to complete booking
- **Reliability**: 99.9% uptime for booking system  
- **Fallback Success**: 100% booking form availability when Calendly is down
- **Performance**: < 2 seconds average booking completion
- **Mobile Usage**: 70% of bookings via mobile devices

## Future Enhancements

1. **Payment Integration**: Stripe payment processing
2. **Multi-language**: Spanish/English booking flow
3. **Group Bookings**: Multiple students per slot
4. **Recurring Bookings**: Package deals and subscriptions
5. **Instructor Management**: Self-service availability updates
6. **Analytics Dashboard**: Booking patterns and revenue tracking