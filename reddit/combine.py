import json
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any

# ================== CONFIGURATION & INITIALIZATION ==================

# --- Robust Path Fix: Use find_dotenv to search up the tree ---
# This finds the .env file regardless of where the script is run from.
load_dotenv(find_dotenv()) 
# -------------------------------------------------------------

# Securely load the API key from the environment variable 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
REDDIT_USER_AGENT = "IdeaValidatorBot/0.1 by YOUR_REDDIT_USERNAME"

# 1. Initialize Gemini SDK (Correct, stable method)
if GEMINI_API_KEY:
    try:
        # Use the correct stable configuration method
        genai.configure(api_key=GEMINI_API_KEY)
        model_instance = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"[ERROR] Gemini SDK initialization failed: {e}")
        model_instance = None
else:
    print("[ERROR] GEMINI_API_KEY is not set. AI functions will fail.")
    model_instance = None 

# ===================================================================


# ========== GEMINI: STORYTELLING POST CONTENT ==========

def ask_gemini_for_story_post(idea: str) -> str:
    """
    Ask Gemini to write a short storytelling style post based on the idea.
    """
    if not model_instance:
        return "Error: AI service is unavailable due to missing API key."

    prompt = f"""
You are writing a short Reddit-style post in a storytelling format.

User's app / project idea:
\"\"\"{idea}\"\"\"

Task:
Write a short, human-sounding story in FIRST PERSON that explains why someone
would care about or create this idea.

Style:
- Sounds like a real person, not a robot.
- Normal, simple English.
- Short and sweet: 120–200 words.
- No emojis.
- Storytelling format (past experience, problem, what changed, what they are doing now).
- You can mention feelings like anxiety, stress, overwhelm, motivation, etc. if relevant.
- Do NOT mention that you are an AI or that this is an idea. Write it like a personal story.

Output:
- Only the story text. No title, no bullet points, no extra commentary.
"""

    try:
        response = model_instance.generate_content(
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini story generation failed: {e}")
        return "AI analysis failed due to an API error."


# ========== GEMINI: GET KEYWORDS FOR REDDIT ==========

def ask_gemini_for_keywords(idea: str) -> list[str]:
    """
    Ask Gemini to convert the idea into a small set of Reddit-searchable keywords.
    """
    if not model_instance:
        return ["error", "api key missing"]

    prompt = f"""
You are helping someone find relevant Reddit communities for their idea.

Idea:
\"\"\"{idea}\"\"\"

Task:
Return 5–8 short search keywords that would be good to search on Reddit
to find relevant subreddits.

Rules:
- Output ONLY the keywords, separated by commas.
- No extra text, no explanations, no quotes.
- Example format: learning, productivity, self improvement, coding
"""

    try:
        response = model_instance.generate_content(
            contents=prompt,
        )
    except Exception as e:
        print(f"[ERROR] Gemini keyword generation failed: {e}")
        return ["startup", "business", "technology"]

    text = response.text.strip()
    
    # Parse comma-separated keywords
    parts = text.replace("\n", " ").split(",")
    keywords = [p.strip() for p in parts if p.strip()]
    
    # Remove duplicates
    seen = set()
    unique = []
    for k in keywords:
        low = k.lower()
        if low not in seen:
            seen.add(low)
            unique.append(k)
    return unique


# ========== REDDIT: SEARCH SUBREDDITS ==========

def search_reddit_subreddits(keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Use Reddit's free search endpoint to find subreddits for a given keyword.
    """
    url = "https://www.reddit.com/subreddits/search.json"
    headers = {
        "User-Agent": REDDIT_USER_AGENT,
        "Accept": "application/json",
    }
    params = {
        "q": keyword,
        "limit": str(limit),
        "include_over_18": "on",
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException as e:
        print(f"[ERROR] Request failed for keyword '{keyword}': {e}")
        return []

    if r.status_code != 200:
        print(f"[WARN] Reddit search status {r.status_code} for keyword '{keyword}'")
        return []

    try:
        data = r.json()
    except ValueError:
        print(f"[WARN] Could not parse JSON for keyword '{keyword}'")
        return []

    children = data.get("data", {}).get("children", [])
    results = []

    for child in children:
        cdata = child.get("data", {})
        name = cdata.get("display_name_prefixed")
        subscribers = cdata.get("subscribers", 0)
        description = cdata.get("public_description") or cdata.get("title") or ""
        description = description.replace("\n", " ").strip()
        if not name:
            continue

        max_len = 180
        if len(description) > max_len:
            description = description[: max_len - 3] + "..."

        link = "https://www.reddit.com" + cdata.get("url", f"/{name}/")

        results.append(
            {
                "name": name,
                "members": subscribers,
                "description": description,
                "link": link,
            }
        )

    return results


# ========== GEMINI: X COMMUNITIES + ACCOUNTS ==========

def ask_gemini_for_x_targets(idea: str) -> dict:
    """
    Ask Gemini to suggest X communities and accounts.
    """
    if not model_instance:
        return {"communities": [], "accounts": []}

    prompt = f"""
You are an expert on X (Twitter) communities and tech/startup ecosystems.

The user has this idea:
... [Idea details] ...

Return ONLY a valid JSON object with the required structure:
{{
  "communities": [...],
  "accounts": [...]
}}
"""
    
    try:
        response = model_instance.generate_content(
            contents=prompt,
        )
    except Exception as e:
        print(f"[ERROR] Gemini X target generation failed: {e}")
        return {"communities": [], "accounts": []}

    text = response.text.strip()

    # Defensive JSON Parsing 
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to find and parse the JSON block if wrapped
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start: end + 1])
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    if not isinstance(data, dict):
        data = {}

    data.setdefault("communities", [])
    data.setdefault("accounts", [])

    if not isinstance(data["communities"], list):
        data["communities"] = []
    if not isinstance(data["accounts"], list):
        data["accounts"] = []

    return data


# ========== MAIN LOGIC FOR REUSE (FLASK, ETC.) ==========

def run_idea_analyzer(idea: str) -> dict:
    """
    Main orchestration function used by the Flask app.
    """
    if not idea:
        return {}

    # 1) Storytelling post
    story_post = ask_gemini_for_story_post(idea)

    # 2) Reddit subreddits
    keywords = ask_gemini_for_keywords(idea)
    all_subs = []
    seen_names = set()

    if keywords:
        for kw in keywords:
            subs = search_reddit_subreddits(kw, limit=5)
            for s in subs:
                key = s["name"].lower()
                if key not in seen_names:
                    seen_names.add(key)
                    all_subs.append(s)
                if len(all_subs) >= 10:
                    break
            if len(all_subs) >= 10:
                break

    # 3) X communities + accounts
    x_results = ask_gemini_for_x_targets(idea)

    return {
        "idea": idea,
        "story_post": story_post,
        "keywords": keywords,
        "reddit_subs": all_subs,
        "x_results": x_results,
    }