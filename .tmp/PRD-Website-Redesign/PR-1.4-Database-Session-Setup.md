# PR 1.4: Database & Session Setup

## PR Metadata

**Title**: Database Architecture and Session Management with Vercel KV and Postgres  
**Description**: Implement database layer with Vercel KV for sessions/caching and Vercel Postgres for persistent data storage  
**Dependencies**: PR 1.1 (Project Setup), PR 1.2 (Static Site), PR 1.3 (Testing)  
**Estimated Effort**: 7-9 hours  
**Priority**: Critical Path  

## Implementation Overview

This PR establishes the database infrastructure for the Sabor con Flow Dance website using Vercel's managed database services. Vercel KV (Redis) handles sessions, caching, and real-time data, while Vercel Postgres manages persistent data storage with proper schema design, migrations, and connection pooling.

## File Structure Changes

```
api/                            # NEW - Vercel serverless functions
├── lib/                       # Database utilities and configurations
│   ├── db.js                 # Postgres connection and query builder
│   ├── kv.js                 # Redis/KV connection and utilities
│   ├── session.js            # Session management
│   ├── cache.js              # Caching strategies
│   └── migrations/           # Database migrations
│       ├── 001_initial_schema.sql
│       ├── 002_classes_instructors.sql
│       ├── 003_bookings_payments.sql
│       └── migrate.js
├── models/                   # Data models and schemas
│   ├── user.js              # User model
│   ├── class.js             # Dance class model
│   ├── instructor.js        # Instructor model
│   ├── booking.js           # Booking model
│   ├── payment.js           # Payment model
│   └── contact.js           # Contact form model
├── middleware/               # API middleware
│   ├── auth.js              # Authentication middleware
│   ├── session.js           # Session middleware
│   ├── cors.js              # CORS configuration
│   ├── rate-limit.js        # Rate limiting
│   └── error-handler.js     # Error handling middleware
├── utils/                    # Utility functions
│   ├── validation.js        # Input validation
│   ├── sanitization.js      # Data sanitization
│   ├── encryption.js        # Data encryption
│   └── email.js            # Email utilities
├── endpoints/                # API route handlers
│   ├── auth/                # Authentication endpoints
│   │   ├── login.js
│   │   ├── logout.js
│   │   ├── register.js
│   │   └── session.js
│   ├── classes/             # Class management endpoints
│   │   ├── list.js
│   │   ├── details.js
│   │   ├── schedule.js
│   │   └── availability.js
│   ├── bookings/            # Booking endpoints
│   │   ├── create.js
│   │   ├── cancel.js
│   │   ├── list.js
│   │   └── payment.js
│   ├── contact/             # Contact form endpoints
│   │   └── submit.js
│   └── admin/               # Admin endpoints
│       ├── dashboard.js
│       ├── users.js
│       └── analytics.js
└── config/                  # Configuration files
    ├── database.js         # Database configuration
    ├── redis.js           # Redis configuration
    └── environment.js     # Environment variables
```

## Implementation Steps

### 1. Database Connection Setup

```javascript
// api/lib/db.js
import { createPool } from '@vercel/postgres';
import { config } from '../config/database.js';

// Connection pool for Postgres
let pool;

export function getPool() {
  if (!pool) {
    pool = createPool({
      connectionString: process.env.POSTGRES_URL,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });
  }
  return pool;
}

// Query builder with error handling and logging
export async function query(text, params = []) {
  const start = Date.now();
  const client = getPool();
  
  try {
    const result = await client.query(text, params);
    const duration = Date.now() - start;
    
    // Log slow queries
    if (duration > 1000) {
      console.warn(`Slow query executed in ${duration}ms:`, text);
    }
    
    return result;
  } catch (error) {
    console.error('Database query error:', {
      text,
      params,
      error: error.message,
      stack: error.stack
    });
    throw error;
  }
}

// Transaction wrapper
export async function transaction(callback) {
  const client = await getPool().connect();
  
  try {
    await client.query('BEGIN');
    const result = await callback(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

// Health check
export async function healthCheck() {
  try {
    const result = await query('SELECT NOW() as current_time');
    return {
      status: 'healthy',
      timestamp: result.rows[0].current_time,
      connectionCount: pool?.totalCount || 0
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message
    };
  }
}

// Graceful shutdown
export async function closePool() {
  if (pool) {
    await pool.end();
    pool = null;
  }
}
```

