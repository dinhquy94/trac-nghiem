# 🖼️ Hướng dẫn Upload Ảnh Đại Diện

## Tính năng mới: Upload Ảnh từ Máy tính

Người dùng giờ có thể **tải ảnh đại diện lên từ máy tính** thay vì phải nhập URL.

### ✨ Các tính năng:

1. **Upload file ảnh trực tiếp**
   - Hỗ trợ định dạng: JPG, PNG, GIF, WEBP
   - Giới hạn kích thước: 5MB
   - Preview ảnh trước khi upload
   - Tự động đổi tên file để tránh trùng lặp

2. **Hoặc nhập URL ảnh** (như trước)
   - Vẫn hỗ trợ nhập link ảnh từ internet
   - Tự động fallback về ảnh mặc định nếu URL rỗng

3. **Ảnh mặc định tự động**
   - Nếu không upload/nhập URL → hiển thị avatar với chữ cái đầu của username
   - Sử dụng UI Avatars API với màu gradient đẹp

### 📁 Cấu trúc lưu trữ:

```
uploads/
  └── avatars/
      ├── avatar_USER_ID_20251221_205959.jpg
      ├── avatar_USER_ID_20251221_210123.png
      └── ...
```

- Mỗi ảnh có tên duy nhất: `avatar_{user_id}_{timestamp}.{ext}`
- Lưu trong thư mục `uploads/avatars/`
- Truy cập qua URL: `/uploads/avatars/filename.jpg`

### 🔧 Cài đặt:

Thư mục `uploads/avatars` đã được tạo tự động.

### 💡 Cách sử dụng:

1. Đăng nhập vào hệ thống
2. Vào **Thông tin cá nhân** (click avatar trên menu)
3. Trong phần "Cập nhật thông tin":
   - **Chọn ảnh từ máy**: Click nút "📤 Chọn ảnh từ máy tính"
   - **Hoặc nhập URL**: Điền vào ô "Hoặc nhập URL ảnh"
4. Click "💾 Cập nhật thông tin"

### 🎯 Backend Implementation:

**routes/auth.py:**
- `update_profile()`: Xử lý upload file
- Kiểm tra định dạng file với `allowed_file()`
- Tạo tên file duy nhất với timestamp
- Lưu vào `uploads/avatars/`
- Cập nhật database với đường dẫn `/uploads/avatars/{filename}`

**app.py:**
- Route `@app.route('/uploads/<path:filename>')`: Serve uploaded files
- Sử dụng `send_from_directory()` để trả về file

**models/user.py:**
- `update_profile()`: Cập nhật thông tin user
- Hỗ trợ cập nhật `avatar_url` với đường dẫn local hoặc URL

### 🔒 Bảo mật:

- ✅ Kiểm tra định dạng file (chỉ cho phép ảnh)
- ✅ Giới hạn kích thước file (5MB)
- ✅ Sử dụng `secure_filename()` để tránh path traversal
- ✅ Tạo tên file duy nhất để tránh ghi đè

### 🚀 API Endpoint:

```python
POST /auth/update_profile
Content-Type: multipart/form-data

Parameters:
- full_name: string (required)
- email: string (required)
- avatar_file: file (optional, image file)
- avatar_url: string (optional, URL ảnh)

Response:
- Redirect to /auth/profile with flash message
```

### 📝 Note:

- Nếu cả hai `avatar_file` và `avatar_url` đều có giá trị, ưu tiên `avatar_file`
- Ảnh cũ không bị xóa tự động (có thể thêm logic xóa sau)
- Preview ảnh chỉ hoạt động trên client-side (JavaScript)
