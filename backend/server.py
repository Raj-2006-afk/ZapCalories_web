from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import base64
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="ZapCalories API")

# Define CORS allowed origins. 
# Note: Using allow_origins=["*"] with allow_credentials=True triggers a Starlette/FastAPI RuntimeError,
# causing a 500 Internal Server Error. Specifying the exact origins resolves this error.
origins = [
    "https://www.zapcalories.com",
    "https://zapcalories.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Configure CORS Middleware immediately after app instantiation to intercept all pre-flight and routing requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'zap_calories')]

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
SECRET_KEY = os.environ.get('JWT_SECRET', secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# ==================== CONSTANTS ====================
FREE_SCAN_LIMIT = 2
PROMO_END_DATE = "2026-10-26"  # 50% discount until this date

# Pricing (in cents for precision)
PRICING = {
    "monthly": {
        "price": 999,  # $9.99
        "promo_price": 499,  # $4.99 (50% off)
        "scans_per_month": 100,
        "name": "Monthly",
        "period_days": 30
    },
    "quarterly": {
        "price": 2499,  # $24.99
        "promo_price": 1249,  # $12.49 (50% off)
        "scans_per_month": 100,
        "name": "Quarterly",
        "period_days": 90
    },
    "annual": {
        "price": 7999,  # $79.99
        "promo_price": 3999,  # $39.99 (50% off)
        "scans_per_month": -1,  # Unlimited
        "name": "Annual",
        "period_days": 365
    }
}

# Achievement definitions
ACHIEVEMENTS = {
    "first_scan": {"name": "First Bite", "description": "Complete your first food scan", "icon": "camera", "points": 10},
    "streak_3": {"name": "Getting Started", "description": "Maintain a 3-day streak", "icon": "fire", "points": 25},
    "streak_7": {"name": "Week Warrior", "description": "Maintain a 7-day streak", "icon": "fire", "points": 50},
    "streak_30": {"name": "Monthly Master", "description": "Maintain a 30-day streak", "icon": "trophy", "points": 200},
    "scans_10": {"name": "Scanner Pro", "description": "Scan 10 meals", "icon": "star", "points": 30},
    "scans_50": {"name": "Food Detective", "description": "Scan 50 meals", "icon": "search", "points": 100},
    "scans_100": {"name": "Nutrition Expert", "description": "Scan 100 meals", "icon": "award", "points": 250},
    "calories_goal": {"name": "Goal Crusher", "description": "Hit your calorie goal 5 times", "icon": "target", "points": 75},
    "protein_goal": {"name": "Protein Power", "description": "Hit protein goal 10 times", "icon": "muscle", "points": 100},
    "weight_loss_1": {"name": "First Pound", "description": "Lose your first kg", "icon": "scale", "points": 50},
    "weight_loss_5": {"name": "Transformation", "description": "Lose 5 kg", "icon": "medal", "points": 200},
    "subscriber": {"name": "Premium Member", "description": "Subscribe to ZapCalories", "icon": "crown", "points": 100},
    "share_first": {"name": "Social Butterfly", "description": "Share your first meal", "icon": "share", "points": 20},
}

# ==================== MODELS ====================

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Profile data
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal_weight: Optional[float] = None
    activity_level: Optional[str] = "moderate"
    
    # Subscription
    subscription_plan: Optional[str] = None  # 'monthly', 'quarterly', 'annual'
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    
    # Usage & Gamification
    free_scans_used: int = 0
    total_scans: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_scan_date: Optional[str] = None
    total_points: int = 0
    level: int = 1
    achievements: List[str] = Field(default_factory=list)
    goals_hit_calories: int = 0
    goals_hit_protein: int = 0
    shares_count: int = 0

class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal_weight: Optional[float] = None
    activity_level: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_end: Optional[datetime] = None
    free_scans_used: int = 0
    total_scans: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    total_points: int = 0
    level: int = 1
    achievements: List[str] = []

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal_weight: Optional[float] = None
    activity_level: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

class CalorieCalculation(BaseModel):
    bmr: float
    tdee: float
    goal_calories: float
    goal_type: str
    protein_goal: float
    carbs_goal: float
    fat_goal: float

class FoodAnalysis(BaseModel):
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: str
    confidence: float
    details: str

class FoodLogEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: str
    image_base64: Optional[str] = None
    meal_type: str = "snack"
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    shared: bool = False
    share_id: Optional[str] = None

class FoodLogCreate(BaseModel):
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float = 0
    serving_size: str
    image_base64: Optional[str] = None
    meal_type: str = "snack"

class DailyProgress(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    meal_count: int

class WeightEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    weight: float
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalyzeRequest(BaseModel):
    image_base64: str

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    points: int
    unlocked: bool
    unlocked_at: Optional[datetime] = None

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    name: str
    points: int
    level: int
    streak: int

class PricingPlan(BaseModel):
    id: str
    name: str
    price: float
    promo_price: float
    scans_per_month: int
    period_days: int
    is_promo_active: bool

class MealSuggestion(BaseModel):
    meal_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    description: str
    meal_type: str

class ShareMealRequest(BaseModel):
    log_id: str
    message: Optional[str] = None

class WeightLogRequest(BaseModel):
    weight: float

# ==================== HELPER FUNCTIONS ====================

def parse_ai_json_response(response: str) -> dict:
    clean_response = response.strip()
    if clean_response.startswith('```'):
        parts = clean_response.split('```')
        if len(parts) >= 2:
            clean_response = parts[1]
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
    clean_response = clean_response.strip()
    return json.loads(clean_response)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user_doc:
            return User(**user_doc)
        return None
    except JWTError:
        return None

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    user = await get_current_user(credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def is_promo_active() -> bool:
    promo_end = datetime.strptime(PROMO_END_DATE, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < promo_end

def can_scan(user: User) -> tuple[bool, str]:
    """Check if user can perform a scan"""
    # Check subscription
    if user.subscription_plan and user.subscription_end:
        if isinstance(user.subscription_end, str):
            sub_end = datetime.fromisoformat(user.subscription_end)
        else:
            sub_end = user.subscription_end
        if sub_end > datetime.now(timezone.utc):
            plan = PRICING.get(user.subscription_plan, {})
            if plan.get('scans_per_month', 0) == -1:  # Unlimited
                return True, "unlimited"
            # For monthly limits, we'd need to track monthly usage
            return True, "subscribed"
    
    # Check free scans
    if user.free_scans_used < FREE_SCAN_LIMIT:
        return True, "free"
    
    return False, "limit_reached"

def calculate_level(points: int) -> int:
    """Calculate user level based on points"""
    if points < 50:
        return 1
    elif points < 150:
        return 2
    elif points < 300:
        return 3
    elif points < 500:
        return 4
    elif points < 800:
        return 5
    elif points < 1200:
        return 6
    elif points < 1800:
        return 7
    elif points < 2500:
        return 8
    elif points < 3500:
        return 9
    else:
        return 10

async def check_and_award_achievements(user_id: str) -> List[str]:
    """Check and award new achievements"""
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        return []
    
    user = User(**user_doc)
    new_achievements = []
    
    # Check each achievement
    checks = [
        ("first_scan", user.total_scans >= 1),
        ("streak_3", user.current_streak >= 3),
        ("streak_7", user.current_streak >= 7),
        ("streak_30", user.current_streak >= 30),
        ("scans_10", user.total_scans >= 10),
        ("scans_50", user.total_scans >= 50),
        ("scans_100", user.total_scans >= 100),
        ("calories_goal", user.goals_hit_calories >= 5),
        ("protein_goal", user.goals_hit_protein >= 10),
        ("subscriber", user.subscription_plan is not None),
        ("share_first", user.shares_count >= 1),
    ]
    
    for achievement_id, condition in checks:
        if condition and achievement_id not in user.achievements:
            new_achievements.append(achievement_id)
            points = ACHIEVEMENTS[achievement_id]["points"]
            await db.users.update_one(
                {"id": user_id},
                {
                    "$push": {"achievements": achievement_id},
                    "$inc": {"total_points": points}
                }
            )
    
    # Update level
    if new_achievements:
        updated_user = await db.users.find_one({"id": user_id}, {"_id": 0})
        new_level = calculate_level(updated_user["total_points"])
        await db.users.update_one({"id": user_id}, {"$set": {"level": new_level}})
    
    return new_achievements

async def update_streak(user_id: str) -> int:
    """Update user's streak"""
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        return 0
    
    today = datetime.now(timezone.utc).date().isoformat()
    last_scan = user_doc.get("last_scan_date")
    current_streak = user_doc.get("current_streak", 0)
    
    if last_scan == today:
        # Already scanned today
        return current_streak
    
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    
    if last_scan == yesterday:
        # Continuing streak
        new_streak = current_streak + 1
    else:
        # Streak broken, start new
        new_streak = 1
    
    longest = max(user_doc.get("longest_streak", 0), new_streak)
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "current_streak": new_streak,
            "longest_streak": longest,
            "last_scan_date": today
        }}
    )
    
    return new_streak

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    if gender.lower() == 'male':
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return bmr * activity_multipliers.get(activity_level, 1.2)

def calculate_macros(goal_calories: float, goal_type: str) -> dict:
    if goal_type == 'loss':
        protein_pct, carbs_pct, fat_pct = 0.35, 0.35, 0.30
    elif goal_type == 'gain':
        protein_pct, carbs_pct, fat_pct = 0.30, 0.45, 0.25
    else:
        protein_pct, carbs_pct, fat_pct = 0.30, 0.40, 0.30
    
    return {
        'protein': (goal_calories * protein_pct) / 4,
        'carbs': (goal_calories * carbs_pct) / 4,
        'fat': (goal_calories * fat_pct) / 9
    }

async def analyze_food_with_ai(image_base64: str) -> FoodAnalysis:
    """Analyze food image using OpenAI GPT-4o"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    clean_base64 = image_base64
    if ',' in clean_base64:
        clean_base64 = clean_base64.split(',')[1]
    clean_base64 = clean_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="""You are an expert nutritionist for ZapCalories app. Analyze food images and provide accurate nutritional information.

Respond ONLY with valid JSON:
{
    "food_name": "Name of food",
    "calories": <number>,
    "protein": <grams>,
    "carbs": <grams>,
    "fat": <grams>,
    "fiber": <grams>,
    "serving_size": "estimated size",
    "confidence": <0-1>,
    "details": "Brief description"
}"""
        ).with_model("openai", "gpt-4o")
        
        image_content = ImageContent(image_base64=clean_base64)
        user_message = UserMessage(
            text="Analyze this food and provide nutritional information in JSON format.",
            file_contents=[image_content]
        )
        
        response = await chat.send_message(user_message)
        logger.info(f"AI Response: {response}")
        
        data = parse_ai_json_response(response)
        
        return FoodAnalysis(
            food_name=data.get('food_name', 'Unknown Food'),
            calories=float(data.get('calories', 0)),
            protein=float(data.get('protein', 0)),
            carbs=float(data.get('carbs', 0)),
            fat=float(data.get('fat', 0)),
            fiber=float(data.get('fiber', 0)),
            serving_size=data.get('serving_size', 'Unknown'),
            confidence=float(data.get('confidence', 0.5)),
            details=data.get('details', '')
        )
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response")
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Food analysis failed: {str(e)}")

async def get_ai_meal_suggestions(remaining_calories: float, remaining_protein: float, remaining_carbs: float, remaining_fat: float, meal_type: str) -> List[MealSuggestion]:
    """Get AI-powered meal suggestions based on remaining macros"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return []
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="You are a nutritionist helping users meet their daily macro goals."
        ).with_model("openai", "gpt-4o")
        
        prompt = f"""Suggest 3 {meal_type} meals that fit these remaining daily macros:
- Calories: {remaining_calories:.0f} kcal
- Protein: {remaining_protein:.0f}g
- Carbs: {remaining_carbs:.0f}g
- Fat: {remaining_fat:.0f}g

Respond with JSON array:
[{{
    "meal_name": "name",
    "calories": <number>,
    "protein": <grams>,
    "carbs": <grams>,
    "fat": <grams>,
    "description": "brief description",
    "meal_type": "{meal_type}"
}}]"""
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        data = parse_ai_json_response(response)
        return [MealSuggestion(**item) for item in data]
    except Exception as e:
        logger.error(f"Meal suggestion failed: {e}")
        return []

# ==================== API ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "ZapCalories API", "version": "1.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if email exists
    existing = await db.users.find_one({"email": user_data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email.lower(),
        name=user_data.name,
        password_hash=hash_password(user_data.password)
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    token = create_access_token({"sub": user.id})
    
    return TokenResponse(
        access_token=token,
        user=UserPublic(**user.model_dump())
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email.lower()}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": user_doc["id"]})
    
    return TokenResponse(
        access_token=token,
        user=UserPublic(**user_doc)
    )

@api_router.get("/auth/me", response_model=UserPublic)
async def get_me(user: User = Depends(require_auth)):
    return UserPublic(**user.model_dump())

# ==================== PROFILE ROUTES ====================

@api_router.put("/profile", response_model=UserPublic)
async def update_profile(profile: ProfileUpdate, user: User = Depends(require_auth)):
    update_data = {k: v for k, v in profile.model_dump().items() if v is not None}
    
    if update_data:
        await db.users.update_one({"id": user.id}, {"$set": update_data})
    
    updated = await db.users.find_one({"id": user.id}, {"_id": 0})
    return UserPublic(**updated)

@api_router.get("/calculate-tdee", response_model=CalorieCalculation)
async def calculate_tdee_endpoint(user: User = Depends(require_auth)):
    if not all([user.weight, user.height, user.age, user.gender]):
        raise HTTPException(status_code=400, detail="Complete your profile first")
    
    bmr = calculate_bmr(user.weight, user.height, user.age, user.gender)
    tdee = calculate_tdee(bmr, user.activity_level or "moderate")
    
    weight_diff = (user.goal_weight or user.weight) - user.weight
    if weight_diff < -2:
        goal_type = 'loss'
        goal_calories = tdee - 500
    elif weight_diff > 2:
        goal_type = 'gain'
        goal_calories = tdee + 300
    else:
        goal_type = 'maintain'
        goal_calories = tdee
    
    macros = calculate_macros(goal_calories, goal_type)
    
    return CalorieCalculation(
        bmr=round(bmr, 0),
        tdee=round(tdee, 0),
        goal_calories=round(goal_calories, 0),
        goal_type=goal_type,
        protein_goal=round(macros['protein'], 0),
        carbs_goal=round(macros['carbs'], 0),
        fat_goal=round(macros['fat'], 0)
    )

# ==================== SUBSCRIPTION & PRICING ====================

@api_router.get("/pricing", response_model=List[PricingPlan])
async def get_pricing():
    promo_active = is_promo_active()
    plans = []
    for plan_id, plan in PRICING.items():
        plans.append(PricingPlan(
            id=plan_id,
            name=plan["name"],
            price=plan["price"] / 100,
            promo_price=plan["promo_price"] / 100,
            scans_per_month=plan["scans_per_month"],
            period_days=plan["period_days"],
            is_promo_active=promo_active
        ))
    return plans

@api_router.get("/subscription/status")
async def get_subscription_status(user: User = Depends(require_auth)):
    can_use, reason = can_scan(user)
    
    return {
        "has_subscription": user.subscription_plan is not None,
        "plan": user.subscription_plan,
        "subscription_end": user.subscription_end,
        "free_scans_used": user.free_scans_used,
        "free_scans_remaining": max(0, FREE_SCAN_LIMIT - user.free_scans_used),
        "can_scan": can_use,
        "reason": reason,
        "total_scans": user.total_scans
    }

@api_router.post("/subscription/activate")
async def activate_subscription(plan_id: str, user: User = Depends(require_auth)):
    """Activate subscription (mock - ready for Stripe integration)"""
    if plan_id not in PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = PRICING[plan_id]
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=plan["period_days"])
    
    await db.users.update_one(
        {"id": user.id},
        {"$set": {
            "subscription_plan": plan_id,
            "subscription_start": now.isoformat(),
            "subscription_end": end_date.isoformat()
        }}
    )
    
    # Award subscriber achievement
    await check_and_award_achievements(user.id)
    
    return {
        "success": True,
        "plan": plan_id,
        "subscription_end": end_date.isoformat(),
        "message": "Subscription activated! (Mock - Stripe integration pending)"
    }

# ==================== FOOD ANALYSIS ====================

@api_router.post("/analyze-food", response_model=FoodAnalysis)
async def analyze_food(request: AnalyzeRequest, user: User = Depends(require_auth)):
    # Check if user can scan
    can_use, reason = can_scan(user)
    
    if not can_use:
        raise HTTPException(
            status_code=403,
            detail="Scan limit reached. Please subscribe to continue scanning."
        )
    
    # Perform analysis
    result = await analyze_food_with_ai(request.image_base64)
    
    # Update usage
    update_data = {"$inc": {"total_scans": 1}}
    if reason == "free":
        update_data["$inc"]["free_scans_used"] = 1
    
    await db.users.update_one({"id": user.id}, update_data)
    
    # Update streak
    await update_streak(user.id)
    
    # Check achievements
    await check_and_award_achievements(user.id)
    
    return result

# ==================== FOOD LOG ====================

@api_router.post("/food-log", response_model=FoodLogEntry)
async def create_food_log(entry: FoodLogCreate, user: User = Depends(require_auth)):
    log_entry = FoodLogEntry(
        user_id=user.id,
        **entry.model_dump()
    )
    
    doc = log_entry.model_dump()
    doc['logged_at'] = doc['logged_at'].isoformat()
    
    if doc.get('image_base64') and len(doc['image_base64']) > 5000000:
        doc['image_base64'] = None
    
    await db.food_logs.insert_one(doc)
    return log_entry

@api_router.get("/food-log", response_model=List[FoodLogEntry])
async def get_food_logs(user: User = Depends(require_auth), date: Optional[str] = None, limit: int = 50):
    query = {"user_id": user.id}
    if date:
        start = datetime.fromisoformat(f"{date}T00:00:00+00:00")
        end = datetime.fromisoformat(f"{date}T23:59:59+00:00")
        query['logged_at'] = {'$gte': start.isoformat(), '$lte': end.isoformat()}
    
    logs = await db.food_logs.find(query, {"_id": 0}).sort("logged_at", -1).limit(limit).to_list(limit)
    
    for log in logs:
        if isinstance(log.get('logged_at'), str):
            log['logged_at'] = datetime.fromisoformat(log['logged_at'])
    
    return logs

@api_router.get("/food-log/today", response_model=List[FoodLogEntry])
async def get_today_logs(user: User = Depends(require_auth)):
    today = datetime.now(timezone.utc).date().isoformat()
    return await get_food_logs(user=user, date=today)

@api_router.delete("/food-log/{log_id}")
async def delete_food_log(log_id: str, user: User = Depends(require_auth)):
    result = await db.food_logs.delete_one({"id": log_id, "user_id": user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Deleted"}

# ==================== PROGRESS ====================

@api_router.get("/daily-progress", response_model=DailyProgress)
async def get_daily_progress(user: User = Depends(require_auth), date: Optional[str] = None):
    if not date:
        date = datetime.now(timezone.utc).date().isoformat()
    
    logs = await get_food_logs(user=user, date=date, limit=100)
    
    total_calories = sum(log['calories'] for log in logs)
    total_protein = sum(log['protein'] for log in logs)
    total_carbs = sum(log['carbs'] for log in logs)
    total_fat = sum(log['fat'] for log in logs)
    
    return DailyProgress(
        date=date,
        total_calories=round(total_calories, 1),
        total_protein=round(total_protein, 1),
        total_carbs=round(total_carbs, 1),
        total_fat=round(total_fat, 1),
        meal_count=len(logs)
    )

@api_router.get("/weekly-progress", response_model=List[DailyProgress])
async def get_weekly_progress(user: User = Depends(require_auth)):
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=6)
    
    start_iso = datetime.fromisoformat(f"{start_date.isoformat()}T00:00:00+00:00").isoformat()
    end_iso = datetime.fromisoformat(f"{today.isoformat()}T23:59:59+00:00").isoformat()
    
    logs = await db.food_logs.find({
        "user_id": user.id,
        "logged_at": {"$gte": start_iso, "$lte": end_iso}
    }, {"_id": 0}).to_list(1000)
    
    # Group by date
    progress_dict = {}
    for i in range(7):
        d = (today - timedelta(days=i)).isoformat()
        progress_dict[d] = {"total_calories": 0, "total_protein": 0, "total_carbs": 0, "total_fat": 0, "meal_count": 0}
        
    for log in logs:
        if isinstance(log.get('logged_at'), str):
            log_date = datetime.fromisoformat(log['logged_at']).date().isoformat()
        else:
            log_date = log['logged_at'].date().isoformat()
            
        if log_date in progress_dict:
            progress_dict[log_date]["total_calories"] += log.get('calories', 0)
            progress_dict[log_date]["total_protein"] += log.get('protein', 0)
            progress_dict[log_date]["total_carbs"] += log.get('carbs', 0)
            progress_dict[log_date]["total_fat"] += log.get('fat', 0)
            progress_dict[log_date]["meal_count"] += 1
            
    progress = []
    for i in range(7):
        d = (today - timedelta(days=i)).isoformat()
        p = progress_dict[d]
        progress.append(DailyProgress(
            date=d,
            total_calories=round(p["total_calories"], 1),
            total_protein=round(p["total_protein"], 1),
            total_carbs=round(p["total_carbs"], 1),
            total_fat=round(p["total_fat"], 1),
            meal_count=p["meal_count"]
        ))
    
    return progress

# ==================== WEIGHT ====================

@api_router.post("/weight", response_model=WeightEntry)
async def log_weight(request: WeightLogRequest, user: User = Depends(require_auth)):
    entry = WeightEntry(user_id=user.id, weight=request.weight)
    doc = entry.model_dump()
    doc['recorded_at'] = doc['recorded_at'].isoformat()
    
    await db.weight_logs.insert_one(doc)
    await db.users.update_one({"id": user.id}, {"$set": {"weight": request.weight}})
    
    # Check weight loss achievements
    first_weight = await db.weight_logs.find_one(
        {"user_id": user.id},
        sort=[("recorded_at", 1)]
    )
    if first_weight:
        weight_lost = first_weight["weight"] - request.weight
        if weight_lost >= 1:
            await check_and_award_achievements(user.id)
    
    return entry

@api_router.get("/weight-history", response_model=List[WeightEntry])
async def get_weight_history(user: User = Depends(require_auth), limit: int = 30):
    entries = await db.weight_logs.find(
        {"user_id": user.id}, {"_id": 0}
    ).sort("recorded_at", -1).limit(limit).to_list(limit)
    
    for entry in entries:
        if isinstance(entry.get('recorded_at'), str):
            entry['recorded_at'] = datetime.fromisoformat(entry['recorded_at'])
    
    return entries

# ==================== GAMIFICATION ====================

@api_router.get("/achievements", response_model=List[Achievement])
async def get_achievements(user: User = Depends(require_auth)):
    achievements = []
    for ach_id, ach in ACHIEVEMENTS.items():
        achievements.append(Achievement(
            id=ach_id,
            name=ach["name"],
            description=ach["description"],
            icon=ach["icon"],
            points=ach["points"],
            unlocked=ach_id in user.achievements
        ))
    return achievements

@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 20):
    users = await db.users.find(
        {},
        {"_id": 0, "id": 1, "name": 1, "total_points": 1, "level": 1, "current_streak": 1}
    ).sort("total_points", -1).limit(limit).to_list(limit)
    
    leaderboard = []
    for i, u in enumerate(users):
        leaderboard.append(LeaderboardEntry(
            rank=i + 1,
            user_id=u["id"],
            name=u.get("name", "Anonymous"),
            points=u.get("total_points", 0),
            level=u.get("level", 1),
            streak=u.get("current_streak", 0)
        ))
    return leaderboard

@api_router.get("/stats")
async def get_user_stats(user: User = Depends(require_auth)):
    return {
        "total_scans": user.total_scans,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "total_points": user.total_points,
        "level": user.level,
        "achievements_unlocked": len(user.achievements),
        "total_achievements": len(ACHIEVEMENTS)
    }

# ==================== SOCIAL ====================

@api_router.post("/share-meal")
async def share_meal(request: ShareMealRequest, user: User = Depends(require_auth)):
    log = await db.food_logs.find_one({"id": request.log_id, "user_id": user.id})
    if not log:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    share_id = str(uuid.uuid4())[:8]
    
    await db.food_logs.update_one(
        {"id": request.log_id},
        {"$set": {"shared": True, "share_id": share_id}}
    )
    
    await db.users.update_one(
        {"id": user.id},
        {"$inc": {"shares_count": 1}}
    )
    
    await check_and_award_achievements(user.id)
    
    return {
        "share_id": share_id,
        "share_url": f"/shared/{share_id}",
        "message": request.message
    }

@api_router.get("/shared/{share_id}")
async def get_shared_meal(share_id: str):
    log = await db.food_logs.find_one({"share_id": share_id, "shared": True}, {"_id": 0})
    if not log:
        raise HTTPException(status_code=404, detail="Shared meal not found")
    
    user = await db.users.find_one({"id": log["user_id"]}, {"_id": 0, "name": 1})
    
    return {
        "food_name": log["food_name"],
        "calories": log["calories"],
        "protein": log["protein"],
        "carbs": log["carbs"],
        "fat": log["fat"],
        "serving_size": log["serving_size"],
        "meal_type": log["meal_type"],
        "shared_by": user.get("name", "A ZapCalories user") if user else "A ZapCalories user"
    }

# ==================== AI SUGGESTIONS ====================

@api_router.get("/meal-suggestions", response_model=List[MealSuggestion])
async def get_meal_suggestions(meal_type: str = "lunch", user: User = Depends(require_auth)):
    try:
        tdee = await calculate_tdee_endpoint(user)
        progress = await get_daily_progress(user=user)
        
        remaining_cal = tdee.goal_calories - progress.total_calories
        remaining_protein = tdee.protein_goal - progress.total_protein
        remaining_carbs = tdee.carbs_goal - progress.total_carbs
        remaining_fat = tdee.fat_goal - progress.total_fat
        
        if remaining_cal <= 0:
            return []
        
        suggestions = await get_ai_meal_suggestions(
            remaining_cal, remaining_protein, remaining_carbs, remaining_fat, meal_type
        )
        return suggestions
    except Exception as e:
        logger.error(f"Meal suggestions error: {e}")
        return []

# Include router
app.include_router(api_router)

@app.on_event("startup")
async def startup_db_client():
    # Create indexes for performance
    await db.users.create_index("id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.food_logs.create_index("id", unique=True)
    await db.food_logs.create_index("user_id")
    await db.food_logs.create_index("logged_at")
    await db.weight_logs.create_index("user_id")
    await db.weight_logs.create_index("recorded_at")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
