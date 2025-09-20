#!/bin/bash

# Email Validation API Test Script

API_URL="http://localhost:8000/auth/check-email"

echo "=== Email Validation API Tests ==="
echo ""

# Test 1: Valid email that's available
echo "Test 1: Valid available email"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"email": "test.user@example.com"}' \
  2>/dev/null | python3 -m json.tool
echo ""

# Test 2: Invalid email format
echo "Test 2: Invalid email format"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-email"}' \
  2>/dev/null | python3 -m json.tool
echo ""

# Test 3: Disposable email
echo "Test 3: Disposable email"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@10minutemail.com"}' \
  2>/dev/null | python3 -m json.tool
echo ""

# Test 4: Empty email
echo "Test 4: Empty email"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"email": ""}' \
  2>/dev/null | python3 -m json.tool
echo ""

# Test 5: Email with special characters
echo "Test 5: Email with special characters"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"email": "test+label@example.co.uk"}' \
  2>/dev/null | python3 -m json.tool
echo ""

echo "=== Tests completed ==="
