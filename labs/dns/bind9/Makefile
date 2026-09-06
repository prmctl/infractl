.PHONY: up down verify status logs shell break-primary break-network recover clean

up:
	docker compose up -d

down:
	docker compose down

verify:
	./scripts/verify.sh

status:
	docker compose ps

logs:
	docker compose logs --tail=120 dns-primary dns-secondary

shell:
	docker compose exec client sh

break-primary:
	./scripts/break-primary.sh

break-network:
	./scripts/break-network.sh

recover:
	./scripts/recover.sh

clean:
	docker compose down -v --remove-orphans
