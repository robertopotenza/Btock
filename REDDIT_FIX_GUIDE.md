# Reddit API 401 Error Fix Guide

## 🔍 Problem Identified

Your Reddit API is returning a **401 Unauthorized** error, which means the credentials are being rejected by Reddit's servers.

## 📋 Current Configuration Analysis

Based on your Railway environment variables:
- **Client ID**: `D14b1bj_bpv_bwtX1KcmA` ✅ (Present)
- **Client Secret**: `1DPZmKRSmPOfcxzLgiXVeQChaow` ✅ (Present)  
- **User Agent**: `StockResearchBot/1.0` ✅ (Fixed - now reads from `user_agent` variable)

## 🚨 Root Cause

The **401 error** indicates that Reddit is rejecting your app credentials. Looking at your Reddit app screenshot, the most likely issues are:

### **Issue 1: App Type Mismatch**
- Your app might be configured as "web app" instead of "script"
- **Script apps** are for personal use (what we need)
- **Web apps** require different authentication flow

### **Issue 2: Redirect URI Mismatch**
- I see `http://localhost:8000` in your redirect URI
- For script apps, this should typically be `http://localhost:8080` or can be left blank

## 🔧 Step-by-Step Fix

### **Option 1: Reconfigure Existing App**

1. **Go to Reddit Apps**: https://www.reddit.com/prefs/apps
2. **Click "edit"** on your StockResearchBot app
3. **Verify Settings**:
   - **App Type**: Must be "script" 
   - **Name**: StockResearchBot (current: ✅)
   - **Description**: Can be anything
   - **About URL**: Can be blank
   - **Redirect URI**: Change to `http://localhost:8080` or leave blank
4. **Save Changes**
5. **Copy New Credentials** (they might change after editing)

### **Option 2: Create New App (Recommended)**

1. **Delete Current App**: Click "delete" on StockResearchBot
2. **Create New App**: Click "Create App" or "Create Another App"
3. **Configure Correctly**:
   ```
   Name: BtockSentimentBot
   App Type: script ← CRITICAL
   Description: Btock Stock Sentiment Analysis
   About URL: (leave blank)
   Redirect URI: http://localhost:8080
   ```
4. **Save and Copy Credentials**

### **Option 3: Test with Different Credentials**

Create a completely new Reddit account and app to eliminate any account-specific issues.

## 🔄 Update Railway Environment Variables

After fixing the Reddit app:

1. **Go to Railway Dashboard** → Btock Project → Variables
2. **Update Variables**:
   ```
   REDDIT_CLIENT_ID=your_new_client_id
   REDDIT_CLIENT_SECRET=your_new_client_secret
   user_agent=BtockSentimentBot/1.0
   ```
3. **Deploy** to restart the application

## 🧪 Test the Fix

After updating credentials, test with this command:

```python
import praw

reddit = praw.Reddit(
    client_id="your_new_client_id",
    client_secret="your_new_client_secret", 
    user_agent="BtockSentimentBot/1.0"
)

# Test connection
try:
    subreddit = reddit.subreddit("announcements")
    post = next(iter(subreddit.hot(limit=1)))
    print("✅ Reddit API working!")
    print(f"Test post: {post.title}")
except Exception as e:
    print(f"❌ Still failing: {e}")
```

## 🎯 Expected Results

### **Before Fix**:
```
Reddit API setup failed: received 401 HTTP response
❌ Reddit API still not configured
```

### **After Fix**:
```
✅ Reddit API connected successfully with user agent: BtockSentimentBot/1.0
🚀 Reddit API configured successfully!
```

## 🔍 Additional Debugging

If the issue persists:

### **Check Reddit App Status**
- Ensure your Reddit account is in good standing
- Verify the app hasn't been suspended or restricted
- Check if you've hit any rate limits

### **Verify Credentials Format**
- Client ID should be ~14 characters (yours: `D14b1bj_bpv_bwtX1KcmA` ✅)
- Client Secret should be ~27 characters (yours: correct length ✅)
- No extra spaces or special characters

### **Test with Minimal Code**
```python
import praw
import os

# Test just the connection
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("user_agent", "test/1.0")
)

print(reddit.read_only)  # Should print True
```

## 📞 Next Steps

1. **Try Option 2** (create new app) - this fixes most issues
2. **Update Railway variables** with new credentials  
3. **Test the sentiment analysis** - should work immediately
4. **If still failing** - check Reddit account status and try Option 3

The Reddit API should work perfectly once the app type is set to "script" and credentials are properly configured! 🚀
