SCP_DIR = /usr/local/hoge_board_scraping
PROJECT_ID = hoge-brain-ebis
ZONE = asia-northeast1-b
INSTANCE_NAME = hoge-board-scraping

remote-create-dir:
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) --command "sudo mkdir -p $(SCP_DIR)/logs"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) --command "sudo mkdir -p $(SCP_DIR)/chrome"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) --command "sudo mkdir -p $(SCP_DIR)/cred"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) --command "sudo mkdir -p $(SCP_DIR)/script/images"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) --command "sudo chown -R takahisa $(SCP_DIR)"

remote-set-permission:
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) --command "sudo chmod 666 $(SCP_DIR)/logs/*.log"

# Dockerのインストール
remote-install-docker:
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) \
		--command "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker ${USER}"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) \
		--command "sudo systemctl start docker"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) \
		--command "sudo systemctl enable docker"

# Docker Composeのインストール
remote-install-docker-compose:
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) \
		--command "sudo curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose"
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID) \
		--command "sudo chmod +x /usr/local/bin/docker-compose"

scp-docker-compose:
	gcloud compute scp \
		./docker-compose.yml $(INSTANCE_NAME):$(SCP_DIR) \
		--zone $(ZONE) \
		--project $(PROJECT_ID)

scp-python:
	gcloud compute scp \
		--recurse ./python-selenium/ $(INSTANCE_NAME):$(SCP_DIR) \
		--zone $(ZONE) \
		--project $(PROJECT_ID)

scp-script:
	gcloud compute scp \
        --recurse \
        --recurse ./script/ $(INSTANCE_NAME):$(SCP_DIR) \
        --zone $(ZONE) \
        --project $(PROJECT_ID)

scp-cred:
	gcloud compute scp \
		--recurse ./cred/ $(INSTANCE_NAME):$(SCP_DIR) \
		--zone $(ZONE) \
		--project $(PROJECT_ID)

scp-all: scp-docker-compose scp-python scp-script scp-cred

rebuild-restart-python:
	gcloud compute ssh $(INSTANCE_NAME) \
		--zone $(ZONE) \
		--project $(PROJECT_ID) \
		-- \
		"cd $(SCP_DIR) && \
		docker compose down && \
		docker compose up -d --build python"

ssh:
	gcloud compute ssh $(INSTANCE_NAME) --zone $(ZONE) --project $(PROJECT_ID)