```javascript
// api/lib/kv.js
import { kv } from '@vercel/kv';
import { config } from '../config/redis.js';

// KV client wrapper with error handling
class KVClient {
  constructor() {
    this.client = kv;
    this.defaultTTL = 3600; // 1 hour default TTL
  }
  
  async get(key) {
    try {
      const result = await this.client.get(key);
      console.log(`KV GET: ${key} - ${result ? 'HIT' : 'MISS'}`);
      return result;
    } catch (error) {
      console.error(`KV GET error for key ${key}:`, error);
      return null;
    }
  }
  
  async set(key, value, ttl = this.defaultTTL) {
    try {
      if (ttl > 0) {
        await this.client.setex(key, ttl, JSON.stringify(value));
      } else {
        await this.client.set(key, JSON.stringify(value));
      }
      console.log(`KV SET: ${key} - TTL: ${ttl}s`);
      return true;
    } catch (error) {
      console.error(`KV SET error for key ${key}:`, error);
      return false;
    }
  }
  
  async del(key) {
    try {
      const result = await this.client.del(key);
      console.log(`KV DEL: ${key} - Deleted: ${result}`);
      return result;
    } catch (error) {
      console.error(`KV DEL error for key ${key}:`, error);
      return 0;
    }
  }
  
  async exists(key) {
    try {
      return await this.client.exists(key);
    } catch (error) {
      console.error(`KV EXISTS error for key ${key}:`, error);
      return 0;
    }
  }
  
  async expire(key, ttl) {
    try {
      return await this.client.expire(key, ttl);
    } catch (error) {
      console.error(`KV EXPIRE error for key ${key}:`, error);
      return 0;
    }
  }
  
  async incr(key) {
    try {
      return await this.client.incr(key);
    } catch (error) {
      console.error(`KV INCR error for key ${key}:`, error);
      return null;
    }
  }
  
  // Session-specific methods
  async getSession(sessionId) {
    const key = `session:${sessionId}`;
    const data = await this.get(key);
    return data ? JSON.parse(data) : null;
  }
  
  async setSession(sessionId, data, ttl = 86400) { // 24 hours
    const key = `session:${sessionId}`;
    return await this.set(key, data, ttl);
  }
  
  async deleteSession(sessionId) {
    const key = `session:${sessionId}`;
    return await this.del(key);
  }
  
  // Cache-specific methods
  async getCache(key) {
    const cacheKey = `cache:${key}`;
    const data = await this.get(cacheKey);
    return data ? JSON.parse(data) : null;
  }
  
  async setCache(key, data, ttl = 3600) {
    const cacheKey = `cache:${key}`;
    return await this.set(cacheKey, data, ttl);
  }
  
  async invalidateCache(pattern) {
    try {
      // Note: Vercel KV doesn't support KEYS pattern matching
      // This would need to be implemented with a different approach
      // For now, we'll track cache keys separately
      console.warn(`Cache invalidation for pattern ${pattern} not implemented`);
      return 0;
    } catch (error) {
      console.error(`Cache invalidation error for pattern ${pattern}:`, error);
      return 0;
    }
  }
}

export const kvClient = new KVClient();
export default kvClient;
```

### 2. Database Schema and Migrations

```sql
-- api/lib/migrations/001_initial_schema.sql
-- Initial schema for user authentication and basic data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    experience_level VARCHAR(20) DEFAULT 'beginner' CHECK (experience_level IN ('beginner', 'intermediate', 'advanced')),
    medical_conditions TEXT,
    marketing_consent BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    is_staff BOOLEAN DEFAULT false,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table (fallback for KV)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_key VARCHAR(255) UNIQUE NOT NULL,
    session_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Contact form submissions
CREATE TABLE contact_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    subject VARCHAR(300),
    message TEXT NOT NULL,
    source VARCHAR(50) DEFAULT 'website',
    ip_address INET,
    user_agent TEXT,
    is_processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_sessions_key ON user_sessions(session_key);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_contact_created ON contact_submissions(created_at);
CREATE INDEX idx_contact_processed ON contact_submissions(is_processed);

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Updated at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

```sql
-- api/lib/migrations/002_classes_instructors.sql
-- Dance classes and instructor management

