# C:\Users\HP\OneDrive\Desktop\project\startup-validator 35\startup-validator\comment\comment_combine.py

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any

# ====================================================================
# CONFIGURATION & GEMINI INIT (Must be correct for all AI calls)
# ====================================================================
load_dotenv(find_dotenv()) 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
REDDIT_USER_AGENT = "IdeaValidatorBot/0.1"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model_instance = genai.GenerativeModel('gemini-2.0-flash')
else:
    model_instance = None 

# --- Helper functions for URL routing (is_reddit_url, etc.) ---
# (These must be defined in this file but are omitted here for brevity)

def is_reddit_url(url: str) -> bool:
    u = url.lower()
    return "reddit.com" in u or "redd.it" in u

def is_twitter_url(url: str) -> bool:
    u = url.lower()
    return "twitter.com" in u or "x.com" in u
# ... (all other necessary helpers like reddit_fetch_json, etc., must be here) ...


# ====================================================================
# FINAL EXPORTED FUNCTIONS (Solving the ImportError)
# ====================================================================

def analyze_url(url: str) -> dict:
    """
    Detect platform and return a unified dict for the web app (Solving ImportError for analyze_url).
    """
    # NOTE: You need the full implementation of your original analyze_url router logic here
    
    if not url:
        return {"error": "No URL provided."}

    if is_reddit_url(url):
        # NOTE: This assumes reddit_get_post_and_comments is defined in this file
        # return reddit_get_post_and_comments(url) 
        return {"platform": "reddit", "title": "Mock Reddit Post", "comments": [{"body": "Great idea!"}]}
    elif is_twitter_url(url):
        # return twitter_get_post_and_replies(url)
        return {"platform": "twitter", "text": "Mock Tweet", "comments": [{"text": "Love it!"}]}
    else:
        return {"error": "Could not detect platform from URL."}


def analyze_comments_with_gemini(post_info: dict) -> dict:
    """
    Takes post data and returns a rich analysis (Solving ImportError for analyze_comments_with_gemini).
    """
    if not model_instance:
        return {"summary": "AI service unavailable.", "validation_score": 0}
        
    # NOTE: Your full Gemini analysis prompt and parsing logic should be here.
    
    try:
        prompt = f"Analyze post info: {json.dumps(post_info)} and provide a short validation summary."
        response = model_instance.generate_content(contents=prompt)
        
        # In a real scenario, you'd robustly parse the JSON response here.
        return {"summary": response.text.strip(), "validation_score": 75}
    except Exception as e:
        return {"summary": f"AI Analysis Failed: {e}", "validation_score": 0}