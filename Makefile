api:
	uvicorn candlebot.api:app --reload --port 12345

charts:
	cd web && npm run dev
