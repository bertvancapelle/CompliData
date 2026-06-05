#!/usr/bin/env bash
# CompliData smoke test — minimale operationele controle.
# Verwacht een draaiende API op localhost:8000.
set -u

API="${API_URL:-http://localhost:8000}"
PASS=0
FAIL=0

check() {
  local naam="$1" verwacht="$2" gekregen="$3"
  if [ "$gekregen" = "$verwacht" ]; then
    echo "  PASS — $naam"
    PASS=$((PASS + 1))
  else
    echo "  FAIL — $naam (verwacht '$verwacht', kreeg '$gekregen')"
    FAIL=$((FAIL + 1))
  fi
}

echo "CompliData smoke test — API: $API"

# 1. Health endpoint bereikbaar + status ok
code=$(curl -s -o /tmp/cd_health.json -w "%{http_code}" "$API/api/v1/health" 2>/dev/null || echo "000")
check "GET /api/v1/health → HTTP 200" "200" "$code"

status=$(python3 -c "import json,sys; print(json.load(open('/tmp/cd_health.json')).get('status',''))" 2>/dev/null || echo "")
check "health.status == ok" "ok" "$status"

db=$(python3 -c "import json,sys; print(json.load(open('/tmp/cd_health.json')).get('db',''))" 2>/dev/null || echo "")
check "health.db == ok" "ok" "$db"

# 2. /auth/me zonder sessie → 401
code=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/auth/me" 2>/dev/null || echo "000")
check "GET /api/v1/auth/me zonder sessie → HTTP 401" "401" "$code"

echo ""
echo "Resultaat: $PASS geslaagd, $FAIL mislukt"
[ "$FAIL" -eq 0 ]
