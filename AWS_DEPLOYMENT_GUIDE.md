# AWS Deployment Guide - BOSS Voice Assistant

This guide provides step-by-step instructions to deploy the BOSS voice assistant on AWS using EC2 (Ubuntu) and RDS (PostgreSQL).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Infrastructure Setup](#aws-infrastructure-setup)
3. [EC2 Configuration](#ec2-configuration)
4. [Database Setup](#database-setup)
5. [Application Deployment](#application-deployment)
6. [Production Setup](#production-setup)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Prerequisites

- AWS Account with billing enabled
- SSH client (built-in on macOS/Linux, PuTTY on Windows)
- Git installed locally
- Basic familiarity with Linux commands

---

## AWS Infrastructure Setup

### Step 1: Launch EC2 Instance

1. **Log in to AWS Console** → `https://console.aws.amazon.com`

2. **Navigate to EC2** → Click "Instances" → "Launch Instance"

3. **Configure Instance:**
   - **Name**: `boss-assistant-server`
   - **OS**: Ubuntu Server 22.04 LTS (Free Tier eligible)
   - **Instance Type**: `t2.medium` (or t2.small for testing)
   - **Key Pair**: Create new → Download as `.pem` file
   - **Storage**: 30GB gp3
   - **Security Group**: Create new with these rules:
     ```
     Type             Protocol  Port    Source
     SSH              TCP       22      0.0.0.0/0 (restrict to your IP)
     HTTP             TCP       80      0.0.0.0/0
     HTTPS            TCP       443     0.0.0.0/0
     Custom TCP       TCP       5000    0.0.0.0/0
     ```

4. **Launch Instance** and wait for "Running" status

### Step 2: Launch RDS Database

1. **Navigate to RDS** → "Databases" → "Create Database"

2. **Configure Database:**
   - **Engine**: PostgreSQL
   - **Version**: 14+ (or latest)
   - **Templates**: Free tier
   - **DB Instance Identifier**: `boss-assistant-db`
   - **Master Username**: `admin`
   - **Master Password**: Strong password (save it!)
   - **Storage**: 20GB gp2
   - **Public Accessibility**: Yes
   - **Initial Database Name**: `boss_db`

3. **Create Database** and wait for "Available" status

4. **Get RDS Endpoint:**
   - Click database name → Copy endpoint (e.g., `boss-assistant-db.xxxx.us-east-1.rds.amazonaws.com`)

---

## EC2 Configuration

### Step 3: Connect to EC2 Instance

```bash
# macOS/Linux
chmod 600 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Windows (using PuTTY)
# 1. Convert .pem to .ppk using PuTTYgen
# 2. Open PuTTY → Load .ppk file → Connect
```

### Step 4: Update System & Install Dependencies

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git curl wget ffmpeg
sudo apt install -y libpq-dev libssl-dev
sudo apt install -y build-essential

# Verify Python installation
python3 --version
pip3 --version
```

### Step 5: Clone Repository & Setup Project

```bash
# Navigate to home directory
cd ~

# Clone the project
git clone https://github.com/famidha2004/ai_project.git
cd ai_project

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import flask; import psycopg2; print('✅ Dependencies installed')"
```

### Step 6: Configure Environment Variables

```bash
# Create .env file
cp .env.example .env

# Edit .env with your actual values
nano .env

# Add your RDS endpoint and credentials:
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_NAME=boss_db
DB_USER=admin
DB_PASSWORD=your_rds_password
SECRET_KEY=generate-a-random-string-here
DEBUG=False
API_PORT=5000
API_HOST=0.0.0.0

# Save and exit (Ctrl+O, Enter, Ctrl+X)
```

---

## Database Setup

### Step 7: Initialize Database Tables

```bash
# Make sure you're in the project directory with venv activated
source ~/ai_project/venv/bin/activate
cd ~/ai_project

# Run database setup script
python setup_db.py

# Expected output: ✅ Database tables created successfully!
```

### Step 8: Test Database Connection

```bash
# Verify connection (install psql if needed)
sudo apt install -y postgresql-client

# Test connection
psql -h your-rds-endpoint.rds.amazonaws.com -U admin -d boss_db -c "SELECT version();"

# You should see the PostgreSQL version
```

---

## Application Deployment

### Step 9: Test Application Locally

```bash
# Activate virtual environment
source ~/ai_project/venv/bin/activate
cd ~/ai_project

# Run Flask development server
python app.py

# Expected output:
# * Running on http://0.0.0.0:5000
# * Debug mode: off

# Test health endpoint (in another terminal)
curl http://localhost:5000/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

### Step 10: Setup Gunicorn WSGI Server

```bash
# Gunicorn should already be installed via requirements.txt
# Test Gunicorn
cd ~/ai_project
source venv/bin/activate

gunicorn -c gunicorn_config.py app:app

# Expected: [xxxx] [INFO] Starting gunicorn 20.1.0
# [xxxx] [INFO] Listening at: http://0.0.0.0:5000

# Press Ctrl+C to stop
```

---

## Production Setup

### Step 11: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/boss-api.service

# Paste this content:
```

```ini
[Unit]
Description=BOSS Voice Assistant API
After=network.target postgresql.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai_project
Environment="PATH=/home/ubuntu/ai_project/venv/bin"
ExecStart=/home/ubuntu/ai_project/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable boss-api

# Start the service
sudo systemctl start boss-api

# Check status
sudo systemctl status boss-api

# Expected: ● boss-api.service - BOSS Voice Assistant API
#           Loaded: loaded
#           Active: active (running)
```

### Step 12: Setup Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/boss-assistant

# Paste this content:
```

```nginx
server {
    listen 80;
    server_name your-ec2-public-ip;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }

    location /static/ {
        alias /home/ubuntu/ai_project/static/;
    }
}
```

```bash
# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Enable the site
sudo ln -s /etc/nginx/sites-available/boss-assistant /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Expected: nginx: configuration file test is successful

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

### Step 13: Test Complete Setup

```bash
# Test health endpoint via Nginx
curl http://your-ec2-public-ip/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}

# Test API endpoints
curl -X POST http://your-ec2-public-ip/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com"}'

# Expected response:
# {"user_id":1,"message":"User created"}
```

---

## Security Hardening (Optional but Recommended)

### Step 14: Setup HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get free SSL certificate (requires a domain name)
sudo certbot certonly --nginx -d your-domain.com

# Update Nginx to use SSL
sudo nano /etc/nginx/sites-available/boss-assistant

# Add after 'listen 80':
# listen 443 ssl http2;
# ssl_certificate /etc/letsencrypt/live/your-domain/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-domain/privkey.pem;

# Add redirect from HTTP to HTTPS:
# server {
#     listen 80;
#     return 301 https://$server_name$request_uri;
# }

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### Step 15: Restrict Security Groups

```bash
# In AWS Console:
# 1. Go to EC2 → Security Groups
# 2. Edit rules:
#    - SSH: Only from your IP (not 0.0.0.0/0)
#    - HTTP/HTTPS: 0.0.0.0/0 (public)
#    - Port 5000: Remove (internal only, via Nginx)
# 3. Save rules
```

---

## Monitoring & Troubleshooting

### View Logs

```bash
# Application logs
sudo journalctl -u boss-api -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo dmesg | tail -20
```

### Common Issues & Solutions

#### Issue: "Connection refused" on port 5000

```bash
# Check if service is running
sudo systemctl status boss-api

# Restart service
sudo systemctl restart boss-api

# Check Nginx is running
sudo systemctl status nginx

# View service logs
sudo journalctl -u boss-api -n 50
```

#### Issue: "Database connection failed"

```bash
# Verify RDS endpoint in .env
cat ~/.env | grep DB_HOST

# Test connection
psql -h your-rds-endpoint -U admin -d boss_db -c "SELECT 1"

# Check RDS security group in AWS Console
# Ensure EC2 security group is allowed
```

#### Issue: Port 80/443 already in use

```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Kill the process
sudo kill -9 <PID>

# Or change Nginx listen port
sudo nano /etc/nginx/sites-available/boss-assistant
# Change: listen 8080; (instead of 80)
```

### Performance Monitoring

```bash
# Check system resources
top

# Check disk space
df -h

# Check memory usage
free -m

# Monitor network
iftop

# Application metrics (via Flask)
curl http://your-ec2-ip/health
```

### Backup Database

```bash
# Backup RDS (via AWS Console)
# 1. RDS → Databases → boss-assistant-db
# 2. Actions → Create Snapshot
# 3. Enter snapshot name

# Or via pg_dump
pg_dump -h your-rds-endpoint -U admin boss_db > backup.sql
```

---

## Deployment Checklist

- [ ] EC2 instance running (Ubuntu 22.04 LTS)
- [ ] RDS database created and accessible
- [ ] Repository cloned on EC2
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured with RDS credentials
- [ ] Database tables initialized
- [ ] Flask app tested locally
- [ ] Gunicorn service created and enabled
- [ ] Nginx configured as reverse proxy
- [ ] Health endpoint responds correctly
- [ ] API endpoints tested
- [ ] Security groups properly configured
- [ ] (Optional) HTTPS/SSL certificate installed
- [ ] Logs being collected and monitored
- [ ] Regular backup schedule set up

---

## Next Steps

1. **Setup Monitoring**: CloudWatch, DataDog, or New Relic
2. **Auto Scaling**: Configure Auto Scaling Group for multiple instances
3. **Load Balancer**: Use AWS ELB for distributed traffic
4. **CI/CD**: GitHub Actions to auto-deploy on push
5. **Analytics**: Track API usage and performance
6. **Alerts**: Setup notifications for errors/downtime

---

## Support

For issues or questions:
1. Check `/var/log/` and systemd journal
2. Review AWS RDS and EC2 console for resource status
3. Test connectivity with curl/psql
4. Check security group rules in AWS Console

---

**Last Updated**: July 2026
