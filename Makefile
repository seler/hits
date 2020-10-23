runapi:
	uvicorn api:app --reload

runworker:
	python worker.py --verbose --destination ./destination

download:
	http localhost:8000 url=https://www.youtube.com/watch?v=1Uz9NqDV5ZMschedule
