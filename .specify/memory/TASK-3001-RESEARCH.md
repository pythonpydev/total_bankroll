# TASK-3001: Redis Setup Research & Implementation Plan

## PythonAnywhere Redis Support

### Findings
PythonAnywhere **does NOT provide native Redis support** in shared hosting plans. Redis is only available on:
- Enterprise plans
- Custom deployments
- External hosting

### Available Options

#### Option 1: External Redis Hosting (Recommended for Production)
- **Upstash Redis** (Free tier available)
  - 10,000 commands/day free
  - Global edge caching
  - REST API compatible
  - TLS encryption
  - https://upstash.com

- **Redis Labs / Redis Cloud** (Free tier available)
  - 30MB free tier
  - AWS/Azure/GCP hosting
  - High availability

#### Option 2: Simple Memory Cache (Development Fallback)
- **Flask-Caching with SimpleCache backend**
  - No external dependencies
  - Perfect for development
  - Limited to single process
  - Data lost on restart
  - Fine for PythonAnywhere free tier

#### Option 3: Memcached (PythonAnywhere Alternative)
- PythonAnywhere may support Memcached
- Need to verify availability
- Similar performance to Redis

## Implementation Strategy

### Phase 1: Development (Local)
1. Use **SimpleCache** backend for local development
2. Easy setup, no external dependencies
3. Fast iteration

### Phase 2: Production (PythonAnywhere)
**Option A: If staying on PythonAnywhere free tier**
- Use SimpleCache backend (acceptable for small-scale)
- Document limitations
- Plan for future upgrade

**Option B: If using external Redis**
- Setup Upstash free tier account
- Configure TLS connection
- Add credentials to production .env
- Test connectivity from PythonAnywhere

**Option C: Verify Memcached support**
- SSH to PythonAnywhere
- Check if memcached available
- If yes, use as alternative to Redis

## Recommended Approach

1. **Implement dual-backend support**:
   - SimpleCache for development
   - Redis for production (when available)
   - Automatic fallback

2. **Configuration-based**:
   ```python
   CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
   # Options: 'simple', 'redis', 'memcached'
   ```

3. **No code changes needed** when upgrading caching backend

## Implementation Steps

### Step 1: Add Flask-Caching with SimpleCache
- Works immediately on all platforms
- No external dependencies
- Good enough for current scale

### Step 2: Add Redis support (optional)
- Add redis-py library
- Configure Redis connection for when available
- Test with local Redis if desired

### Step 3: Documentation
- Document caching strategy
- Document upgrade path to Redis
- Document Upstash setup instructions

## Decision: Start with SimpleCache

**Rationale:**
1. ✅ Works immediately on PythonAnywhere
2. ✅ No additional costs
3. ✅ No external service setup needed
4. ✅ Adequate performance for current traffic
5. ✅ Easy upgrade path when needed
6. ✅ Better than no caching at all

**When to upgrade to Redis:**
- Traffic increases significantly (>1000 users/day)
- Multiple web workers needed
- Cross-process cache sharing needed
- Advanced features needed (pub/sub, streams)