-- Instructors table
CREATE TABLE instructors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    specialties TEXT[], -- Array of dance styles
    certifications TEXT[],
    experience_years INTEGER DEFAULT 0,
    hourly_rate DECIMAL(10,2),
    profile_image_url TEXT,
    social_media_links JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dance class types
CREATE TABLE class_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    difficulty_level VARCHAR(20) NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'all-levels')),
    duration_minutes INTEGER NOT NULL DEFAULT 60,
    max_participants INTEGER DEFAULT 20,
    price_per_class DECIMAL(10,2) NOT NULL,
    image_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scheduled classes
CREATE TABLE scheduled_classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_type_id UUID REFERENCES class_types(id) ON DELETE CASCADE,
    instructor_id UUID REFERENCES instructors(id) ON DELETE CASCADE,
    title VARCHAR(200),
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    room VARCHAR(50),
    price_override DECIMAL(10,2), -- Override default class price
    is_cancelled BOOLEAN DEFAULT false,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    CONSTRAINT valid_participants CHECK (current_participants <= COALESCE(max_participants, 999))
);

-- Recurring class patterns
CREATE TABLE class_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    class_type_id UUID REFERENCES class_types(id) ON DELETE CASCADE,
    instructor_id UUID REFERENCES instructors(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0 = Sunday
    start_time TIME NOT NULL,
    duration_minutes INTEGER NOT NULL,
    max_participants INTEGER,
    room VARCHAR(50),
    effective_from DATE NOT NULL,
    effective_until DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_duration CHECK (duration_minutes > 0)
);

-- Indexes
CREATE INDEX idx_instructors_active ON instructors(is_active) WHERE is_active = true;
CREATE INDEX idx_instructors_specialties ON instructors USING GIN(specialties);
CREATE INDEX idx_class_types_active ON class_types(is_active) WHERE is_active = true;
CREATE INDEX idx_class_types_difficulty ON class_types(difficulty_level);
CREATE INDEX idx_scheduled_classes_time ON scheduled_classes(start_time, end_time);
CREATE INDEX idx_scheduled_classes_instructor ON scheduled_classes(instructor_id);
CREATE INDEX idx_scheduled_classes_type ON scheduled_classes(class_type_id);
CREATE INDEX idx_class_schedules_day_time ON class_schedules(day_of_week, start_time);

-- Triggers
CREATE TRIGGER update_instructors_updated_at BEFORE UPDATE ON instructors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_class_types_updated_at BEFORE UPDATE ON class_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scheduled_classes_updated_at BEFORE UPDATE ON scheduled_classes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3. Session Management

