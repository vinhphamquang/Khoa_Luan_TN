# Bảo Mật API Key - Hướng Dẫn Quan Trọng

## ⚠️ Vấn Đề Hiện Tại

API key của Gemini đã bị leak (rò rỉ) và bị Google khóa với lỗi:
```
403 - Your API key was reported as leaked. Please use another API key.
```

## 🔐 Cách Tạo API Key Mới

### 1. Truy cập Google AI Studio
- URL: https://aistudio.google.com/app/apikey
- Hoặc: https://makersuite.google.com/app/apikey

### 2. Tạo API Key
1. Click "Create API Key"
2. Chọn Google Cloud project (hoặc tạo mới)
3. Copy API key mới được tạo

### 3. Cập nhật file .env
```bash
GEMINI_API_KEY="YOUR_NEW_API_KEY_HERE"
SECRET_KEY="your-secret-key-change-in-production-12345"
```

### 4. Restart server
```bash
# Stop server hiện tại (Ctrl+C)
# Start lại
python backend/app.py
```

## 🛡️ Cách Bảo Vệ API Key

### 1. KHÔNG BAO GIỜ commit API key lên Git

**Kiểm tra .gitignore:**
```bash
# File .gitignore phải có:
.env
*.env
.env.local
```

**Nếu đã commit nhầm:**
```bash
# Xóa file khỏi Git history
git rm --cached .env
git commit -m "Remove .env from tracking"

# Thêm vào .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

### 2. Sử dụng Environment Variables

**Development (Local):**
- Lưu trong file `.env`
- File `.env` phải có trong `.gitignore`

**Production:**
- Sử dụng environment variables của hosting platform
- Heroku: `heroku config:set GEMINI_API_KEY=xxx`
- Vercel: Settings > Environment Variables
- AWS: Systems Manager Parameter Store

### 3. Giới Hạn API Key

**Trong Google Cloud Console:**
1. Vào API & Services > Credentials
2. Click vào API key
3. Thiết lập restrictions:
   - **Application restrictions**: HTTP referrers hoặc IP addresses
   - **API restrictions**: Chỉ cho phép Generative Language API

### 4. Monitoring và Alerts

**Thiết lập cảnh báo:**
- Google Cloud Console > Monitoring
- Tạo alert khi có usage bất thường
- Theo dõi quota và billing

### 5. Rotate API Keys Định Kỳ

- Tạo API key mới mỗi 3-6 tháng
- Xóa API key cũ sau khi migrate

## 📋 Checklist Bảo Mật

- [ ] File .env có trong .gitignore
- [ ] Không commit API key lên Git
- [ ] API key có restrictions (IP/domain)
- [ ] Thiết lập monitoring và alerts
- [ ] Sử dụng environment variables trong production
- [ ] Rotate API keys định kỳ
- [ ] Review Git history để đảm bảo không có API key

## 🔍 Kiểm Tra API Key Đã Bị Leak

**Cách 1: Kiểm tra Git history**
```bash
git log --all --full-history --source -- .env
git log -p --all -- .env
```

**Cách 2: Search trên GitHub**
- Vào repository settings
- Security > Secret scanning alerts

**Cách 3: Sử dụng tools**
```bash
# Cài đặt gitleaks
brew install gitleaks

# Scan repository
gitleaks detect --source . --verbose
```

## 🚨 Nếu API Key Bị Leak

1. **Revoke ngay lập tức:**
   - Vào Google Cloud Console
   - Delete API key bị leak

2. **Tạo API key mới:**
   - Tạo key mới với restrictions
   - Cập nhật vào .env

3. **Review code:**
   - Kiểm tra xem còn chỗ nào hardcode API key không
   - Đảm bảo .gitignore đúng

4. **Clean Git history (nếu cần):**
   ```bash
   # Sử dụng BFG Repo-Cleaner
   bfg --replace-text passwords.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

## 📚 Best Practices

1. **Sử dụng .env.example:**
   ```bash
   # .env.example (commit được)
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

2. **Documentation:**
   - Ghi rõ cách setup API key trong README
   - Hướng dẫn team members

3. **Code Review:**
   - Review kỹ trước khi merge
   - Kiểm tra không có sensitive data

4. **Automated Checks:**
   - Pre-commit hooks để detect secrets
   - CI/CD pipeline checks

## 🔗 Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Google Cloud API Keys Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
