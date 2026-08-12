# GCP Compute Engine Deployment

## Quick Deploy (GCE + Docker)

### 1. Create Instance
```bash
gcloud compute instances create support-bot \
  --machine-type=e2-standard-2 \
  --boot-disk-size=50GB \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server \
  --zone=us-central1-a
```

### 2. Open Ports
```bash
gcloud compute firewall-rules create allow-bot \
  --allow tcp:8000,tcp:80,tcp:443 \
  --target-tags=http-server
```

### 3. Deploy
```bash
gcloud compute ssh support-bot --zone=us-central1-a -- \
  bash -c '
    sudo apt update && sudo apt install -y docker.io docker-compose git
    git clone <repo-url>
    cd ai-customer-support-bot-template
    bash deploy/quick-deploy.sh
  '
```

## Estimated Cost
- e2-standard-2: ~$25/mo
- 50GB PD: ~$4/mo
- **Total: ~$30/mo**
