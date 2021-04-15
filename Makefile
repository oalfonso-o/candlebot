back:
	uvicorn candlebot.api:app --reload --port 12345

front:
	export FLASK_APP=candlefront.app:app && export FLASK_ENV=development && flask run