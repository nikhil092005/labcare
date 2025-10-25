# AI Chat Troubleshooting Guide

## 🚨 "I'm having trouble connecting to the AI service" Error

This error occurs when the Gemini API connection fails. Here's how to fix it:

## 🔧 Step 1: Test Your API Key

Run the test script to verify your API key:

```bash
python test_gemini.py
```

This will tell you exactly what's wrong with your API connection.

## 🔑 Step 2: Get a Valid API Key

If you don't have a valid API key:

1. **Visit Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Create a new API key**
4. **Copy the key** (starts with "AIza...")
5. **Replace the key** in `ai_chat.py` line 13:

```python
GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
```

## 🛠️ Step 3: Install Required Dependencies

Make sure you have the required package:

```bash
pip install google-generativeai
```

## 🔍 Step 4: Common Issues & Solutions

### Issue 1: Invalid API Key

**Error**: "API_KEY_INVALID" or "authentication failed"
**Solution**:

- Get a new API key from Google AI Studio
- Make sure the key is correctly copied (no extra spaces)
- Ensure the API key is enabled

### Issue 2: Quota Exceeded

**Error**: "quota exceeded" or "limit reached"
**Solution**:

- Check your usage in Google AI Studio
- Wait for quota reset (usually daily)
- Upgrade to a paid plan if needed

### Issue 3: Network Issues

**Error**: "network" or "connection" errors
**Solution**:

- Check your internet connection
- Ensure you can access Google services
- Try from a different network

### Issue 4: Model Not Found (404 Error)

**Error**: "404 models/gemini-pro is not found" or "model not supported"
**Solution**:

- The older `gemini-1.5-flash` models are no longer available
- Updated to use `gemini-2.0-flash` (current stable model)
- Fallback options: `gemini-2.5-flash`, `gemini-flash-latest`, `gemini-2.0-flash-001`

### Issue 5: API Not Enabled

**Error**: "API not enabled" or "service not available"
**Solution**:

- Enable Gemini API in Google Cloud Console
- Make sure billing is set up (even for free tier)

## 🧪 Step 5: Test the Connection

1. **Run the test script**:

   ```bash
   python test_gemini.py
   ```

2. **Check the Flask console** for debug messages when using AI chat

3. **Visit the test endpoint** (while logged in):
   ```
   http://localhost:5000/ai-chat/test
   ```

## 📋 Step 6: Verify Your Setup

### Check API Key Format

Your API key should:

- Start with "AIza"
- Be about 39 characters long
- Have no spaces or extra characters

### Check Dependencies

```bash
pip list | grep google-generativeai
```

Should show: `google-generativeai`

### Check Flask Console

When you send a message, you should see:

```
🔧 Sending request to Gemini API...
📝 Message: Your message here...
🔑 API Key configured: True
📥 AI Response: AI response here...
```

## 🚀 Step 7: Restart Your Application

After making changes:

1. Stop your Flask app (Ctrl+C)
2. Restart it: `python app.py`
3. Test the AI chat again

## 📞 Still Having Issues?

### Check These Files:

- `ai_chat.py` - Line 13 has your API key
- `app.py` - AI chat blueprint is registered
- `requirements_ai.txt` - Dependencies listed

### Debug Mode:

Add this to your Flask app for more detailed errors:

```python
app.config['DEBUG'] = True
```

### Test Endpoints:

- `/ai-chat` - AI chat page
- `/ai-chat/test` - Test API connection
- `/ai-chat/send` - Send message (POST)

## ✅ Success Indicators

When working correctly, you should see:

- ✅ Test script shows "SUCCESS!"
- ✅ Flask console shows debug messages
- ✅ AI chat responds with actual content
- ✅ No error messages in browser console

## 🔄 Quick Fix Checklist

- [ ] API key is valid and correctly set
- [ ] `google-generativeai` package is installed
- [ ] Flask app is restarted after changes
- [ ] Internet connection is working
- [ ] No firewall blocking Google services
- [ ] API quota is not exceeded

## 📚 Additional Resources

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google Cloud Console](https://console.cloud.google.com/)

---

**Need more help?** Check the Flask console output and the test script results for specific error messages.