```javascript
// api/lib/session.js
import { kvClient } from './kv.js';
import crypto from 'crypto';
import { query } from './db.js';

export class SessionManager {
  constructor() {
    this.sessionTTL = 86400; // 24 hours
    this.cookieName = 'sabor_session';
  }
  
  // Generate secure session ID
  generateSessionId() {
    return crypto.randomBytes(32).toString('hex');
  }
  
  // Create new session
  async createSession(userId, metadata = {}) {
    const sessionId = this.generateSessionId();
    const sessionData = {
      userId,
      createdAt: new Date().toISOString(),
      lastActivity: new Date().toISOString(),
      metadata
    };
    
    try {
      // Store in KV (primary)
      await kvClient.setSession(sessionId, sessionData, this.sessionTTL);
      
      // Store in Postgres (fallback)
      await query(
        `INSERT INTO user_sessions (user_id, session_key, session_data, ip_address, user_agent, expires_at)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [
          userId,
          sessionId,
          sessionData,
          metadata.ipAddress,
          metadata.userAgent,
          new Date(Date.now() + this.sessionTTL * 1000)
        ]
      );
      
      return sessionId;
    } catch (error) {
      console.error('Session creation error:', error);
      throw new Error('Failed to create session');
    }
  }
  
  // Get session data
  async getSession(sessionId) {
    if (!sessionId) return null;
    
    try {
      // Try KV first
      let sessionData = await kvClient.getSession(sessionId);
      
      if (!sessionData) {
        // Fallback to Postgres
        const result = await query(
          `SELECT session_data, expires_at FROM user_sessions 
           WHERE session_key = $1 AND expires_at > NOW()`,
          [sessionId]
        );
        
        if (result.rows.length > 0) {
          sessionData = result.rows[0].session_data;
          // Restore to KV
          const ttl = Math.floor((new Date(result.rows[0].expires_at) - new Date()) / 1000);
          if (ttl > 0) {
            await kvClient.setSession(sessionId, sessionData, ttl);
          }
        }
      }
      
      if (sessionData) {
        // Update last activity
        sessionData.lastActivity = new Date().toISOString();
        await kvClient.setSession(sessionId, sessionData, this.sessionTTL);
      }
      
      return sessionData;
    } catch (error) {
      console.error('Session retrieval error:', error);
      return null;
    }
  }
  
  // Update session data
  async updateSession(sessionId, data) {
    const sessionData = await this.getSession(sessionId);
    if (!sessionData) {
      throw new Error('Session not found');
    }
    
    const updatedData = {
      ...sessionData,
      ...data,
      lastActivity: new Date().toISOString()
    };
    
    try {
      await kvClient.setSession(sessionId, updatedData, this.sessionTTL);
      
      // Update Postgres
      await query(
        `UPDATE user_sessions SET session_data = $1, expires_at = $2 
         WHERE session_key = $3`,
        [
          updatedData,
          new Date(Date.now() + this.sessionTTL * 1000),
          sessionId
        ]
      );
      
      return updatedData;
    } catch (error) {
      console.error('Session update error:', error);
      throw new Error('Failed to update session');
    }
  }
  
  // Destroy session
  async destroySession(sessionId) {
    try {
      await kvClient.deleteSession(sessionId);
      await query('DELETE FROM user_sessions WHERE session_key = $1', [sessionId]);
      return true;
    } catch (error) {
      console.error('Session destruction error:', error);
      return false;
    }
  }
  
  // Clean expired sessions
  async cleanExpiredSessions() {
    try {
      const result = await query(
        'DELETE FROM user_sessions WHERE expires_at < NOW() RETURNING COUNT(*)'
      );
      console.log(`Cleaned ${result.rowCount} expired sessions`);
      return result.rowCount;
    } catch (error) {
      console.error('Session cleanup error:', error);
      return 0;
    }
  }
  
  // Get session cookie options
  getCookieOptions(secure = false) {
    return {
      httpOnly: true,
      secure,
      sameSite: 'lax',
      maxAge: this.sessionTTL * 1000,
      path: '/'
    };
  }
}

export const sessionManager = new SessionManager();
```

### 4. Data Models

```javascript
// api/models/user.js
import { query, transaction } from '../lib/db.js';
import bcrypt from 'bcryptjs';

export class User {
  constructor(data) {
    Object.assign(this, data);
  }
  
  // Create new user
  static async create(userData) {
    const {
      email,
      password,
      firstName,
      lastName,
      phone,
      dateOfBirth,
      emergencyContactName,
      emergencyContactPhone,
      experienceLevel,
      medicalConditions,
      marketingConsent
    } = userData;
    
    // Hash password
    const passwordHash = await bcrypt.hash(password, 12);
    
    try {
      const result = await query(
        `INSERT INTO users (
          email, password_hash, first_name, last_name, phone, date_of_birth,
          emergency_contact_name, emergency_contact_phone, experience_level,
          medical_conditions, marketing_consent
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id, email, first_name, last_name, created_at`,
        [
          email.toLowerCase(),
          passwordHash,
          firstName,
          lastName,
          phone,
          dateOfBirth,
          emergencyContactName,
          emergencyContactPhone,
          experienceLevel,
          medicalConditions,
          marketingConsent
        ]
      );
      
      return new User(result.rows[0]);
    } catch (error) {
      if (error.code === '23505') { // Unique violation
        throw new Error('User with this email already exists');
      }
      throw error;
    }
  }
  
