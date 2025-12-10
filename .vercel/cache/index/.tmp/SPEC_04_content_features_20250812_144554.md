# SPEC 04: Content Features (Instructors & Gallery)
**Component:** Instructor Profiles and Media Gallery
**Priority:** P1 - Important  
**Parallel Execution:** Tasks 1-3 parallel, 4-6 parallel, 7-9 parallel

## High-Level Context
Create engaging content sections that showcase the studio's instructors and capture the energy of classes through photos and videos. These features build trust by highlighting instructor expertise and give potential students a visual preview of the dance experience.

## Mid-Level Objectives
- Build instructor profile pages with bios and videos
- Create media gallery for photos and videos
- Implement efficient media storage and delivery
- Enable easy content management through admin
- Optimize media loading for performance
- Integrate Instagram content display

## Implementation Notes
- Store media URLs only in database, files in Google Drive
- Use lazy loading for gallery images
- Implement responsive image sizing
- Cache instructor data for performance
- Follow progressive enhancement principles
- Support both photos and videos in gallery

## Required Context
- Database models from SPEC_01 (Instructor model)
- Base styling and templates from SPEC_02
- Google Drive for media storage
- Instagram API access (optional)
- Admin interface configured

## Beginning Context (Prerequisites)
### Available Files
- `core/models.py` - Instructor model defined
- `templates/base.html` - Base template
- `static/css/base.css` - Base styles
- Admin interface functional

### System State
- Database with Instructor table
- Static file serving configured
- Google Drive accessible for media
- Development server running

## Ending Context (Deliverables)
### Files to Create/Modify
- `templates/instructors/list.html` - Instructor listing page
- `templates/instructors/detail.html` - Individual instructor page
- `templates/gallery/index.html` - Media gallery page
- `templates/components/instructor_card.html` - Reusable card
- `templates/components/media_grid.html` - Gallery grid component
- `core/views.py` - Instructor and gallery views
- `static/css/instructors.css` - Instructor styles
- `static/css/gallery.css` - Gallery styles
- `static/js/gallery.js` - Gallery interactions

### System State
- Instructor profiles displaying with photos/videos
- Gallery showing class photos and videos
- Media loading optimized with lazy loading
- Admin can manage all content
- Mobile responsive layouts

## Low-Level Tasks (Implementation Prompts)

### Task 1: Create Instructor List View
**Prompt**: "In core/views.py, create instructor_list view that fetches all Instructor objects from database ordered by name. Create templates/instructors/list.html displaying instructors in a responsive grid (2 columns mobile, 3 columns desktop). Each card shows photo, name, primary specialty, and 'View Profile' button."

**Acceptance Criteria**:
- [ ] View fetches all instructors
- [ ] Responsive grid layout
- [ ] Cards show photo, name, specialty
- [ ] Links to detail pages

### Task 2: Build Instructor Detail Page
**Prompt**: "Create instructor_detail view accepting instructor ID/slug. Create templates/instructors/detail.html showing full instructor profile: large photo, full bio, all specialties as badges, embedded 30-second intro video, Instagram link, and 'Book Private Lesson' button that opens Calendly with instructor pre-selected."

**Acceptance Criteria**:
- [ ] Detail view with URL parameter
- [ ] Full profile information displayed
- [ ] Video embed working
- [ ] Instagram link functional
- [ ] Calendly integration with pre-selection

### Task 3: Design Instructor Card Component
**Prompt**: "Create templates/components/instructor_card.html as a reusable component. Card should have image with 1:1 aspect ratio, name in Playfair Display font, specialty badges with gold background, hover effect that shows brief bio excerpt, and smooth transitions. Make it flexible to work in both list and homepage contexts."

**Acceptance Criteria**:
- [ ] Reusable card component
- [ ] Consistent image aspect ratio
- [ ] Specialty badges styled
- [ ] Hover bio preview
- [ ] Smooth animations

### Task 4: Create Gallery View Structure
**Prompt**: "Create gallery_view in core/views.py that fetches media items (photos/videos) organized by event/class type. Support filtering by type (photo/video) and category (class/event/performance). Create templates/gallery/index.html with filter buttons and media grid display area."

**Acceptance Criteria**:
- [ ] Gallery view with filtering logic
- [ ] Filter buttons for type/category
- [ ] Grid layout for media items
- [ ] Support both photos and videos

### Task 5: Implement Media Grid Component
**Prompt**: "Create templates/components/media_grid.html displaying media in masonry layout. For photos: show thumbnail with lightbox on click. For videos: show thumbnail with play button overlay, open in modal when clicked. Include loading placeholders and implement lazy loading for images below fold."

