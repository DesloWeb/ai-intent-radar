#!/bin/bash
# AI Intent Radar - Production Verification Script
# Run this after deployment to verify everything works

set -e

echo "🔍 AI Intent Radar - Production Verification"
echo "============================================="

API_URL="${1:-http://localhost:8000}"
FRONTEND_URL="${2:-http://localhost:3000}"
TOKEN=""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}✅ $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 1. Health check
echo ""
echo "1️⃣  Health Check"
if curl -s "${API_URL}/health" | grep -q "ok"; then
    pass "GET /health → {\"status\":\"ok\"}"
else
    fail "GET /health failed"
    exit 1
fi

# 2. Register user
echo ""
echo "2️⃣  User Registration"
RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test-verify@example.com","password":"testpass123","full_name":"Verify User"}')
if echo "$RESPONSE" | grep -q "access_token"; then
    pass "POST /api/v1/auth/register → creates user, returns tokens"
    TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
else
    warn "POST /api/v1/auth/register → user may already exist, trying login..."
fi

# 3. Login
echo ""
echo "3️⃣  User Login"
if [ -z "$TOKEN" ]; then
    RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"test-verify@example.com","password":"testpass123"}')
    if echo "$RESPONSE" | grep -q "access_token"; then
        pass "POST /api/v1/auth/login → works with credentials"
        TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    else
        fail "POST /api/v1/auth/login failed"
    fi
else
    pass "POST /api/v1/auth/login → already have token"
fi

# 4. HN dry run
echo ""
echo "4️⃣  HN Signal Ingestion (Dry Run)"
RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/signals/ingest/hn?dry_run=true" \
    -H "Authorization: Bearer ${TOKEN}")
if echo "$RESPONSE" | grep -q "ingested"; then
    pass "POST /api/v1/signals/ingest/hn?dry_run=true → returns ingested count"
else
    warn "POST /api/v1/signals/ingest/hn?dry_run=true → response: $RESPONSE"
fi

# 5. HN real ingest
echo ""
echo "5️⃣  HN Signal Ingestion (Real)"
RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/signals/ingest/hn" \
    -H "Authorization: Bearer ${TOKEN}")
if echo "$RESPONSE" | grep -q "ingested"; then
    pass "POST /api/v1/signals/ingest/hn → ingests real signals"
else
    warn "POST /api/v1/signals/ingest/hn → response: $RESPONSE"
fi

# 6. Process pipeline
echo ""
echo "6️⃣  Pipeline Processing"
RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/signals/process" \
    -H "Authorization: Bearer ${TOKEN}")
if echo "$RESPONSE" | grep -q "processed"; then
    pass "POST /api/v1/signals/process → processes pipeline, creates opportunities"
else
    warn "POST /api/v1/signals/process → response: $RESPONSE"
fi

# 7. Get opportunities
echo ""
echo "7️⃣  Get Opportunities"
RESPONSE=$(curl -s "${API_URL}/api/v1/opportunities" \
    -H "Authorization: Bearer ${TOKEN}")
if echo "$RESPONSE" | grep -q "opportunities"; then
    pass "GET /api/v1/opportunities → returns scored opportunities"
else
    fail "GET /api/v1/opportunities failed"
fi

# 8. Get dashboard
echo ""
echo "8️⃣  Dashboard"
RESPONSE=$(curl -s "${API_URL}/api/v1/dashboard" \
    -H "Authorization: Bearer ${TOKEN}")
if echo "$RESPONSE" | grep -q "total_opportunities"; then
    pass "GET /api/v1/dashboard → returns aggregated stats"
else
    fail "GET /api/v1/dashboard failed"
fi

# 9. Frontend check
echo ""
echo "9️⃣  Frontend"
if curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" | grep -q "200"; then
    pass "Frontend loads at ${FRONTEND_URL}"
else
    warn "Frontend not accessible at ${FRONTEND_URL}"
fi

# 10. Check for localhost references in frontend
echo ""
echo "🔟 Frontend Configuration"
if [ -f "frontend/.env" ] || [ -f "frontend/.env.local" ]; then
    if grep -q "http://localhost" frontend/.env* 2>/dev/null; then
        warn "Frontend .env contains localhost references - update for production"
    else
        pass "Frontend .env has no localhost references"
    fi
else
    warn "No frontend .env file found"
fi

echo ""
echo "============================================="
echo "✅ Verification Complete"
echo "============================================="
