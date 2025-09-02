#!/bin/bash
# Deployment script for Digital Ocean server
# IPv4: 164.92.177.11
# IPv6: 2a03:b0c0:3:f0:0:1:3d40:8000

SERVER_IP="164.92.177.11"
SERVER_PASSWORD="6737d0753a63dac96bc5f2ce9a"
BACKEND_DIR="/srv/qvantify-backend"
FRONTEND_DIR="/srv/qvantify-frontend"

echo "=== Deploying to Digital Ocean Server ==="
echo "Server: $SERVER_IP"
echo "IPv6: 2a03:b0c0:3:f0:0:1:3d40:8000"

# Deploy backend files
echo "📦 Deploying backend..."
rsync -avz --progress \
    --exclude __pycache__ \
    --exclude "*.pyc" \
    --exclude ".git" \
    --exclude "deploy-to-do.sh" \
    . root@$SERVER_IP:$BACKEND_DIR/

# Deploy frontend build
echo "📦 Deploying frontend..."
rsync -avz --progress \
    "../qvantify front/qvantify/web-build/" \
    root@$SERVER_IP:$FRONTEND_DIR/

# Configure server
echo "⚙️ Configuring server..."
ssh root@$SERVER_IP << 'EOF'

# Install dependencies
apt-get update
apt-get install -y python3-pip python3-venv nginx

# Setup backend
cd /srv/qvantify-backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn psycopg2-binary openai pgvector

# Create systemd service
cat > /etc/systemd/system/qvantify-backend.service << 'SERVICE'
[Unit]
Description=Qvantify Backend API
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/srv/qvantify-backend
Environment="PATH=/srv/qvantify-backend/.venv/bin"
ExecStart=/srv/qvantify-backend/.venv/bin/gunicorn -w 2 -b 127.0.0.1:8001 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

# Configure Nginx
cat > /etc/nginx/sites-available/qvantify << 'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name _;

    # Self-signed certificate
    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    client_max_body_size 20m;

    root /srv/qvantify-frontend;
    index index.html;

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Host $host;
    }

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
NGINX

# Create SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Qvantify/CN=164.92.177.11"

# Enable site
ln -sf /etc/nginx/sites-available/qvantify /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Start services
systemctl daemon-reload
systemctl enable qvantify-backend
systemctl start qvantify-backend
nginx -t && systemctl restart nginx

# Test deployment
echo ""
echo "=== Testing Deployment ==="
sleep 3

echo "Backend status:"
systemctl status qvantify-backend --no-pager -l

echo ""
echo "Testing backend directly:"
curl -s http://127.0.0.1:8001/project/ -H "projectId: ea762c3e-8dc1-4ec9-a33b-9581d6b69f77" | head -c 100

echo ""
echo "Testing via nginx:"
curl -sk https://localhost/api/project/ -H "projectId: ea762c3e-8dc1-4ec9-a33b-9581d6b69f77" | head -c 100

echo ""
echo "=== Deployment Complete ==="
echo "IPv4: https://164.92.177.11"
echo "IPv6: https://[2a03:b0c0:3:f0:0:1:3d40:8000]"

EOF

echo "🎉 Deployment script completed!"
echo ""
echo "Your app is now available at:"
echo "IPv4: https://164.92.177.11"
echo "IPv6: https://[2a03:b0c0:3:f0:0:1:3d40:8000]"