**Acceptance Criteria**:
- [ ] Masonry grid layout
- [ ] Lightbox for photos
- [ ] Modal player for videos
- [ ] Lazy loading implemented
- [ ] Loading placeholders

### Task 6: Build Gallery Lightbox
**Prompt**: "Create static/js/gallery.js implementing a lightbox for photo viewing. Features: full-screen overlay with image, previous/next navigation with keyboard support, close button and ESC key to exit, swipe gestures on mobile, and image preloading for smooth transitions. Maintain aspect ratios properly."

**Acceptance Criteria**:
- [ ] Full-screen lightbox overlay
- [ ] Keyboard navigation (arrows, ESC)
- [ ] Touch/swipe support
- [ ] Image preloading
- [ ] Proper aspect ratio handling

### Task 7: Style Instructor Profiles
**Prompt**: "Create static/css/instructors.css with styles for instructor grid using CSS Grid with gap spacing, cards with soft shadows and rounded corners (8px), specialty badges with gold background (#C7B375), bio text with good typography (line-height 1.6), and video embed responsive wrapper maintaining 16:9 ratio."

**Acceptance Criteria**:
- [ ] Grid layout with proper spacing
- [ ] Card shadows and rounded corners
- [ ] Gold specialty badges
- [ ] Readable bio typography
- [ ] Responsive video embeds

### Task 8: Style Gallery Layout
**Prompt**: "Create static/css/gallery.css with masonry grid using CSS Grid or Flexbox, filter buttons with active state styling, media items with hover overlay showing type icon, loading skeletons with animated gradient, and lightbox/modal styles with semi-transparent backdrop."

**Acceptance Criteria**:
- [ ] Masonry layout working
- [ ] Filter button states
- [ ] Hover overlays on media
- [ ] Animated loading skeletons
- [ ] Lightbox styling complete

### Task 9: Add Media Management Admin
**Prompt**: "Enhance admin.py to add MediaGallery model admin with image preview in list view, bulk upload capability, drag-and-drop ordering, and category/event tagging. For Instructor admin, add inline video preview and image upload with automatic resizing."

**Acceptance Criteria**:
- [ ] Media preview in admin list
- [ ] Bulk upload interface
- [ ] Ordering capability
- [ ] Tagging system
- [ ] Automatic image optimization

### Task 10: Implement Video Player
**Prompt**: "Create a video player component for gallery videos and instructor intros. Use HTML5 video with custom controls, poster image from first frame, play button overlay, fullscreen capability, and mobile-optimized interface. For instructor videos, add autoplay on page load (muted) with play button for audio."

**Acceptance Criteria**:
- [ ] Custom HTML5 video controls
- [ ] Poster images for videos
- [ ] Fullscreen support
- [ ] Mobile-optimized player
- [ ] Autoplay handling for intros

### Task 11: Add Instagram Integration
**Prompt**: "Create function to fetch and display recent Instagram posts in the gallery. Use Instagram Basic Display API to fetch recent media, cache results for 1 hour, display in gallery grid with Instagram icon overlay, and link to original posts. Handle API failures gracefully with fallback content."

**Acceptance Criteria**:
- [ ] Instagram API integration
- [ ] Caching mechanism (1 hour)
- [ ] Instagram posts in gallery
- [ ] Links to original posts
- [ ] Graceful failure handling

### Task 12: Optimize Media Loading
**Prompt**: "Implement performance optimizations for media: create multiple image sizes (thumbnail, medium, large), use srcset for responsive images, implement lazy loading with Intersection Observer, add WebP format with JPEG fallback, and preload critical images above fold."

**Acceptance Criteria**:
- [ ] Multiple image sizes generated
- [ ] Srcset implementation
- [ ] Lazy loading working
- [ ] WebP with fallbacks
- [ ] Critical images preloaded

## Parallel Execution Groups

**Group A (Parallel):**
- Task 1: Instructor list view
- Task 2: Instructor detail page
- Task 3: Instructor card component

**Group B (Parallel):**
- Task 4: Gallery view structure
- Task 5: Media grid component
- Task 6: Gallery lightbox

**Group C (Parallel):**
- Task 7: Instructor styles
- Task 8: Gallery styles
- Task 9: Media admin

**Group D (Sequential):**
- Task 10: Video player
- Task 11: Instagram integration  
- Task 12: Performance optimization

## Success Metrics
- Instructor pages increase engagement by 30%
- Gallery page time > 2 minutes average
- Media loading under 1 second
- Instagram integration increases social follows by 20%
- Mobile performance score > 90

## Risk Mitigation
- Fallback for video loading issues
- Placeholder images for missing media
- Graceful Instagram API failure handling
- CDN backup for Google Drive outages
- Progressive enhancement for JavaScript features