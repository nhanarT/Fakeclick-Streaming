up:
	docker compose up --build -d

down:
	docker compose down

run-checkout-attribution-job:
	docker exec jobmanager ./bin/flink run --python ./code/checkout_attribution.py

sleep:
	sleep 20 

run: down up sleep run-checkout-attribution-job
