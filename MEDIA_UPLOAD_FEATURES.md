# Media Upload Features - Group Questions & Skill Questions

## 📋 Overview

Các câu hỏi nhóm và câu hỏi kỹ năng (nghe, nói, đọc, viết) giờ đây hỗ trợ upload file media trực tiếp thay vì chỉ nhập link.

## 🎯 Features

### 1. Media Upload Support
- **File Upload**: Tải lên trực tiếp file audio/video từ máy tính
- **URL Input**: Vẫn hỗ trợ nhập link trực tiếp nếu muốn
- **Supported Formats**:
  - Audio: MP3, WAV, M4A, FLAC, OGG
  - Video: MP4, WebM, AVI, MOV, 3GP

### 2. Question Types with Media
- **listening** (Nghe): Audio file + support content + correct answer
- **speaking** (Nói): Audio file + support content + correct answer
- **reading** (Đọc): Text/video file + support content + correct answer
- **writing** (Viết): Support content (instructions) + correct answer
- **group** (Nhóm câu hỏi): Media file (NEW!) + group prompt + correct answer

### 3. File Management
- **Storage Location**: `uploads/media/`
- **Max File Size**: 100MB
- **Naming**: Automatic unique naming with timestamp to prevent conflicts
- **Serving**: Files served via `/uploads/media/{filename}` route

## 📁 File Changes

### Backend Files

#### 1. `utils/file_handler.py`
**Added**: `save_media_file()` function
- Validates file extensions
- Creates media subfolder if not exists
- Generates unique filename with timestamp
- Returns file path and relative URL
- Supports: mp3, wav, m4a, mp4, webm, avi, mov, flac, ogg, 3gp

#### 2. `routes/exam.py`
**Updated**: `add_question()` endpoint
- Added media file upload handling
- Detects file in `media_file` form field
- Falls back to `media_url` if no file uploaded
- Applies to all skill questions + group questions
- Validates file type before saving

**Updated**: `edit_question()` endpoint
- Same media upload handling
- Allows replacing existing media files

**Added**: Import for `save_media_file` function

#### 3. `config.py`
**Updated**: 
- Increased `MAX_CONTENT_LENGTH` from 16MB to 100MB for media files

### Frontend Files

#### 1. `templates/exam/edit.html`
**Updated**: Add Question Modal
- Added `enctype="multipart/form-data"` to form
- Skill questions section:
  - Added file input: `<input type="file" name="media_file" accept="audio/*,video/*">`
  - Kept URL input as fallback
  - Added supported formats info
- Group questions section:
  - Added media file upload input (optional)
  - Added URL input as fallback
  - Shows it's optional with proper messaging

**Updated**: Edit Question Modal
- Added `enctype="multipart/form-data"` to form
- Added skill questions edit section with media file upload
- Added group questions edit section with media file upload
- Updated question type selection to include all 8 types

**Updated**: Question Display
- Group questions now show media URL in preview (if exists)

#### 2. `templates/attempt/take.html`
**Updated**: Group Question Display
- Shows media player (audio/video) if media_url exists
- Auto-detects file type (audio vs video)
- Audio: `<audio controls>` element
- Video: `<video controls>` element

#### 3. `templates/attempt/result.html`
**Updated**: Group Question Results
- Displays media player if media_url exists
- Shows original media during result review
- Shows student answer + expected answer

## 🚀 Usage

### Creating a Question with Media Upload

1. **Navigate to**: Exam Edit page → Add Question
2. **Select Question Type**: Choose "Nhóm câu hỏi" or skill type (Nghe, Nói, Đọc, Viết)
3. **Upload Media** (two options):
   - Click file input to select audio/video file from computer
   - OR enter URL directly if you have a link
4. **Add Other Details**:
   - Group prompt / Support content
   - Correct answer / Expected response
5. **Save**: Submit form

### Form Validation
- Must select either file upload OR URL (at least one)
- File types validated on server side
- File size limited to 100MB
- Clear error messages for invalid formats

## 🔄 Data Flow

### When Creating Question
```
1. User selects "Group" or Skill question type
2. Form shows media upload + URL input fields
3. User uploads file OR enters URL
4. Form submitted with enctype="multipart/form-data"
5. Backend receives file via request.files['media_file']
6. save_media_file() validates and stores file
7. Returns URL like "/uploads/media/media_20260104_120000.mp3"
8. URL saved to database in question.media_url field
```

### When Student Takes Exam
```
1. Question displayed with media player
2. Browser loads media from /uploads/media/{filename}
3. Student can listen/watch media
4. Student provides answer
```

### When Viewing Results
```
1. Media URL retrieved from database
2. Media player displayed for review
3. Original media + student answer shown together
```

## 📊 Database Schema

### Question Document (Updated)
```python
{
    "_id": ObjectId,
    "exam_id": ObjectId,
    "question_text": str,
    "question_type": str,  # 'group', 'listening', etc.
    "options": list,
    "correct_answer": str,
    "difficulty": str,
    "points": int,
    "explanation": str,
    "media_url": str,        # NEW: "/uploads/media/filename"
    "support_content": str,
    "group_prompt": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

## ✅ Validation

### File Upload Validation
- ✅ File extension checked (must be audio/video format)
- ✅ File size limited to 100MB
- ✅ Unique filename generated to prevent overwrites
- ✅ Proper MIME type handling (audio vs video)

### Form Validation
- ✅ At least question text required
- ✅ Difficulty and question type required
- ✅ File OR URL must be provided for media types
- ✅ Correct answer required

## 🎓 Teacher Features

### Create Group Question with Media
```
1. Question: "Lắng nghe đoạn hội thoại sau và trả lời các câu hỏi"
2. Type: Nhóm câu hỏi
3. Upload: conversation_audio.mp3
4. Group Prompt: "Trả lời các câu hỏi sau dựa trên đoạn nghe"
5. Save: Tạo câu hỏi nhóm với audio
```

### Edit Question Media
```
1. Click "Sửa" on question
2. Can replace old media with new file
3. Or update URL
4. Can clear media by leaving blank
5. Save changes
```

## 👥 Student Experience

### Taking Exam with Media Questions
```
1. See group question prompt
2. Audio/video player appears
3. Can replay media multiple times
4. Answers questions in textarea
5. Submit exam
```

### Reviewing Results
```
1. See original media
2. Compare with their answer
3. See expected/suggested answer
4. Can review media again if needed
```

## 🔐 Security

- ✅ Files saved with unique timestamp-based names
- ✅ File extension validation (whitelist)
- ✅ File size limits enforced
- ✅ Secure filename generation using werkzeug
- ✅ Files stored outside public web root
- ✅ Served through Flask route (can add permissions later)

## 📈 Performance

- **File Upload**: 
  - Asynchronous file processing could be added in future
  - Current: Synchronous (acceptable for most use cases)
- **Bandwidth**: Media streaming via Flask (consider CDN for large deployments)
- **Storage**: ~1GB per 100 hours of audio @ 128kbps MP3

## 🔄 Backward Compatibility

- ✅ Existing questions without media still work
- ✅ media_url field defaults to empty string
- ✅ Templates handle missing media gracefully
- ✅ All existing question types unaffected

## 🚀 Future Enhancements

1. **Media Compression**: Auto-compress uploaded audio
2. **Transcoding**: Convert to standard formats
3. **CDN Integration**: Serve media from CDN for faster delivery
4. **Thumbnail Generation**: Generate video thumbnails
5. **Duration Info**: Display media duration
6. **Streaming**: Support streaming for large files
7. **Media Library**: Reuse media across questions
8. **Video Editing**: Built-in video trimming
