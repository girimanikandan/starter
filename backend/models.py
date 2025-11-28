"""
Data Models using Pydantic
---------------------------
Defines structure for all data objects in the application
Provides automatic validation and serialization
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# ============================================
# INPUT MODELS (From Frontend Form)
# ============================================

class IdeaInput(BaseModel):
    """
    Raw input from user form
    All fields that user fills in the frontend
    """
    idea_name: str
    problem: str
    why_problem_exists: str
    target_audience: str
    solution: str
    key_features: str
    uniqueness: str
    market: str
    revenue_model: str
    expected_users: str
    region: str
    extra_notes: Optional[str] = ""

# ============================================
# PROCESSED MODELS (After Gemini Processing)
# ============================================

class ProcessedInput(BaseModel):
    """
    Cleaned and structured input after Gemini processing
    This is what we use for further analysis
    """
    idea_name: str
    problem: str
    solution: str
    target_audience: str
    uniqueness: str
    market: str
    revenue_model: str
    region: str
    additional_context: str  # Combined from other fields

# ============================================
# COMPETITOR ANALYSIS MODELS
# ============================================

class CompetitorInfo(BaseModel):
    """
    Information about each competitor
    Extracted from web search and scraping
    """
    name: str
    url: Optional[str] = ""
    description: str
    founders: Optional[str] = "Unknown"
    revenue: Optional[str] = "Unknown"
    region: Optional[str] = "Unknown"
    features: List[str] = []

# ============================================
# WEB RESEARCH MODELS
# ============================================

class WebResearchData(BaseModel):
    """
    All data collected from web research
    Combines Serper and Firecrawl results
    """
    serper_results: List[Dict[str, Any]]     # Raw search results
    firecrawl_results: List[Dict[str, Any]]  # Scraped website data
    competitors: List[CompetitorInfo]         # Structured competitor info
    market_insights: Dict[str, Any]           # Market statistics

# ============================================
# VALIDATION SUMMARY MODELS
# ============================================

class ValidationSummary(BaseModel):
    """
    Final AI-generated validation summary
    Contains all analysis and recommendations
    """
    overview: str                             # Executive summary
    feasibility_score: int                    # 1-100
    market_readiness_score: int               # 1-100
    swot_analysis: Dict[str, List[str]]      # Strengths, Weaknesses, Opportunities, Threats
    risk_analysis: List[str]                  # Identified risks
    recommendations: List[str]                # Action items
    competitive_advantage: str                # How to stand out
    market_size_estimate: str                 # TAM/SAM/SOM

# ============================================
# COMPLETE VALIDATION REPORT
# ============================================

class ValidationReport(BaseModel):
    """
    Complete validation report
    This is what gets saved to MongoDB
    """
    id: Optional[str] = Field(alias="_id", default=None)
    user_input: IdeaInput                     # Original form data
    processed_input: ProcessedInput           # Cleaned data
    web_research: WebResearchData             # Research results
    final_summary: ValidationSummary          # AI analysis
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }