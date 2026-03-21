# Gmail Email Verification Setup Guide

## Problem
Verification emails are not being sent to users' Gmail inboxes.

## Solution: Configure Gmail SMTP

### Step 1: Create a Test Gmail Account (Recommended)
Create a separate Gmail account for testing (do NOT use your personal Gmail with sensitive data):
- Example: `yourflow.test@gmail.com`
- Keep this account separate from production

### Step 2: Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on **"2-Step Verification"**
3. Follow the steps to enable 2FA on your test Gmail account

### Step 3: Create an App Password

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select:
   - **Device**: Select "Mail"
   - **OS/App**: Select "Other (custom name)" and type "Django"
3. Click **"Generate"**
4. Google will show you a 16-character password
5. **Copy this password** (example: `abcd efgh ijkl mnop`)

### Step 4: Update Django Settings

Open `backend_project/settings.py` and replace:

```python
EMAIL_HOST_USER = "your-test-email@gmail.com"  # Your test Gmail address
EMAIL_HOST_PASSWORD = "your-app-password-here"  # The 16-char password from Step 3
```

Example:
```python
EMAIL_HOST_USER = "yourflow.test@gmail.com"
EMAIL_HOST_PASSWORD = "abcd efgh ijkl mnop"
```

### Step 5: Save and Restart Server

1. Save the `settings.py` file
2. Stop the Django server (Ctrl+C)
3. Restart it: `python manage.py runserver 8000`

### Step 6: Test Email Verification

1. Sign up with any email address
2. Check the verification email in your inbox
3. Click the verification link
4. Login with your credentials

---

## Troubleshooting

### Error: "Authentication failed"
- ❌ Check if you're using the correct Gmail address
- ❌ Check if the app password is exactly 16 characters with spaces
- ❌ Verify 2-Factor Authentication is enabled

### Email Not Arriving
- ❌ Check spam/promotions folder
- ❌ Wait 30 seconds (Gmail delivery takes time)
- ❌ Check console for error messages

### I Don't Want to Use Gmail
Use the **Development Verification Endpoint**:

```bash
curl -X POST http://127.0.0.1:8000/api/dev-verify/ \
  -H "Content-Type: application/json" \
  -d '{"username": "yourUsername"}'
```

Or change `settings.py` to file backend:
```python
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "logs" / "emails"
```

---

## Security Notes

⚠️ **IMPORTANT FOR PRODUCTION:**
- ❌ NEVER hardcode credentials in settings.py
- ✅ Use environment variables: `EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")`
- ✅ Store in `.env` file (add to `.gitignore`)
- ✅ Use Django's `python-decouple` or `python-dotenv` package

---

## For Production Deployment

Use environment variables instead:

```bash
# .env file
EMAIL_HOST_USER=yourflow@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

And update settings.py:
```python
import os
from decouple import config

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
```

