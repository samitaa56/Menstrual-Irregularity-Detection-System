# Email Verification Guide - Development

## Problem
Verification emails are not being sent to users' Gmail inboxes.

## Solution: Configure Gmail SMTP (RECOMMENDED)

**See `GMAIL_SETUP.md` for complete Gmail setup instructions.**

### Quick Steps:
1. Create a test Gmail account
2. Enable 2-Factor Authentication
3. Generate an "App Password" at https://myaccount.google.com/apppasswords
4. Update `settings.py` with your Gmail and App Password:
   ```python
   EMAIL_HOST_USER = "your-test-email@gmail.com"
   EMAIL_HOST_PASSWORD = "your-16-char-app-password"
   ```
5. Restart the Django server
6. Emails will now be sent to users' inboxes! ✅

---

## Alternative Option 1: Use Development Verification API (For Testing Only)

If you don't want to set up Gmail, use this endpoint to verify accounts instantly:

```bash
curl -X POST http://127.0.0.1:8000/api/dev-verify/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username"}'
```

**Response**:
```json
{
  "message": "✅ User 'username' has been verified and activated for testing!"
}
```

Then you can login. **Note:** This only works in development mode (DEBUG=True).

---

## Alternative Option 2: Check Email File Backend

If configured with file backend, emails are saved to: `./tracker/logs/emails/`

1. Check the `logs/emails/` folder
2. Open the email file to find the verification link
3. Copy and use that link in your browser

---

## For Production

**IMPORTANT:** 
- Use environment variables for Gmail credentials
- Never hardcode passwords in settings.py
- Switch to file backend or alternative email service
- See `GMAIL_SETUP.md` for production best practices

---

## Quick Test Steps

### With Gmail Setup:
1. Sign up form with valid email
2. **Wait 30 seconds** for email delivery
3. Check your Gmail inbox
4. Click verification link
5. Login and enjoy! 🎉

### Without Gmail (Dev Endpoint):
1. Sign up with any email
2. Call `/api/dev-verify/` endpoint
3. Login immediately

## Cross-Device Testing (Phone/Tablet)

If you want to verify emails on a different device than your PC:
1. Find your PC's local IP address (e.g., run `ipconfig` in CMD).
2. Update `FRONTEND_URL` in `backend_project/settings.py` with your IP: `http://192.168.1.109:3000`.
3. Update `API_BASE_URL` in `period_frontend/src/config.js` with your IP: `http://192.168.1.109:8000/api`.
4. **CRITICAL:** Restart the Django server using this exact command to allow phone access:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
5. Restart the React dev server (`npm start`).
6. Sign up again. The app and the verification link will now work on your phone!

**Troubleshooting:**
- If it still doesn't load on your phone, ensure your phone and PC are on the **same Wi-Fi**.
- You might need to temporarily disable your PC's **Firewall** or allow port 8000 and 3000.



