# 📚 Hệ thống Thi Trực tuyến với AI

Hệ thống quản lý đề thi và thi trực tuyến với khả năng tạo câu hỏi tự động bằng AI (Google Gemini), được thiết kế dành cho học sinh THPT.

## ✨ Tính năng

### Cho Giáo viên:
- 📝 **Quản lý tài liệu**: Upload PDF, DOCX, TXT hoặc viết Markdown
- 🤖 **Tạo câu hỏi AI**: Sử dụng Gemini AI để tự động tạo câu hỏi từ tài liệu
- 📋 **Quản lý đề thi**: Tạo, sửa, xóa đề thi với nhiều loại câu hỏi
- ⚖️ **Phân mức độ**: Dễ, trung bình, khó cho từng câu hỏi
- 📄 **Xuất PDF**: Xuất đề thi ra file PDF với tùy chọn trộn câu hỏi/đáp án
- 📊 **Thống kê**: Xem điểm số, tỷ lệ đậu, quản lý lượt thi

### Cho Học sinh:
- 📝 **Làm bài trực tuyến**: Giao diện thân thiện, dễ sử dụng
- ⏱️ **Đồng hồ đếm ngược**: Theo dõi thời gian làm bài
- ✅ **Chấm điểm tự động**: Trắc nghiệm được chấm ngay
- 📈 **Xem kết quả**: Chi tiết từng câu, đáp án đúng/sai
- 📚 **Lịch sử**: Xem lại các lần thi trước

## 🛠️ Công nghệ sử dụng

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI**: Google Gemini API
- **File Processing**: PyPDF2, python-docx
- **PDF Export**: ReportLab
- **Frontend**: HTML/CSS (Responsive)

## 📋 Yêu cầu

- Python 3.8+
- MongoDB 4.0+
- Google Gemini API key (để sử dụng tính năng tạo câu hỏi AI)

## 🚀 Cài đặt

### 1. Clone repository

```bash
cd de_thi_ai
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình MongoDB

Đảm bảo MongoDB đang chạy:

```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB
```

### 5. Cấu hình biến môi trường

Sao chép file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
FLASK_SECRET_KEY=your-secret-key-here-change-this-in-production
MONGO_URI=mongodb://localhost:27017/exam_system
GEMINI_API_KEY=your-gemini-api-key-here
```

Lấy Gemini API key tại: https://makersuite.google.com/app/apikey

### 6. Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

## 📖 Hướng dẫn sử dụng

### Đăng ký tài khoản

1. Truy cập http://localhost:5000
2. Nhấp "Đăng ký"
3. Chọn vai trò: **Giáo viên** hoặc **Học sinh**
4. Điền thông tin và hoàn tất đăng ký

### Dành cho Giáo viên

#### Tạo tài liệu:
1. Vào menu "Tài liệu" → "Tạo tài liệu"
2. Chọn upload file (PDF/DOCX/TXT) hoặc nhập Markdown
3. Hệ thống tự động trích xuất nội dung

#### Tạo đề thi thủ công:
1. Vào menu "Đề thi" → "Tạo đề thi"
2. Nhập thông tin: tiêu đề, thời gian, điểm đạt
3. Thêm câu hỏi: Trắc nghiệm, Đúng/Sai, hoặc Tự luận
4. Phân loại độ khó cho mỗi câu

#### Tạo đề thi bằng AI:
1. Tạo hoặc chỉnh sửa đề thi
2. Chọn tài liệu làm nguồn
3. Chọn số lượng câu theo độ khó (Dễ/Trung bình/Khó)
4. Nhấn "Tạo câu hỏi AI"
5. AI sẽ tự động tạo câu hỏi từ nội dung tài liệu

#### Xuất đề thi PDF:
1. Vào đề thi cần xuất
2. Nhấn "Xuất PDF"
3. Tùy chọn:
   - Trộn ngẫu nhiên câu hỏi
   - Trộn ngẫu nhiên đáp án
   - Hiển thị đáp án đúng

### Dành cho Học sinh

1. Đăng nhập với tài khoản học sinh
2. Xem danh sách đề thi công khai
3. Nhấn "Làm bài" để bắt đầu
4. Làm bài trong thời gian quy định
5. Nộp bài và xem kết quả ngay

## 📁 Cấu trúc dự án

