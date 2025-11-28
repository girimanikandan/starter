"""
FastAPI Main Application
-------------------------
The main backend server

ENDPOINTS:
- POST /api/validate → Validate a startup idea
- GET /api/reports → Get all validation reports
- GET /api/reports/{id} → Get specific report
- DELETE /api/reports/{id} → Delete a report
- GET /api/health → Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime
from bson import ObjectId

from config import get_settings
from database import Database, VALIDATIONS_COLLECTION
from models import IdeaInput, ValidationReport
from services.validator import ValidationService

settings = get_settings()

# ============================================
# APPLICATION LIFECYCLE
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown
    
    Startup: Connect to MongoDB
    Shutdown: Close MongoDB connection
    """
    # Startup
    print("\n🚀 Starting Startup Idea Validator API...")
    await Database.connect_db()
    print("✅ Application ready!\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down...")
    await Database.close_db()
    print("✅ Cleanup complete!\n")

# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="Startup Idea Validator API",
    description="AI-powered startup idea validation using Gemini, Serper, and Firecrawl",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================
# CORS MIDDLEWARE (Allow frontend to call API)
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize validation service
validation_service = ValidationService()

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """
    Root endpoint - API info
    """
    return {
        "message": "Startup Idea Validator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "validate": "POST /api/validate",
            "reports": "GET /api/reports",
            "health": "GET /api/health"
        }
    }

@app.post("/api/validate")
async def validate_idea(idea_input: IdeaInput):
    """
    🎯 MAIN ENDPOINT: Validate a startup idea
    
    This is the core function that:
    1. Takes user input
    2. Runs complete validation workflow
    3. Saves to MongoDB
    4. Returns results
    
    Request Body: IdeaInput (all form fields)
    Response: Complete validation report
    """
    try:
        print("\n" + "="*60)
        print("📥 NEW VALIDATION REQUEST RECEIVED")
        print(f"   Idea: {idea_input.idea_name}")
        print(f"   Market: {idea_input.market}")
        print("="*60)
        
        # Run validation workflow
        validation_report = await validation_service.validate_idea(idea_input)
        
        # Save to MongoDB
        print("💾 Saving to MongoDB...")
        collection = Database.get_collection(VALIDATIONS_COLLECTION)
        report_dict = validation_report.dict(by_alias=True, exclude={"id"})
        result = await collection.insert_one(report_dict)
        print(f"   ✅ Saved with ID: {result.inserted_id}\n")
        
        # Add MongoDB ID to response
        validation_report_dict = validation_report.model_dump()
        validation_report_dict["_id"] = str(result.inserted_id)
        
        return {
            "success": True,
            "message": "Validation completed successfully",
            "report_id": str(result.inserted_id),
            "data": validation_report_dict
        }
        
    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {str(e)}\n")
        raise HTTPException(
            status_code=500, 
            detail=f"Validation failed: {str(e)}"
        )

@app.get("/api/reports")
async def get_all_reports(limit: int = 10, skip: int = 0):
    """
    Get all validation reports
    
    Query Parameters:
    - limit: Number of reports to return (default: 10)
    - skip: Number of reports to skip (for pagination)
    
    Returns: List of validation reports
    """
    try:
        collection = Database.get_collection(VALIDATIONS_COLLECTION)
        
        # Get reports sorted by creation date (newest first)
        cursor = collection.find().sort("created_at", -1).skip(skip).limit(limit)
        reports = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for report in reports:
            report["_id"] = str(report["_id"])
        
        # Get total count
        total = await collection.count_documents({})
        
        return {
            "success": True,
            "data": reports,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch reports: {str(e)}"
        )

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """
    Get a specific validation report by ID
    
    Path Parameter:
    - report_id: MongoDB document ID
    
    Returns: Single validation report
    """
    try:
        collection = Database.get_collection(VALIDATIONS_COLLECTION)
        report = await collection.find_one({"_id": ObjectId(report_id)})
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Convert ObjectId to string
        report["_id"] = str(report["_id"])
        
        return {
            "success": True,
            "data": report
        }
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch report: {str(e)}"
        )

@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a validation report
    
    Path Parameter:
    - report_id: MongoDB document ID
    
    Returns: Success message
    """
    try:
        collection = Database.get_collection(VALIDATIONS_COLLECTION)
        result = await collection.delete_one({"_id": ObjectId(report_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "message": "Report deleted successfully"
        }
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete report: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    
    Checks:
    - API is running
    - MongoDB connection is active
    
    Returns: Health status
    """
    try:
        # Test database connection
        db = Database.get_database()
        await db.command("ping")
        
        return {
            "status": "healthy",
            "api": "running",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api": "running",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================
# RUN THE SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         🚀 STARTUP IDEA VALIDATOR API 🚀                 ║
    ║                                                           ║
    ║  Server starting at: http://localhost:8000                ║
    ║  API Docs: http://localhost:8000/docs                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level="info"
    )