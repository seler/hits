runapi:
	uvicorn api:app --reload

runworker:
	python worker.py
