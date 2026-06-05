.PHONY: build up down logs install uninstall clean

help:
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start generators in background"
	@echo "  make down       - Stop generators"
	@echo "  make logs       - View logs"
	@echo "  make clean      - Remove containers, images and temp files"
	@echo "  make install    - Install as systemd service (requires sudo)"
	@echo "  make uninstall  - Remove systemd service (requires sudo)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

install:
	@echo "Building Docker images (this may take a while on first run)..."
	@docker compose build
	@echo "Installing systemd service..."
	@sed "s|WorkingDirectory=.*|WorkingDirectory=$(CURDIR)|" deploy/traffic-noise.service | sudo tee /etc/systemd/system/traffic-noise.service > /dev/null
	@sudo systemctl daemon-reload
	@sudo systemctl enable traffic-noise
	@sudo systemctl start traffic-noise
	@echo "Service installed and started!"

uninstall:
	@echo "Removing service..."
	@sudo systemctl stop traffic-noise || true
	@sudo systemctl disable traffic-noise || true
	@sudo rm /etc/systemd/system/traffic-noise.service || true
	@sudo systemctl daemon-reload
	@echo "Service removed."

clean:
	@echo "Cleaning up..."
	docker compose down --rmi all --volumes --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f deploy/*.tmp
	@echo "All clean!"