  // Find user by email
  static async findByEmail(email) {
    const result = await query(
      'SELECT * FROM users WHERE email = $1 AND is_active = true',
      [email.toLowerCase()]
    );
    
    return result.rows.length > 0 ? new User(result.rows[0]) : null;
  }
  
  // Find user by ID
  static async findById(id) {
    const result = await query(
      'SELECT * FROM users WHERE id = $1 AND is_active = true',
      [id]
    );
    
    return result.rows.length > 0 ? new User(result.rows[0]) : null;
  }
  
  // Verify password
  async verifyPassword(password) {
    return await bcrypt.compare(password, this.password_hash);
  }
  
  // Update user data
  async update(updateData) {
    const allowedFields = [
      'first_name', 'last_name', 'phone', 'date_of_birth',
      'emergency_contact_name', 'emergency_contact_phone',
      'experience_level', 'medical_conditions', 'marketing_consent'
    ];
    
    const updates = {};
    for (const [key, value] of Object.entries(updateData)) {
      if (allowedFields.includes(key)) {
        updates[key] = value;
      }
    }
    
    if (Object.keys(updates).length === 0) {
      return this;
    }
    
    const setClause = Object.keys(updates)
      .map((key, index) => `${key} = $${index + 2}`)
      .join(', ');
    
    const values = [this.id, ...Object.values(updates)];
    
    const result = await query(
      `UPDATE users SET ${setClause} WHERE id = $1 RETURNING *`,
      values
    );
    
    Object.assign(this, result.rows[0]);
    return this;
  }
  
  // Change password
  async changePassword(newPassword) {
    const passwordHash = await bcrypt.hash(newPassword, 12);
    
    await query(
      'UPDATE users SET password_hash = $1 WHERE id = $2',
      [passwordHash, this.id]
    );
    
    this.password_hash = passwordHash;
    return true;
  }
  
  // Deactivate user (soft delete)
  async deactivate() {
    await query(
      'UPDATE users SET is_active = false WHERE id = $1',
      [this.id]
    );
    
    this.is_active = false;
    return true;
  }
  
  // Get user's bookings
  async getBookings() {
    const result = await query(
      `SELECT b.*, sc.title, sc.start_time, sc.end_time, ct.name as class_name
       FROM bookings b
       JOIN scheduled_classes sc ON b.scheduled_class_id = sc.id
       JOIN class_types ct ON sc.class_type_id = ct.id
       WHERE b.user_id = $1
       ORDER BY sc.start_time DESC`,
      [this.id]
    );
    
    return result.rows;
  }
  
  // Serialize for API response (exclude sensitive data)
  toJSON() {
    const {
      password_hash,
      ...safeData
    } = this;
    
    return safeData;
  }
}
```

### 5. API Middleware

```javascript
// api/middleware/session.js
import { sessionManager } from '../lib/session.js';

