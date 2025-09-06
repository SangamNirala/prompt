from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import google.generativeai as genai
import asyncio
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class PromptEnhanceRequest(BaseModel):
    original_prompt: str
    enhancement_style: str = "creative"  # creative, technical, artistic, cinematic, detailed

class PromptEnhanceResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    enhanced_prompt: str
    enhancement_style: str
    enhancement_reasoning: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnhancementHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    enhanced_prompt: str
    enhancement_style: str
    enhancement_reasoning: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Enhancement Prompts for different styles
ENHANCEMENT_PROMPTS = {
    "creative": """
    You are an expert prompt engineer specializing in creative image generation. Transform the given prompt into a highly creative, imaginative, and visually stunning prompt that will produce exceptional AI-generated images.

    Guidelines:
    - Add rich visual details, artistic styles, and creative elements
    - Include lighting, composition, and atmospheric details
    - Suggest artistic techniques or famous artist inspirations
    - Make it vivid and imaginative while staying true to the core concept
    - Add creative twists that enhance the visual impact
    
    Original prompt: {original_prompt}
    
    Provide your response in this exact JSON format:
    {
        "enhanced_prompt": "your enhanced prompt here",
        "reasoning": "brief explanation of what you enhanced and why"
    }
    """,
    
    "technical": """
    You are an expert prompt engineer specializing in technical and detailed image generation. Transform the given prompt into a highly technical, precise, and detailed prompt with specific parameters.

    Guidelines:
    - Add technical specifications, camera settings, and rendering details
    - Include specific lighting setups, angles, and compositions
    - Add technical art terms and precise descriptors
    - Specify image quality, resolution, and rendering style
    - Include technical artistic techniques
    
    Original prompt: {original_prompt}
    
    Provide your response in this exact JSON format:
    {
        "enhanced_prompt": "your enhanced prompt here",
        "reasoning": "brief explanation of what you enhanced and why"
    }
    """,
    
    "artistic": """
    You are an expert prompt engineer specializing in artistic and aesthetic image generation. Transform the given prompt into a beautifully artistic prompt inspired by art history and aesthetic principles.

    Guidelines:
    - Reference famous artists, art movements, or artistic styles
    - Add aesthetic elements like color palettes, brushstrokes, textures
    - Include artistic composition techniques
    - Suggest art mediums and techniques
    - Create an emotionally resonant and aesthetically pleasing description
    
    Original prompt: {original_prompt}
    
    Provide your response in this exact JSON format:
    {
        "enhanced_prompt": "your enhanced prompt here",
        "reasoning": "brief explanation of what you enhanced and why"
    }
    """,
    
    "cinematic": """
    You are an expert prompt engineer specializing in cinematic and movie-like image generation. Transform the given prompt into a dramatic, cinematic prompt that would create movie-quality visuals.

    Guidelines:
    - Add cinematic lighting, camera angles, and shot types
    - Include mood, atmosphere, and dramatic elements
    - Reference cinematography techniques and film styles
    - Add depth, drama, and visual storytelling elements
    - Create a sense of narrative and emotional impact
    
    Original prompt: {original_prompt}
    
    Provide your response in this exact JSON format:
    {
        "enhanced_prompt": "your enhanced prompt here",
        "reasoning": "brief explanation of what you enhanced and why"
    }
    """,
    
    "detailed": """
    You are an expert prompt engineer specializing in extremely detailed and comprehensive image generation. Transform the given prompt into an incredibly detailed, specific, and comprehensive prompt.

    Guidelines:
    - Add extensive visual details about every element
    - Describe textures, materials, surfaces, and fine details
    - Include environmental details, background elements
    - Specify colors, shapes, sizes, and spatial relationships
    - Create a highly descriptive and immersive prompt
    
    Original prompt: {original_prompt}
    
    Provide your response in this exact JSON format:
    {
        "enhanced_prompt": "your enhanced prompt here",
        "reasoning": "brief explanation of what you enhanced and why"
    }
    """
}

def enhance_prompt_with_gemini(original_prompt: str, style: str) -> dict:
    """Enhanced prompt using Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        enhancement_prompt = ENHANCEMENT_PROMPTS.get(style, ENHANCEMENT_PROMPTS["creative"])
        formatted_prompt = enhancement_prompt.format(original_prompt=original_prompt)
        
        response = model.generate_content(formatted_prompt)
        response_text = response.text.strip()
        
        # Try to parse JSON response
        try:
            # Clean the response text
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return {
                "enhanced_prompt": result.get("enhanced_prompt", original_prompt),
                "reasoning": result.get("reasoning", "Enhanced with AI creativity")
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "enhanced_prompt": response_text,
                "reasoning": f"Enhanced using {style} style with AI creativity"
            }
            
    except Exception as e:
        logging.error(f"Error enhancing prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Quantum AI Prompt Enhancer - Ready to transcend creativity!"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/enhance-prompt", response_model=PromptEnhanceResponse)
async def enhance_prompt(request: PromptEnhanceRequest):
    """Enhance a prompt using Gemini AI"""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    if not request.original_prompt.strip():
        raise HTTPException(status_code=400, detail="Original prompt cannot be empty")
    
    try:
        # Enhance the prompt using Gemini
        enhancement_result = await enhance_prompt_with_gemini(
            request.original_prompt, 
            request.enhancement_style
        )
        
        # Create response object
        response = PromptEnhanceResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt=enhancement_result["enhanced_prompt"],
            enhancement_style=request.enhancement_style,
            enhancement_reasoning=enhancement_result["reasoning"]
        )
        
        # Save to database
        await db.enhancements.insert_one(response.dict())
        
        return response
        
    except Exception as e:
        logging.error(f"Enhancement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/enhancement-history", response_model=List[EnhancementHistory])
async def get_enhancement_history(limit: int = 50):
    """Get enhancement history"""
    try:
        enhancements = await db.enhancements.find().sort("timestamp", -1).limit(limit).to_list(limit)
        return [EnhancementHistory(**enhancement) for enhancement in enhancements]
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch enhancement history")

@api_router.get("/enhancement-styles")
async def get_enhancement_styles():
    """Get available enhancement styles"""
    return {
        "styles": [
            {"id": "creative", "name": "Creative", "description": "Imaginative and visually stunning enhancements"},
            {"id": "technical", "name": "Technical", "description": "Precise, detailed technical specifications"},
            {"id": "artistic", "name": "Artistic", "description": "Art-inspired with aesthetic principles"},
            {"id": "cinematic", "name": "Cinematic", "description": "Movie-quality dramatic visuals"},
            {"id": "detailed", "name": "Detailed", "description": "Extremely comprehensive descriptions"}
        ]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()