# 📹 Media Upload for Group Questions - User Guide

## Quick Start

### For Teachers

#### Upload Media for Group Questions
1. Go to Exam Edit page
2. Click "➕ Thêm câu hỏi" (Add Question)
3. Select Question Type: **"Nhóm câu hỏi"** (Group Questions)
4. Fill in question details
5. **Upload Media** (Choose one):
   - **Option A**: Click "📁 Tải lên Media (Audio/Video)" to upload from your computer
   - **Option B**: Paste media URL in "Media URL (Link trực tiếp)" field
6. Fill in group prompt and expected answer
7. Click "Thêm câu hỏi" (Add Question)

#### Supported Media Formats

**Audio**:
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)
- OGG (.ogg)

**Video**:
- MP4 (.mp4)
- WebM (.webm)
- AVI (.avi)
- MOV (.mov)
- 3GP (.3gp)

**Limits**:
- Maximum file size: 100MB
- Recommended: 10-30MB for smooth playback

### For Students

#### Taking Exam with Media
1. Open exam to take
2. When you see group question with media icon 🎵:
   - Audio questions: Click play to listen
   - Video questions: Click play to watch
   - Can replay multiple times
3. Answer questions in the text area below
4. Submit exam

#### Reviewing Results
1. After exam submission
2. In results page, media player shows original content
3. Compare your answer with expected answer
4. Can review media again for self-learning

---

## Detailed Features

### 1. Group Questions with Media

**What are Group Questions?**
- Multiple related questions under ONE shared prompt
- Shared media (audio/video) for all questions
- Common use case: Listening comprehension, video comprehension

**Example**: 
```
📚 Group Question - Listening Comprehension
🎵 [Audio player with recording]
    
Câu 1: What is the main topic? (Answer: _________)
Câu 2: Who is speaking? (Answer: _________)
Câu 3: When does it happen? (Answer: _________)
```

### 2. Skill-Based Questions (with Media)

All skill questions also support media upload:

#### 🎧 Listening Questions
- Upload: Audio file (MP3, WAV, etc.)
- Students listen to audio
- Answer comprehension questions

#### 🎤 Speaking Questions
- Upload: Audio/video file (optional)
- Students describe what they heard/saw
- Or provide spoken answer description

#### 📖 Reading Questions
- Upload: Text or document
- Students read and comprehend
- Answer questions about content

#### ✍️ Writing Questions
- No media required
- Support content = Writing instructions
- Students write essay/response

---

## 🛠️ Technical Details

### File Storage
- **Location**: `uploads/media/` folder
- **Access**: Via `/uploads/media/{filename}` URL
- **Naming**: Auto-generated with timestamp to prevent conflicts
  - Example: `media_20260104_143025.mp3`

### Upload Process
1. Select file or enter URL
2. Submit form with `enctype="multipart/form-data"`
3. Backend validates file type and size
4. File saved to `uploads/media/` folder
5. URL stored in database
6. URL accessible to students during exam

### Database Storage
- **Field**: `question.media_url`
- **Format**: `/uploads/media/media_TIMESTAMP.extension`
- **Type**: String (URL path)
- **Backup**: Can also store external URLs (HTTP/HTTPS)

---

## ⚙️ Configuration

### Default Settings
```python
# config.py
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
UPLOAD_FOLDER = 'uploads'
```

### Change Max File Size (if needed)
Edit `.env`:
```
MAX_CONTENT_LENGTH=52428800  # 50MB instead of 100MB
```

---

## 🔒 Security Features

✅ File type validation (whitelist approach)
✅ File size limit enforcement
✅ Unique filename generation (prevents overwrites)
✅ Secure filename handling (werkzeug)
✅ Stored outside web root
✅ Served through Flask route

---

## 📊 Usage Statistics

### Upload Guidelines
- **Recommended file size**: 5-20MB for smooth playback
- **Max duration**: ~40 minutes for 100MB audio (128kbps MP3)
- **Typical**: 5-10 minute media for exam questions

### Storage Estimation
```
1 exam with 5 questions (5MB media each) = 25MB
1000 exams = 25GB storage
```

---

## 🐛 Troubleshooting

### "File format not supported"
- Check extension is in supported list
- Verify file is not corrupted
- Try converting file to MP3 (audio) or MP4 (video)

### "File too large"
- File exceeds 100MB limit
- Compress file or use shorter media
- Use online tools: TinyMP3, HandBrake, etc.

### "Upload failed"
- Check internet connection
- Try smaller file
- Browser may have timeout limit (~30 minutes)

### "Media doesn't play in browser"
- Convert to MP3 (audio) or MP4 (video)
- Try different browser (Chrome, Firefox, Safari)
- Check browser supports format

---

## 💡 Tips & Best Practices

### For Teachers

1. **Keep Media Short**
   - 1-3 minutes for listening exercises
   - 3-5 minutes for video
   - Improves exam experience

2. **Use Standard Formats**
   - MP3 for audio (best compatibility)
   - MP4 for video (best compatibility)
   - Lower file size: faster upload & playback

3. **Test Before Publishing**
   - Preview exam
   - Check media plays correctly
   - Verify audio quality

4. **Organize Media**
   - Name files clearly
   - Keep original file backup
   - Version control for updates

### For Students

1. **Stable Internet**
   - Use good WiFi/connection
   - Media streams from server
   - Prepare before exam if possible

2. **Practice with Media**
   - Get comfortable with controls
   - Know how to replay/rewind
   - Test your device sound before exam

3. **Time Management**
   - Don't spend too long on one question
   - Can review media multiple times
   - Note key points while listening

---

## 📱 Browser Support

✅ Chrome/Edge 90+
✅ Firefox 88+
✅ Safari 14+
✅ Mobile browsers (iOS Safari, Chrome Android)
✅ Tablets supported

**Note**: Some formats may not be supported on older browsers or mobile devices.

---

## 🚀 Advanced Features (Future)

- [ ] Auto-compress media on upload
- [ ] CDN integration for faster delivery
- [ ] Media transcoding (convert formats)
- [ ] Video thumbnail generation
- [ ] Media duration display
- [ ] Adaptive bitrate streaming
- [ ] Media library (reuse across exams)
- [ ] Video editing in browser

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review MEDIA_UPLOAD_FEATURES.md
3. Check logs in server console
4. Contact administrator

---

## Version History

- **v1.0** (2025-01-04): Initial media upload for group questions
  - File upload support
  - Audio/video playback
  - URL fallback support
