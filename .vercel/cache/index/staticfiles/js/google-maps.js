/**
 * Google Maps Integration for Sabor con Flow Dance
 * Professional implementation with dark theme and responsive design
 */

class SaborMapsManager {
    constructor() {
        this.map = null;
        this.marker = null;
        this.infoWindow = null;
        this.isLoaded = false;
        
        // Load configuration from global variable set by Django template
        const config = window.SABOR_MAP_CONFIG || {};
        
        // Studio location (fallback to Boulder, CO if not configured)
        this.studioLocation = config.studioLocation || {
            lat: 40.0150, // Boulder, CO coordinates
            lng: -105.2705
        };
        
        // Zoom level
        this.zoomLevel = config.zoomLevel || 16;
        
        // Business information (with fallbacks)
        this.businessInfo = {
            name: config.businessInfo?.name || "Sabor con Flow Dance",
            address: config.businessInfo?.address || "Avalon Ballroom<br>Boulder, CO",
            phone: config.businessInfo?.phone || "(555) 123-4567",
            email: config.businessInfo?.email || "saborconflowdance@gmail.com",
            website: "https://saborconflowdance.com"
        };
        
        // Dark theme map styling
        this.mapStyles = [
            {
                "elementType": "geometry",
                "stylers": [{"color": "#1d2c4d"}]
            },
            {
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#8ec3b9"}]
            },
            {
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#1a3646"}]
            },
            {
                "featureType": "administrative.country",
                "elementType": "geometry.stroke",
                "stylers": [{"color": "#4b6878"}]
            },
            {
                "featureType": "administrative.land_parcel",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#64779e"}]
            },
            {
                "featureType": "administrative.province",
                "elementType": "geometry.stroke",
                "stylers": [{"color": "#4b6878"}]
            },
            {
                "featureType": "landscape.man_made",
                "elementType": "geometry.stroke",
                "stylers": [{"color": "#334e87"}]
            },
            {
                "featureType": "landscape.natural",
                "elementType": "geometry",
                "stylers": [{"color": "#023e58"}]
            },
            {
                "featureType": "poi",
                "elementType": "geometry",
                "stylers": [{"color": "#283d6a"}]
            },
            {
                "featureType": "poi",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#6f9ba5"}]
            },
            {
                "featureType": "poi",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#1d2c4d"}]
            },
            {
                "featureType": "poi.park",
                "elementType": "geometry.fill",
                "stylers": [{"color": "#023e58"}]
            },
            {
                "featureType": "poi.park",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#3C7680"}]
            },
            {
                "featureType": "road",
                "elementType": "geometry",
                "stylers": [{"color": "#304a7d"}]
            },
            {
                "featureType": "road",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#98a5be"}]
            },
            {
                "featureType": "road",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#1d2c4d"}]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry",
                "stylers": [{"color": "#2c6675"}]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry.stroke",
                "stylers": [{"color": "#255763"}]
            },
            {
                "featureType": "road.highway",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#b0d5ce"}]
            },
            {
                "featureType": "road.highway",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#023e58"}]
            },
            {
                "featureType": "transit",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#98a5be"}]
            },
            {
                "featureType": "transit",
                "elementType": "labels.text.stroke",
                "stylers": [{"color": "#1d2c4d"}]
            },
            {
                "featureType": "transit.line",
                "elementType": "geometry.fill",
                "stylers": [{"color": "#283d6a"}]
            },
            {
                "featureType": "transit.station",
                "elementType": "geometry",
                "stylers": [{"color": "#3a4762"}]
            },
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [{"color": "#0e1626"}]
            },
            {
                "featureType": "water",
                "elementType": "labels.text.fill",
                "stylers": [{"color": "#4e6d70"}]
            }
        ];
        