```
de_thi_ai/
├── app.py                 # Flask application
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── .env                  # Environment variables (create from .env.example)
├── models/               # Database models
│   ├── user.py
│   ├── document.py
│   ├── exam.py
│   ├── question.py
│   └── exam_attempt.py
├── routes/               # Route handlers
│   ├── auth.py          # Authentication
│   ├── main.py          # Dashboard
│   ├── document.py      # Document management
│   ├── exam.py          # Exam management
│   └── attempt.py       # Exam taking
├── utils/                # Utility functions
│   ├── file_handler.py  # File processing
│   ├── gemini_service.py # AI integration
│   └── pdf_exporter.py   # PDF export
├── templates/            # HTML templates
│   ├── base.html
│   ├── auth/
│   ├── main/
│   ├── document/
│   ├── exam/
│   └── attempt/
└── uploads/              # Uploaded files
```

## 🔒 Bảo mật

- Mật khẩu được mã hóa bằng bcrypt
- Session được bảo mật với SECRET_KEY
- Phân quyền giáo viên/học sinh
- Validation đầu vào

## 📄 Xuất PDF

Hệ thống hỗ trợ xuất đề thi ra file PDF với các tính năng:
- **Font tiếng Việt**: Sử dụng DejaVu Sans font, hỗ trợ đầy đủ ký tự tiếng Việt
- **Trình bày chuyên nghiệp**: Header trường học, tiêu đề rõ ràng, hướng dẫn làm bài
- **Tùy chọn linh hoạt**:
  - Trộn ngẫu nhiên câu hỏi
  - Trộn ngẫu nhiên đáp án
  - Hiển thị đáp án đúng và giải thích (cho đáp án)
- **Định dạng đẹp**: Sử dụng màu sắc, bảng, spacing hợp lý
- **KeepTogether**: Câu hỏi và đáp án luôn ở cùng một trang

Font DejaVu Sans được tải tự động khi cài đặt.

## 🌐 Triển khai Production

### Sử dụng Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Với Docker:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### Lưu ý Production:
- Đổi `FLASK_SECRET_KEY` thành giá trị ngẫu nhiên mạnh
- Sử dụng MongoDB Atlas hoặc MongoDB server production
- Bật HTTPS và cập nhật `SESSION_COOKIE_SECURE=True`
- Cấu hình Nginx/Apache làm reverse proxy

## 🐛 Xử lý lỗi thường gặp

### MongoDB connection error:
```bash
# Kiểm tra MongoDB đang chạy
mongosh  # hoặc mongo

# Nếu chưa chạy, start MongoDB
brew services start mongodb-community  # macOS
```

### Gemini API error:
- Kiểm tra API key trong file `.env`
- Đảm bảo đã enable Gemini API
- Kiểm tra quota và billing

### File upload error:
- Kiểm tra thư mục `uploads/` có quyền ghi
- Kiểm tra `MAX_CONTENT_LENGTH` trong config

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repository
2. Tạo branch cho tính năng mới
3. Commit và push
4. Tạo Pull Request

## � Deployment với Docker

Hệ thống hỗ trợ triển khai dễ dàng với Docker và Docker Compose.

### Requirements
- Docker v20.10+
- Docker Compose v1.29+

### Cấu hình nhanh

```bash
# 1. Copy cấu hình
cp .env.production .env

# 2. Chỉnh sửa .env với giá trị thực tế
nano .env

# 3. Triển khai
bash deploy.sh

# Hoặc sử dụng docker-compose trực tiếp
docker-compose up -d
```

### Truy cập

- **URL**: http://localhost:8000
- **Admin**: admin / admin@123 (thay đổi ngay!)
- **Student**: student1 / student@123

### Các lệnh hữu ích

```bash
# Xem logs
docker-compose logs -f web

# Dừng dịch vụ
docker-compose down

# Khởi tạo database
docker-compose exec web python init_db.py

# Truy cập MongoDB
docker-compose exec mongodb mongosh -u admin -p password
```

### Cấu hình HTTPS

```bash
# Tạo chứng chỉ tự ký
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem -keyout certs/key.pem -days 365
```

Xem [DEPLOYMENT.md](./DEPLOYMENT.md) để hướng dẫn chi tiết.

## �📝 License

MIT License - Xem file LICENSE để biết thêm chi tiết

## 👥 Tác giả

Được phát triển cho học sinh THPT với giao diện thân thiện và dễ sử dụng.

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo Issue trên GitHub hoặc liên hệ qua email.

---

**Chúc bạn sử dụng hệ thống hiệu quả! 🎓**
