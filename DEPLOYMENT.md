# Deployment Guide

This guide covers deploying the Kassa AI Bot to various platforms.

## Prerequisites

- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key
- Server with public IP (for webhook)

## Environment Setup

### 1. Server Requirements

**Minimum:**
- 1 CPU core
- 512MB RAM
- 1GB storage
- Ubuntu 20.04+ or similar

**Recommended:**
- 2 CPU cores
- 1GB RAM
- 5GB storage
- Ubuntu 22.04 LTS

### 2. System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install additional dependencies
sudo apt install git nginx supervisor -y
```

## Deployment Methods

### Method 1: Direct Server Deployment

#### 1. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/Muhammaddiyor2010/Kassa_origin.git
sudo chown -R $USER:$USER Kassa_origin
cd Kassa_origin
```

#### 2. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/production.txt
```

#### 3. Configure Environment

```bash
# Create environment file
cat > .env << EOF
BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_PATH=/webhook
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=8080
MAIN_ADMIN_ID=7231910736
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF
```

#### 4. Setup Nginx (Reverse Proxy)

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/kassa-bot << EOF
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/kassa-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Setup SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 6. Setup Supervisor

```bash
# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/kassa-bot.conf << EOF
[program:kassa-bot]
command=/opt/Kassa_origin/venv/bin/python webhook_server.py
directory=/opt/Kassa_origin
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/kassa-bot.log
environment=BOT_TOKEN="your_bot_token_here",GEMINI_API_KEY="your_gemini_api_key_here",WEBHOOK_URL="https://yourdomain.com"
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start kassa-bot
```

### Method 2: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "webhook_server.py"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  kassa-bot:
    build: .
    ports:
      - "8080:8080"
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - MAIN_ADMIN_ID=7231910736
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - kassa-bot
    restart: unless-stopped
```

#### 3. Deploy with Docker

```bash
# Create environment file
cat > .env << EOF
BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
WEBHOOK_URL=https://yourdomain.com
EOF

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f kassa-bot
```

### Method 3: Cloud Platform Deployment

#### Heroku

1. Create `Procfile`:
```
web: python webhook_server.py
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set BOT_TOKEN=your_token
heroku config:set GEMINI_API_KEY=your_key
heroku config:set WEBHOOK_URL=https://your-app-name.herokuapp.com
git push heroku main
```

#### Railway

1. Connect GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically

#### DigitalOcean App Platform

1. Create new app from GitHub
2. Configure environment variables
3. Set build command: `pip install -r requirements/production.txt`
4. Set run command: `python webhook_server.py`

## Monitoring and Maintenance

### 1. Health Checks

```bash
# Check bot status
curl https://yourdomain.com/health

# Check statistics
curl https://yourdomain.com/stats
```

### 2. Log Monitoring

```bash
# View logs
tail -f /var/log/kassa-bot.log

# Check supervisor status
sudo supervisorctl status kassa-bot
```

### 3. Database Backup

```bash
# Create backup script
cat > backup.sh << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
cp /opt/Kassa_origin/main.db /opt/backups/main_${DATE}.db
find /opt/backups -name "main_*.db" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/Kassa_origin/backup.sh
```

### 4. Updates

```bash
# Update bot
cd /opt/Kassa_origin
git pull origin main
source venv/bin/activate
pip install -r requirements/production.txt
sudo supervisorctl restart kassa-bot
```

## Troubleshooting

### Common Issues

1. **Bot not responding:**
   - Check webhook URL
   - Verify bot token
   - Check logs for errors

2. **Database errors:**
   - Ensure database file permissions
   - Check disk space
   - Verify database schema

3. **Memory issues:**
   - Monitor memory usage
   - Restart bot periodically
   - Optimize database queries

### Debug Commands

```bash
# Check bot status
sudo supervisorctl status kassa-bot

# View recent logs
sudo journalctl -u kassa-bot -f

# Test webhook
curl -X POST https://yourdomain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id": 1, "message": {"message_id": 1, "from": {"id": 123}, "chat": {"id": 123}, "text": "/start"}}'
```

## Security Considerations

1. **Environment Variables:**
   - Never commit .env files
   - Use strong, unique tokens
   - Rotate tokens regularly

2. **Server Security:**
   - Keep system updated
   - Use firewall (ufw)
   - Disable root login
   - Use SSH keys

3. **Bot Security:**
   - Validate all inputs
   - Rate limit requests
   - Monitor for abuse
   - Regular backups

## Performance Optimization

1. **Database:**
   - Use connection pooling
   - Index frequently queried columns
   - Regular VACUUM (SQLite)

2. **Memory:**
   - Monitor memory usage
   - Implement caching
   - Optimize image processing

3. **Network:**
   - Use CDN for static files
   - Compress responses
   - Optimize webhook handling
