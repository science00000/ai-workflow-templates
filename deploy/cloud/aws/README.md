# AWS EC2 Deployment Guide

## Quick Deploy (EC2 + Docker)

### 1. Launch EC2 Instance
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f6 \
  --instance-type t3.large \
  --key-name your-key \
  --security-group-ids sg-your-sg \
  --user-data file://deploy/cloud/aws/user-data.sh
```

**Minimum specs:** t3.large (2 vCPU, 8GB RAM)

### 2. Connect & Deploy
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo apt update && sudo apt install -y docker.io docker-compose git
git clone <repo-url>
cd ai-customer-support-bot-template
bash deploy/quick-deploy.sh
```

### 3. Setup Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name support.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 4. SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d support.yourdomain.com
```

## Estimated Cost
- t3.large: ~$30/mo
- EBS 50GB: ~$5/mo
- **Total: ~$35/mo**
