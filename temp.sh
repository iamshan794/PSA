#!/bin/bash 

curl -X POST http://localhost:8000/apps/multi_tool_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"key1": "value1", "key2": 42}}'

  curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"appName": "multi_tool_agent",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'