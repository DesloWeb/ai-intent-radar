SECRET_KEY :: 453a9a971ecba1285f59aafee03026634187fbe56040e2f6c1279fed3b4666b7

JWT_SECRET_KEY. :: 64d4f6a6d6da06ba96123d4bc219bc92d7713648e835fb4059a20df2d91c947b

neon connection string: postgresql+asyncpg://neondb_owner:npg_6LUvJ5XKEakA@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

redis url: redis://default:gQAAAAAAAkfUAAIgcDI2ZGRiODBhOTkzZDM0ODdhODEwOWE2OGM3YzVlMmQzOQ@coherent-amoeba-149460.upstash.io:6379

postgresql://neondb_owner:npg_Qoa6dNgcK2Hv@ep-delicate-sky-a5oxiayn-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

token 
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwOTQ4MWU2ZS0yYjQ2LTRmOTUtYjg1NS1lOWYxNzQ2ZTVmMzYiLCJyb2xlIjoiYWRtaW4iLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg4NTQxNjE0fQ.sl9-Z9_YDbWqmMmOs3EiBV8RS87vS8H7IWcwqJaTXxM","refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwOTQ4MWU2ZS0yYjQ2LTRmOTUtYjg1NS1lOWYxNzQ2ZTVmMzYiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc5MTEzMDAxNH0.B3yMBeoasHTQuuZFBtHgy5f4GPMaIRISAt0rnNp_uR4

email":"test3@test.com","password":"testpass123"

The app is fully deployed and secured. Here's where everything stands:

Live URLs:

Frontend: https://ai-intent-radar.vercel.app
Backend API: https://ai-intent-radar.onrender.com
API docs: https://ai-intent-radar.onrender.com/docs
To keep data fresh (run whenever you want new opportunities):
RESPONSE=$(curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/auth/login" -H "Content-Type: application/json" -d '{"email":"test3@test.com","password":"testpass123"}')
TOKEN=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/signals/ingest/hn?limit_stories=50&limit_comments=50" -H "Authorization: Bearer $TOKEN"
curl -s -X POST "https://ai-intent-radar.onrender.com/api/v1/signals/process?limit=100" -H "Authorization: Bearer $TOKEN"
hi 