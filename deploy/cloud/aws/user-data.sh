#!/bin/bash
# AWS EC2 user-data script — auto-installs Docker and deploys the bot

set -eux

apt-get update
apt-get install -y docker.io docker-compose git curl

usermod -aG docker ubuntu

git clone <REPO_URL> /home/ubuntu/ai-customer-support-bot
cd /home/ubuntu/ai-customer-support-bot
cp .env.example .env

cd deploy/docker
docker compose up -d

echo "✅ Bot deployed. Access at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/chat"
