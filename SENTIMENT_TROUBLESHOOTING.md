# Sentiment Analysis Troubleshooting Guide

## 🔧 Getting Real Sentiment Analysis Working

This guide helps you configure and troubleshoot the sentiment analysis feature to get **real social media data** instead of demo mode.

## 📋 Quick Diagnostic Checklist

### **Step 1: Check Current Status**
1. Run sentiment analysis and look for mode indicator
2. If you see "🎯 Demo Mode Active" - APIs need configuration
3. If you see "🚀 Live Mode Active" - APIs are working

### **Step 2: Identify Required APIs**
The sentiment analysis uses three data sources:
- **X (Twitter)** via Grok API - Requires XAI_API_KEY
- **Reddit** - Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET  
- **StockTwits** - Public API (no key required, but may have rate limits)

## 🔑 API Configuration Steps

### **X (Twitter) via Grok API Setup**

#### **1. Get Grok API Access**
- Visit: https://x.ai/ or https://grok.x.ai/
- Sign up for Grok API access
- Obtain your API key

#### **2. Set Environment Variable**
```bash
# In Railway Dashboard → Variables
XAI_API_KEY=your_actual_grok_api_key_here

# Or locally for testing
export XAI_API_KEY="your_actual_grok_api_key_here"
```

#### **3. Verify API Endpoint**
The default endpoint is: `https://api.x.ai/v1/chat/completions`
If this doesn't work, try:
```bash
# Alternative endpoint (if needed)
XAI_API_URL=https://api.grok.x.ai/v1/chat/completions
```

### **Reddit API Setup**

#### **1. Create Reddit App**
- Go to: https://www.reddit.com/prefs/apps
- Click "Create App" or "Create Another App"
- Choose "script" type
- Note your client ID and secret

#### **2. Set Environment Variables**
```bash
# In Railway Dashboard → Variables
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=Btock Sentiment Analyzer v1.0
```

### **StockTwits API**
- No setup required (public API)
- May encounter rate limits without authentication
- Works automatically when other APIs are configured

## 🐛 Common Issues & Solutions

### **Issue 1: Still Seeing Demo Mode**

#### **Symptoms:**
- "🎯 Demo Mode Active" message
- Simulated sentiment data
- No real API calls

#### **Troubleshooting Steps:**
1. **Check Environment Variables**
   ```bash
   # In Railway Dashboard, verify these are set:
   XAI_API_KEY=your_key
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   ```

2. **Restart Application**
   - Redeploy on Railway after setting environment variables
   - Environment variables only load on app restart

3. **Test API Keys**
   - Verify Grok API key is valid and active
   - Test Reddit credentials with a simple API call

### **Issue 2: X (Twitter) 404 Errors**

#### **Symptoms:**
- "X sentiment analysis failed: 404 Client Error"
- URL: https://api.x.ai/v1/chat/completions

#### **Solutions:**
1. **Verify API Key**
   ```bash
   # Test your Grok API key
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"grok-beta","messages":[{"role":"user","content":"test"}],"max_tokens":1}' \
        https://api.x.ai/v1/chat/completions
   ```

2. **Check API Endpoint**
   - Try alternative endpoint: `https://api.grok.x.ai/v1/chat/completions`
   - Verify the correct Grok API URL from documentation

3. **API Key Format**
   - Ensure no extra spaces or characters
   - Verify key is complete and not truncated

### **Issue 3: Reddit API Errors**

#### **Symptoms:**
- "Reddit sentiment analysis failed"
- Authentication errors

#### **Solutions:**
1. **Verify Reddit App Setup**
   - Ensure app type is "script"
   - Client ID and secret are correct
   - App is not suspended or restricted

2. **Test Reddit Connection**
   ```python
   import praw
   reddit = praw.Reddit(
       client_id="your_client_id",
       client_secret="your_client_secret", 
       user_agent="test"
   )
   print(list(reddit.subreddit("test").hot(limit=1)))
   ```

### **Issue 4: StockTwits 403 Errors**

#### **Symptoms:**
- "StockTwits sentiment analysis failed: 403 Forbidden"

#### **Solutions:**
1. **Rate Limiting**
   - Wait a few minutes and try again
   - Reduce number of tickers analyzed simultaneously

2. **User Agent Issues**
   - System automatically handles proper headers
   - No action needed from user

## 🧪 Testing & Debugging

### **Manual API Testing**

#### **Test Grok API**
```bash
# Replace YOUR_API_KEY with actual key
curl -X POST https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-beta",
    "messages": [{"role": "user", "content": "Analyze sentiment for AAPL stock"}],
    "max_tokens": 100
  }'
```

#### **Test Reddit API**
```python
import praw
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Btock Test"
)
# Should not raise an exception
subreddit = reddit.subreddit("stocks")
print("Reddit API working!")
```

### **Debug Mode in Application**

#### **Enable Detailed Logging**
1. Look for warning messages during sentiment analysis
2. Check specific API error messages
3. Note which APIs are failing vs working

#### **Check API Status**
The application shows which APIs are configured:
- ✅ Green checkmark = API working
- ❌ Red X = API not configured or failing

## 🚀 Railway Deployment Configuration

### **Setting Environment Variables**
1. Go to Railway Dashboard
2. Select your Btock project
3. Go to "Variables" tab
4. Add these variables:
   ```
   XAI_API_KEY=your_grok_api_key
   REDDIT_CLIENT_ID=your_reddit_client_id  
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=Btock Sentiment Analyzer v1.0
   ```
5. Click "Deploy" to restart with new variables

### **Verify Deployment**
1. Check deployment logs for errors
2. Test sentiment analysis after deployment
3. Look for "🚀 Live Mode Active" message

## 📞 Getting Help

### **If APIs Still Don't Work**
1. **Check API Documentation**
   - Grok API: https://x.ai/api
   - Reddit API: https://www.reddit.com/dev/api/

2. **Verify Account Status**
   - Ensure API accounts are active
   - Check for any usage limits or restrictions
   - Verify billing/payment status if required

3. **Test with Minimal Example**
   - Use simple curl commands to test APIs
   - Isolate whether issue is with keys or application

### **Alternative Approach**
If you can't get APIs working immediately:
1. **Start with One API**: Configure just Reddit or just Grok
2. **Gradual Setup**: Add APIs one by one
3. **Test Each Step**: Verify each API works before adding the next

## ✅ Success Indicators

### **When Everything is Working:**
- Message shows "🚀 Live Mode Active"
- Real sentiment data from social media platforms
- Varied, realistic sentiment scores
- No "demo mode" warnings
- API-specific data in X, Reddit, StockTwits columns

### **Expected Results:**
```
Ticker  X  Reddit  StockTwits  SentimentTotal       Sentiment
  AAPL  2      -1           3               4      🟡 Positive
  TSLA -1       0           1               0      ⚪ Neutral
  MSFT  1       2          -1               2      🟡 Positive
```

The sentiment scores will vary based on actual social media discussions and won't be the same every time you run the analysis.