export function withSession(handler) {
  return async (req, res) => {
    try {
      // Extract session ID from cookie
      const cookies = parseCookies(req.headers.cookie || '');
      const sessionId = cookies[sessionManager.cookieName];
      
      // Get session data
      req.session = sessionId ? await sessionManager.getSession(sessionId) : null;
      req.user = null;
      
      // If session exists, get user data
      if (req.session) {
        const { User } = await import('../models/user.js');
        req.user = await User.findById(req.session.userId);
        
        if (!req.user) {
          // User no longer exists, destroy session
          await sessionManager.destroySession(sessionId);
          req.session = null;
          
          // Clear cookie
          res.setHeader('Set-Cookie', [
            `${sessionManager.cookieName}=; Path=/; HttpOnly; Max-Age=0`
          ]);
        }
      }
      
      // Add session helper methods to response
      res.setSession = async (userId, metadata = {}) => {
        const sessionId = await sessionManager.createSession(userId, {
          ...metadata,
          ipAddress: getClientIP(req),
          userAgent: req.headers['user-agent']
        });
        
        const cookieOptions = sessionManager.getCookieOptions(
          req.headers['x-forwarded-proto'] === 'https'
        );
        
        res.setHeader('Set-Cookie', [
          `${sessionManager.cookieName}=${sessionId}; ${formatCookieOptions(cookieOptions)}`
        ]);
        
        return sessionId;
      };
      
      res.clearSession = async () => {
        if (req.session && sessionId) {
          await sessionManager.destroySession(sessionId);
        }
        
        res.setHeader('Set-Cookie', [
          `${sessionManager.cookieName}=; Path=/; HttpOnly; Max-Age=0`
        ]);
      };
      
      return await handler(req, res);
    } catch (error) {
      console.error('Session middleware error:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  };
}

// Require authentication
export function requireAuth(handler) {
  return withSession(async (req, res) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    return await handler(req, res);
  });
}

// Require admin privileges
export function requireAdmin(handler) {
  return requireAuth(async (req, res) => {
    if (!req.user.is_admin) {
      return res.status(403).json({ error: 'Admin privileges required' });
    }
    
    return await handler(req, res);
  });
}

// Helper functions
function parseCookies(cookieHeader) {
  const cookies = {};
  cookieHeader.split(';').forEach(cookie => {
    const [name, value] = cookie.trim().split('=');
    if (name && value) {
      cookies[name] = decodeURIComponent(value);
    }
  });
  return cookies;
}

function formatCookieOptions(options) {
  const parts = [];
  
  if (options.path) parts.push(`Path=${options.path}`);
  if (options.domain) parts.push(`Domain=${options.domain}`);
  if (options.maxAge) parts.push(`Max-Age=${Math.floor(options.maxAge / 1000)}`);
  if (options.expires) parts.push(`Expires=${options.expires.toUTCString()}`);
  if (options.httpOnly) parts.push('HttpOnly');
  if (options.secure) parts.push('Secure');
  if (options.sameSite) parts.push(`SameSite=${options.sameSite}`);
  
  return parts.join('; ');
}

function getClientIP(req) {
  return req.headers['x-forwarded-for']?.split(',')[0]?.trim() ||
         req.headers['x-real-ip'] ||
         req.connection?.remoteAddress ||
         '127.0.0.1';
}
```

### 6. API Endpoints

```javascript
// api/endpoints/auth/login.js
import { withSession } from '../../middleware/session.js';
import { User } from '../../models/user.js';
import { validate } from '../../utils/validation.js';

const loginSchema = {
  email: {
    required: true,
    type: 'email',
    maxLength: 255
  },
  password: {
    required: true,
    type: 'string',
    minLength: 8
  }
};

async function loginHandler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    // Validate input
    const validation = validate(req.body, loginSchema);
    if (!validation.isValid) {
      return res.status(400).json({
        error: 'Validation failed',
        details: validation.errors
      });
    }
    
    const { email, password } = req.body;
    
    // Find user
    const user = await User.findByEmail(email);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Verify password
    const isValidPassword = await user.verifyPassword(password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Create session
    await res.setSession(user.id, {
      loginMethod: 'email',
      loginTime: new Date().toISOString()
    });
    
    return res.status(200).json({
      success: true,
      user: user.toJSON()
    });
    
  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}

export default withSession(loginHandler);
```

### 7. Database Testing

```javascript
// tests/integration/database.test.js
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { query, transaction, healthCheck } from '../../api/lib/db.js';
import { kvClient } from '../../api/lib/kv.js';
import { sessionManager } from '../../api/lib/session.js';
import { User } from '../../api/models/user.js';

describe('Database Integration', () => {
  beforeEach(async () => {
    // Clean test data
    await query('DELETE FROM users WHERE email LIKE %test%');
    await query('DELETE FROM user_sessions WHERE session_key LIKE test_%');
  });
  
  describe('Postgres Connection', () => {
    it('should connect to database successfully', async () => {
      const health = await healthCheck();
      expect(health.status).toBe('healthy');
      expect(health.timestamp).toBeDefined();
    });
    
    it('should execute queries with parameters', async () => {
      const result = await query(
        'SELECT $1::text as message, $2::int as number',
        ['Hello World', 42]
      );
      
      expect(result.rows).toHaveLength(1);
      expect(result.rows[0].message).toBe('Hello World');
      expect(result.rows[0].number).toBe(42);
    });
    
    it('should handle transactions correctly', async () => {
      const testEmail = 'transaction-test@example.com';
      
      try {
        await transaction(async (client) => {
          await client.query(
            `INSERT INTO users (email, password_hash, first_name, last_name) 
             VALUES ($1, $2, $3, $4)`,
            [testEmail, 'hash', 'Test', 'User']
          );
          
          throw new Error('Rollback test');
        });
      } catch (error) {
        expect(error.message).toBe('Rollback test');
      }
      
      // Verify rollback worked
      const result = await query('SELECT * FROM users WHERE email = $1', [testEmail]);
      expect(result.rows).toHaveLength(0);
    });
  });
  
  describe('KV Store Operations', () => {
    it('should store and retrieve data', async () => {
      const key = 'test-key';
      const value = { message: 'Hello KV', timestamp: Date.now() };
      
      await kvClient.set(key, value, 60);
      const retrieved = await kvClient.get(key);
      
      expect(retrieved).toEqual(value);
    });
    
    it('should handle TTL expiration', async () => {
      const key = 'ttl-test';
      const value = { data: 'expires soon' };
      
      await kvClient.set(key, value, 1); // 1 second TTL
      
      // Should exist immediately
      let retrieved = await kvClient.get(key);
      expect(retrieved).toEqual(value);
      
      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 1100));
      
      // Should be expired
      retrieved = await kvClient.get(key);
      expect(retrieved).toBeNull();
    });
  });
  
  describe('Session Management', () => {
    it('should create and retrieve sessions', async () => {
      const userId = 'test-user-id';
      const metadata = { test: true };
      
      const sessionId = await sessionManager.createSession(userId, metadata);
      expect(sessionId).toBeDefined();
      expect(sessionId).toHaveLength(64); // 32 bytes hex
      
      const sessionData = await sessionManager.getSession(sessionId);
      expect(sessionData.userId).toBe(userId);
      expect(sessionData.metadata).toEqual(metadata);
      expect(sessionData.createdAt).toBeDefined();
    });
    
    it('should update session data', async () => {
      const sessionId = await sessionManager.createSession('user-1', { initial: true });
      
      const updatedData = await sessionManager.updateSession(sessionId, {
        updated: true,
        newField: 'value'
      });
      
      expect(updatedData.updated).toBe(true);
      expect(updatedData.newField).toBe('value');
      expect(updatedData.initial).toBe(true); // Should preserve existing data
    });
    
    it('should destroy sessions', async () => {
      const sessionId = await sessionManager.createSession('user-2');
      
      // Should exist
      let sessionData = await sessionManager.getSession(sessionId);
      expect(sessionData).toBeDefined();
      
      // Destroy
      const destroyed = await sessionManager.destroySession(sessionId);
      expect(destroyed).toBe(true);
      
      // Should no longer exist
      sessionData = await sessionManager.getSession(sessionId);
      expect(sessionData).toBeNull();
    });
  });
  
  describe('User Model', () => {
    it('should create users with validation', async () => {
      const userData = {
        email: 'test-user@example.com',
        password: 'securePassword123',
        firstName: 'Test',
        lastName: 'User',
        phone: '+1234567890',
        experienceLevel: 'beginner'
      };
      
      const user = await User.create(userData);
      
      expect(user.id).toBeDefined();
      expect(user.email).toBe(userData.email.toLowerCase());
      expect(user.first_name).toBe(userData.firstName);
      expect(user.password_hash).not.toBe(userData.password); // Should be hashed
    });
    
    it('should prevent duplicate email registration', async () => {
      const userData = {
        email: 'duplicate@example.com',
        password: 'password123',
        firstName: 'First',
        lastName: 'User'
      };
      
      await User.create(userData);
      
      await expect(User.create(userData)).rejects.toThrow(
        'User with this email already exists'
      );
    });
    
    it('should authenticate users correctly', async () => {
      const userData = {
        email: 'auth-test@example.com',
        password: 'testPassword123',
        firstName: 'Auth',
        lastName: 'Test'
      };
      
      const user = await User.create(userData);
      
      // Valid password
      const isValid = await user.verifyPassword('testPassword123');
      expect(isValid).toBe(true);
      
      // Invalid password
      const isInvalid = await user.verifyPassword('wrongPassword');
      expect(isInvalid).toBe(false);
    });
  });
});
```

## Completion Checklist

### Database Setup
- [ ] Vercel Postgres connection with pooling
- [ ] Vercel KV (Redis) connection and wrapper
- [ ] Connection health checks and monitoring
- [ ] Graceful connection handling and cleanup
- [ ] Environment variable configuration

### Schema and Migrations
- [ ] Initial schema with users and sessions
- [ ] Class types and instructor tables
- [ ] Booking and payment tables
- [ ] Proper indexes for performance
- [ ] Foreign key constraints and validation

### Session Management
- [ ] Secure session ID generation
- [ ] KV-first with Postgres fallback storage
- [ ] Session TTL and automatic cleanup
- [ ] Session metadata tracking
- [ ] Cookie-based session handling

### Data Models
- [ ] User model with authentication
- [ ] Password hashing with bcrypt
- [ ] Input validation and sanitization
- [ ] Soft delete functionality
- [ ] JSON serialization for API responses

### API Infrastructure
- [ ] Session middleware for request handling
- [ ] Authentication and authorization middleware
- [ ] Error handling and logging
- [ ] Rate limiting and security headers
- [ ] CORS configuration

### Testing Coverage
- [ ] Database connection tests
- [ ] KV store operation tests
- [ ] Session management tests
- [ ] User model tests
- [ ] API endpoint integration tests

### Security Implementation
- [ ] Password hashing with salt rounds
- [ ] Secure session ID generation
- [ ] SQL injection prevention
- [ ] Input validation and sanitization
- [ ] Secure cookie configuration

### Performance Optimization
- [ ] Connection pooling configuration
- [ ] Query optimization with indexes
- [ ] KV caching strategy
- [ ] Session cleanup automation
- [ ] Query performance monitoring

## Environment Variables

```bash
# .env.example
# Database Configuration
POSTGRES_URL=postgresql://user:password@host:5432/database
POSTGRES_URL_NON_POOLING=postgresql://user:password@host:5432/database

# Redis/KV Configuration
KV_URL=redis://localhost:6379
KV_REST_API_URL=https://your-kv-instance.vercel-storage.com
KV_REST_API_TOKEN=your-kv-token

# Security
SESSION_SECRET=your-super-secret-session-key
ENCRYPTION_KEY=32-character-encryption-key

# Email Configuration (for future use)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Environment
NODE_ENV=development
```

## Performance Targets

- **Database Query Response**: < 50ms for 95th percentile
- **Session Lookup**: < 10ms from KV store
- **User Authentication**: < 200ms end-to-end
- **Connection Pool**: Max 20 connections, < 2s timeout
- **KV Cache Hit Ratio**: > 90% for session data
- **Database Health Check**: < 100ms response time

## Security Considerations

- All passwords hashed with bcrypt (12 rounds)
- Session IDs generated with crypto.randomBytes
- SQL injection prevention with parameterized queries
- XSS protection through input sanitization
- CSRF protection with secure cookies
- Rate limiting on authentication endpoints

## Next Steps

After PR approval and merge:
1. Advanced caching strategies implementation
2. Real-time features with WebSocket support
3. Payment processing integration
4. Email notification system
5. Advanced analytics and reporting
6. Phase 2 feature implementation planning