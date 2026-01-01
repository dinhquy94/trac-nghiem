# 🚀 Hướng dẫn Triển khai (Deployment)

## Yêu cầu

- **Docker**: v20.10+
- **Docker Compose**: v1.29+
- **Dung lượng**: Tối thiểu 2GB RAM, 10GB disk

## 1️⃣ Chuẩn bị

### Sao chép repository
```bash
git clone https://github.com/yourusername/de_thi_ai.git
cd de_thi_ai
```

### Cấu hình biến môi trường
```bash
# Copy file cấu hình
cp .env.production .env

# Chỉnh sửa với các giá trị thực tế
nano .env
```

**Các biến cần cập nhật:**
- `FLASK_SECRET_KEY`: Tạo khóa bảo mật mới
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- `MONGO_ROOT_PASSWORD`: Mật khẩu MongoDB
- `GEMINI_API_KEY`: API key từ [Google AI](https://ai.google.dev)

## 2️⃣ Triển khai với Docker Compose

### Khởi động ứng dụng
```bash
docker-compose up -d
```

### Kiểm tra status
```bash
docker-compose ps
docker-compose logs -f web
```

### Dừng ứng dụng
```bash
docker-compose down
```

### Xóa dữ liệu (cảnh báo!)
```bash
docker-compose down -v
```

## 3️⃣ Cấu hình SSL/TLS (HTTPS)

### Tạo chứng chỉ tự ký (Development)
```bash
mkdir -p certs

openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem -keyout certs/key.pem -days 365 \
  -subj "/CN=localhost"
```

### Sử dụng Let's Encrypt (Production)
```bash
# Cài đặt Certbot
sudo apt-get install certbot python3-certbot-nginx

# Tạo certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy vào thư mục certs
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem certs/key.pem
```

## 4️⃣ Quản lý Database

### Truy cập MongoDB
```bash
docker-compose exec mongodb mongosh \
  -u admin -p your-password \
  --authenticationDatabase admin \
  exam_system
```

### Backup Database
```bash
docker-compose exec mongodb mongodump \
  -u admin -p your-password \
  --authenticationDatabase admin \
  --out /backup
```

### Restore Database
```bash
docker-compose exec mongodb mongorestore \
  -u admin -p your-password \
  --authenticationDatabase admin \
  /backup
```

## 5️⃣ Logs & Monitoring

### Xem logs ứng dụng
```bash
docker-compose logs -f web
```

### Xem logs MongoDB
```bash
docker-compose logs -f mongodb
```

### Xem logs Nginx
```bash
docker-compose logs -f nginx
```

## 6️⃣ Scaling & Performance

### Tăng workers
Cập nhật `docker-compose.yml`:
```yaml
web:
  # Hoặc sử dụng environment variables
  environment:
    - WORKERS=8
```

Sau đó restart:
```bash
docker-compose up -d web
```

### Resource limits
```yaml
web:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 512M
```

## 7️⃣ Backup & Restore

### Backup uploads
```bash
tar -czf uploads_backup.tar.gz uploads/
```

### Restore uploads
```bash
tar -xzf uploads_backup.tar.gz
```

### Backup tất cả
```bash
docker-compose exec -T mongodb mongodump \
  -u admin -p your-password \
  --authenticationDatabase admin \
  --out /dump

docker cp exam_mongodb:/dump ./mongodb_backup
tar -czf full_backup.tar.gz mongodb_backup uploads/
```

## 8️⃣ Troubleshooting

### Port đang được sử dụng
```bash
# Thay đổi port trong docker-compose.yml
# Hoặc dừng process khác
lsof -i :8000
kill -9 <PID>
```

### MongoDB không kết nối
```bash
docker-compose logs mongodb
docker-compose restart mongodb
```

### Lỗi permission uploads
```bash
docker-compose exec web chmod -R 755 uploads
```

### Xóa cache Docker
```bash
docker-compose down
docker system prune -a
docker volume prune
docker-compose up -d
```

## 9️⃣ Cấu hình Reverse Proxy (Optional)

### Apache
```apache
<VirtualHost *:80>
    ServerName example.com
    ProxyPreserveHost On
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
</VirtualHost>
```

### Nginx (Standalone)
```nginx
upstream exam_app {
    server localhost:8000;
}

server {
    listen 80;
    server_name example.com;
    
    client_max_body_size 16M;
    
    location / {
        proxy_pass http://exam_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🔟 Health Check

### Kiểm tra API
```bash
curl http://localhost:8000/
curl http://localhost:8000/auth/login
```

### Kiểm tra Database
```bash
docker-compose exec web python -c "
from app import create_app
app = create_app('production')
with app.app_context():
    from models.user import User
    users = User.find_by_username(app.db, 'admin')
    print('✅ Database connection OK')
"
```

## 📝 Cấu trúc File

```
de_thi_ai/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Services orchestration
├── nginx.conf                 # Nginx configuration
├── .dockerignore              # Files to ignore in Docker
├── .env.production            # Production environment
├── app.py                     # Flask application
├── config.py                  # Configuration
├── requirements.txt           # Python dependencies
├── routes/                    # Flask blueprints
├── models/                    # Database models
├── templates/                 # Jinja2 templates
├── utils/                     # Utilities
├── uploads/                   # User uploads (volume)
├── certs/                     # SSL certificates
└── logs/                      # Application logs
```

## ✅ Kiểm tra Sau Deployment

- [ ] Ứng dụng chạy trên port 8000
- [ ] MongoDB kết nối thành công
- [ ] Có thể đăng nhập
- [ ] Có thể upload ảnh đại diện
- [ ] Có thể tạo đề thi
- [ ] PDF export hoạt động
- [ ] Nginx reverse proxy chạy (tùy chọn)

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs: `docker-compose logs -f`
2. Restart services: `docker-compose restart`
3. Rebuild images: `docker-compose down && docker-compose up -d --build`