        this.init();
    }
    
    init() {
        // Initialize map when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeMap());
        } else {
            this.initializeMap();
        }
    }
    
    initializeMap() {
        const mapContainer = document.getElementById('sabor-google-map');
        if (!mapContainer) {
            console.warn('Google Maps container not found');
            return;
        }
        
        try {
            // Create the map
            this.map = new google.maps.Map(mapContainer, {
                center: this.studioLocation,
                zoom: this.zoomLevel, // Configurable zoom level
                styles: this.mapStyles,
                mapTypeControl: false,
                streetViewControl: true,
                fullscreenControl: true,
                zoomControl: true,
                gestureHandling: 'cooperative',
                // Accessibility
                keyboardShortcuts: true,
                // Performance
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                backgroundColor: '#1d2c4d'
            });
            
            // Create custom marker
            this.createCustomMarker();
            
            // Create info window
            this.createInfoWindow();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Handle responsive sizing
            this.handleResize();
            
            this.isLoaded = true;
            
            // Dispatch custom event for successful load
            this.dispatchMapEvent('mapLoaded');
            
        } catch (error) {
            console.error('Error initializing Google Maps:', error);
            this.showMapError();
        }
    }
    
    createCustomMarker() {
        // Create custom marker icon with Sabor con Flow branding
        const markerIcon = {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 12,
            fillColor: '#C7B375', // Gold brand color
            fillOpacity: 1,
            strokeColor: '#FFFFFF',
            strokeWeight: 3,
            strokeOpacity: 1
        };
        
        // Create the marker
        this.marker = new google.maps.Marker({
            position: this.studioLocation,
            map: this.map,
            icon: markerIcon,
            title: this.businessInfo.name,
            animation: google.maps.Animation.DROP,
            optimized: false // Better for custom styling
        });
        
        // Add marker click event
        this.marker.addListener('click', () => {
            this.openInfoWindow();
        });
    }
    
    createInfoWindow() {
        const infoContent = `
            <div class="map-info-window">
                <div class="info-header">
                    <h3>${this.businessInfo.name}</h3>
                </div>
                <div class="info-content">
                    <div class="info-item">
                        <div class="info-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                            </svg>
                        </div>
                        <span>${this.businessInfo.address}</span>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                            </svg>
                        </div>
                        <a href="tel:${this.businessInfo.phone.replace(/[^\d]/g, '')}">${this.businessInfo.phone}</a>
                    </div>
                    <div class="info-item">
                        <div class="info-icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                            </svg>
                        </div>
                        <a href="mailto:${this.businessInfo.email}">${this.businessInfo.email}</a>
                    </div>
                </div>
                <div class="info-actions">
                    <a href="https://maps.google.com/?q=${this.studioLocation.lat},${this.studioLocation.lng}" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       class="directions-btn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M21.71 11.29l-9-9c-.39-.39-1.02-.39-1.41 0l-9 9c-.39.39-.39 1.02 0 1.41l9 9c.39.39 1.02.39 1.41 0l9-9c.39-.38.39-1.01 0-1.41zM14 14.5V12h-4v3H8v-4c0-.55.45-1 1-1h5V7.5l3.5 3.5-3.5 3.5z"/>
                        </svg>
                        Get Directions
                    </a>
                </div>
            </div>
        `;
        
        this.infoWindow = new google.maps.InfoWindow({
            content: infoContent,
            maxWidth: 300,
            pixelOffset: new google.maps.Size(0, -10)
        });
    }
    
    openInfoWindow() {
        if (this.infoWindow && this.marker) {
            this.infoWindow.open(this.map, this.marker);
            
            // Track info window opening
            this.dispatchMapEvent('infoWindowOpened');
        }
    }
    
    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
        
        // Handle map idle event for performance tracking
        this.map.addListener('idle', () => {
            this.dispatchMapEvent('mapIdle');
        });
        
        // Handle zoom changes
        this.map.addListener('zoom_changed', () => {
            const zoom = this.map.getZoom();
            this.dispatchMapEvent('zoomChanged', { zoom });
        });
        
        // Handle center changes
        this.map.addListener('center_changed', () => {
            const center = this.map.getCenter();
            this.dispatchMapEvent('centerChanged', { 
                lat: center.lat(), 
                lng: center.lng() 
            });
        });
    }
    
    handleResize() {
        if (this.map) {
            // Trigger resize event
            google.maps.event.trigger(this.map, 'resize');
            
            // Re-center the map
            this.map.setCenter(this.studioLocation);
        }
    }
    
    showMapError() {
        const mapContainer = document.getElementById('sabor-google-map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="map-error">
                    <div class="error-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    <h3>Map Temporarily Unavailable</h3>
                    <p>We're experiencing technical difficulties loading our interactive map.</p>
                    <div class="fallback-info">
                        <h4>Our Location:</h4>
                        <p><strong>${this.businessInfo.name}</strong></p>
                        <p>${this.businessInfo.address.replace('<br>', ', ')}</p>
                        <a href="https://maps.google.com/?q=Avalon+Ballroom+Boulder+CO" 
                           target="_blank" 
                           rel="noopener noreferrer"
                           class="external-map-link">
                            View on Google Maps
                        </a>
                    </div>
                </div>
            `;
        }
        
        this.dispatchMapEvent('mapError');
    }
    
    dispatchMapEvent(eventName, data = {}) {
        const event = new CustomEvent(`sabor:map:${eventName}`, {
            detail: { ...data, timestamp: Date.now() }
        });
        document.dispatchEvent(event);
        
        // Analytics tracking if available
        if (typeof gtag === 'function') {
            gtag('event', eventName, {
                event_category: 'google_maps',
                event_label: 'sabor_con_flow_map',
                ...data
            });
        }
    }
    
    // Public methods
    recenter() {
        if (this.map) {
            this.map.setCenter(this.studioLocation);
            this.map.setZoom(this.zoomLevel);
        }
    }
    
    showInfoWindow() {
        this.openInfoWindow();
    }
    
    hideInfoWindow() {
        if (this.infoWindow) {
            this.infoWindow.close();
        }
    }
    
    getMapInstance() {
        return this.map;
    }
    
    isMapLoaded() {
        return this.isLoaded;
    }
}

// Global callback function for Google Maps API
window.initSaborMap = function() {
    window.saborMaps = new SaborMapsManager();
};

// Handle API load errors
window.handleMapError = function() {
    console.error('Failed to load Google Maps API');
    const mapContainer = document.getElementById('sabor-google-map');
    if (mapContainer && window.saborMaps) {
        window.saborMaps.showMapError();
    }
};

// Auto-initialize if Google Maps is already loaded
if (typeof google !== 'undefined' && google.maps) {
    window.initSaborMap();
}