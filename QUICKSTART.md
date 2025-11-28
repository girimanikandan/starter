# ⚡ Quick Start Guide - Get Running in 5 Minutes

## Step 1: Install MongoDB
```bash
# Windows
# Download from: https://www.mongodb.com/try/download/community
# Install and run: net start MongoDB

# Mac
brew install mongodb-community
brew services start mongodb-community

# Linux
sudo apt-get install mongodb
sudo systemctl start mongod
```

## Step 2: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## Step 3: Create .env File
Create `backend/.env`:
```env
GEMINI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=startup_validator
```

**Get API Keys:**
- Gemini: https://makersuite.google.com/app/apikey
- Serper: https://serper.dev/
- Firecrawl: https://firecrawl.dev/

## Step 4: Run Backend
```bash
cd backend
python app.py
```

Wait for:
```
✅ Connected to MongoDB
✅ Application ready!
Server starting at: http://localhost:8000
```

## Step 5: Open Frontend
Double-click `frontend/index.html` in your browser

## Step 6: Test It!
1. Fill the form with your startup idea
2. Click "Validate My Idea"
3. Wait 30-60 seconds
4. View your validation report!

---

## 🧪 Test Example

Use this to test if everything works:

**Idea Name:** AI Meal Planner  
**Problem:** People struggle with healthy eating habits  
**Why it exists:** Lack of time and knowledge about nutrition  
**Target Audience:** Busy professionals aged 25-45  
**Solution:** AI-powered personalized meal planning  
**Key Features:** Recipe suggestions, grocery lists, nutrition tracking  
**Uniqueness:** Uses AI to adapt to dietary restrictions  
**Market:** Health & Wellness  
**Revenue Model:** Subscription $9.99/month  
**Expected Users:** 50K in year 1  
**Region:** United States  

---

## 🐛 Common Issues

**MongoDB not connecting?**
```bash
# Check if MongoDB is running
mongosh
# If error, start MongoDB service
```

**Port 8000 already in use?**
```bash
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**API errors?**
- Check all API keys in .env
- No spaces or quotes
- Valid keys

---

## 📖 Full Documentation
See `README.md` for complete details!

---

**That's it! You're ready to validate startup ideas! 🚀**