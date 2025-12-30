import asyncio
import logging
import json
import requests
import secrets
import time
import html
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

try:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "osint-b432e",
        "private_key_id": "f8251ea8b6e6f399c240ec7aa7d2a690f7ac858a",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxruRz5LWSUqKo\n5vfbpMkdf0iuLcPwk5GEkrJgJN6k2kpFuGsQP1cPb1JA0N3vuKSFGJFC2pXeAxUz\n52Vku9+98otexNdvELJKcrzIapXC/lccuzlkr9SVPSzaGS30fyOFXiYLFA6vJKya\nP8e/Op4fTKZrFkMuTjCcVEXt2U0Bvmc/vjYckmVQfF66KpVvkCr8moSU5Z2UghjR\nHElTHqfHUzYi53RsAs4KoFPfCVrsqAFbkPbB59ZHF1t37FK3n0kIOaP1EuIZRUca\ntxG3VM1segGwFxY+Xvt5vnpBlYXi4zytDUkmCio95XKKS1+8ViMNlpBZDO0JQ7wR\nWsEZr0e3AgMBAAECggEAB2KhlD+ZXG+a2zJecv6ybUtxFexJDKLVlZETYPOnXWrF\nU4iKyq4XTEjwPklwMBqYm/+dag3z1LqEExg3GqzEa/y81j+QRMmI35dNSXdEqkow\nDL2rcQft6hYU2yvYwSTXsR9srWE0CwuXMQIdp1EkaWCiOik+uZn+Y0ENdwllLgFO\nQEIHZQtxefn4/QNF7ITx+tKd/ZY4CWhEwegVHNxpwaP3W6WAkILZ18aeEM9MuFq8\nf8URviyWYUCkgmozklPAECR4g2U3WYKsDxBWm4C+GyQiOMY3syF0/nLtjvdJLN2L\nQgfK0+OOS8M524rm5aFlVNxpuTZgSBRlFAa1Fgpa4QKBgQDgyxshY4ciHagkSKHl\nlEPTW9aQaKT6ZbQ31UTaGMDIJj1K2Q2mVD4J6cficSHXaPhSY1AxNMa0KprUc4pH\nhjAz7L3O4wP+yosfi+ZraCSy9IOcShVxzMM+4ftOrL5WLnMl63OlQ336kWooxiDR\nnCyRduCZC8v/1wfnDqISwi5XQwKBgQDKWYtuR0AHq4zmtYzsBeIZP1i9pUdAWgGN\nU1n4WWyqDlDYJy9+lcGJnTsi6pSrBK1ZBmP3Plf3FW+Uo4RxBGM0UZDSc6JdmbiA\n3Pf2xUmDvIuB4gSa60wHyQPT0Ig699j1Vu3D3jBByCgO3OfJ2LXiMu28IUMKqbZF\nvxOMcF3kfQKBgAZc2Vy9k3KcwkicobB83Nqbq9wUii7oOAyohbVio/pGUs/Oivtd\nQRBIxLadGyccuoKiev+ZjdJFrnI6/vv9SVn+5nR3qoJIu11eOVxq6zcBgsQmuKqq\n8A/Ul6dnbk/EKtA09OYFngg8m3OiAAXO1NgdNEhAtDp+nKOmn2HGi0c/AoGAe3pZ\nE1p3QDb3LHHtJLoSVsXJKTEKYcKK3+rVJC+tl7hUrRJ8cQqBp7BCvfPX9ORNw92a\ncu2gUC7MgC+oSi8bOnnrngDiO6vqYvh0eCm7yp/rob6CgObE5ptLsp22BAXqZww8\n2yFi4UF68FbtOsb7dqUNXZgOiRs3FyiajUCkiyECgYEArYEs+nG3T01o+AIEyfyq\nn6NP8IDFQv5RaWqkPTeDU7C+5dwjXVNAlwE4C5A5BraU+Kl8F8A+RLSuIPz0/AAU\nWCbdjiXCO1j1nZejdXq0ZF6YmNWJLbYHpY+fUzi6E7K3ESzVicMOc5kndtKw3URK\np/OMN5aMn3Mo/BkSF/t7XcU=\n-----END PRIVATE KEY-----",
        "client_email": "firebase-adminsdk-fbsvc@osint-b432e.iam.gserviceaccount.com",
        "client_id": "102637178508931850178",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40osint-b432e.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    })

    firebase_admin.initialize_app(cred)
    FIREBASE_ENABLED = True
    print("🔥 Firebase initialized successfully")

except Exception as e:
    FIREBASE_ENABLED = False
    print(f"❌ Firebase Error: {e}")

db = firestore.client() if FIREBASE_ENABLED else None

BOT_TOKEN = os.getenv("BOT_TOKEN", "8314571822:AAFBfXbeWE5gXykPBni_RQL31grg_M1rclY")
BOT_USERNAME = "@IntelSphereX_Bot"
ADMIN_IDS = [7255220723]
SUPPORT_USER_ID = 7255220723
LOG_CHANNEL_ID = -1003592661456

START_IMAGE_URL = "https://i.ibb.co/dwW1by6R/osint-banner.jpg"
MENU_IMAGE_URL = "https://i.ibb.co/dwW1by6R/osint-banner.jpg"
BUY_IMAGE_URL = "https://ibb.co/RknmxtSb"

CHANNEL_1_INVITE_LINK = "https://t.me/DarkByteNet"
REQUIRED_CHANNEL_1_ID = -1002906038515
CHANNEL_2_INVITE_LINK = "https://t.me/BinaryRebel"
REQUIRED_CHANNEL_2_ID = -1002801307481
CHANNEL_4_INVITE_LINK = "https://t.me/IntelSphereX"
REQUIRED_CHANNEL_4_ID = -1003202408148

PHONE_API_ENDPOINT = "https://number.gauravyt566.workers.dev/?number={term}"
PAK_PHONE_API_ENDPOINT = "https://pak-info.gauravyt566.workers.dev/?num={term}"
AADHAAR_API_ENDPOINT = "https://aadhaar.gauravyt566.workers.dev/?aadhaar={term}"
FAMILY_INFO_API_ENDPOINT = "https://family-zeprexxx.gauravyt566.workers.dev?aadhaar={term}"
IFSC_API_ENDPOINT = "https://ifsc-info.gauravyt492.workers.dev/?ifsc={term}"
IP_API_ENDPOINT = "https://ip-info.gauravyt566.workers.dev/?ip={term}"
TG_INFO_API_ENDPOINT = "https://tginfo-zionix.vercel.app/user-details?user={term}"
PAK_FAMILY_API_ENDPOINT = "https://paknuminfo-by-narcos.vercel.app/api/familyinfo?cnic={term}"
GST_API_ENDPOINT = 'https://gst.gauravyt492.workers.dev/?gst={term}'
PAN_API_ENDPOINT = 'https://pan.gauravyt566.workers.dev/?pan={term}'
RC_MOBILE_API_ENDPOINT = 'https://vh.gauravyt566.workers.dev/?key=Gaurav&reg={term}'
IMEI_API_ENDPOINT = 'https://imei-info.gauravyt566.workers.dev/?imei={term}'
PINCODE_API_ENDPOINT = 'https://pincode-info.gauravyt566.workers.dev/?pincode={term}'
FREEFIRE_API_ENDPOINT = 'https://ff-info.gauravyt566.workers.dev/?uid={term}'
CNIC_API_ENDPOINT = 'https://pak-info.gauravyt566.workers.dev/?cnic={term}'
VEHICLE_BASIC_API_ENDPOINT = 'https://vehicle-inf.gauravyt566.workers.dev/?rc={term}'
SMS_BOMBER_API_ENDPOINT = 'https://sms-bomber.gauravyt566.workers.dev/?num={term}'
TELEGRAM_USERNAME_API_ENDPOINT = 'https://gaurav.xo.je/telegram.php?username={term}'
INSTAGRAM_API_ENDPOINT = 'https://gaurav.xo.je/insta.php?username={term}'

# Payment API Endpoints
PAYMENT_API_KEY = "ZephrexXx"
CREATE_SESSION_URL = "https://payment-api-wld5.onrender.com/create-session"
VERIFY_PAYMENT_URL = "https://payment-api-wld5.onrender.com/verify"

# Credit System Configuration
INITIAL_CREDITS = 0
FIRST_TIME_BONUS_CREDITS = 5  # One-time bonus for first-time users only
REFERRAL_CREDITS = 10

# Credit Packages with Bonus - UPDATED
CREDIT_PACKAGES = {
    49: 49,    # 49₹ → 49 credits
    99: 119,   # 99₹ → 119 credits (20 bonus)
    149: 199,  # 149₹ → 199 credits (50 bonus)
    199: 299   # 199₹ → 299 credits (100 bonus)
}

# Service Credit Costs
SERVICE_CREDIT_COSTS = {
    'num': 2,
    'paknum': 2,
    'aadhaar': 2,
    'family': 2,
    'vehicle': 2,
    'vnum': 5,
    'ifsc': 1,
    'ip': 1,
    'tgid': 1,
    'pakfamily': 1,
    'gst': 1,
    'pan': 1,
    'imei': 1,
    'pincode': 1,
    'freefire': 1,
    'cnic': 1,
    'smsbomber': 1,
    'tg': 1,
    'insta': 1
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class UserStates(StatesGroup):
    awaiting_phone = State()
    awaiting_pak_phone = State()
    awaiting_aadhaar = State()
    awaiting_family = State()
    awaiting_ifsc = State()
    awaiting_ip = State()
    awaiting_tg = State()
    awaiting_pak_family = State()
    awaiting_redeem_code = State()
    awaiting_gst = State()
    awaiting_pan = State()
    awaiting_vnum = State()
    awaiting_imei = State()
    awaiting_pincode = State()
    awaiting_freefire = State()
    awaiting_cnic = State()
    awaiting_vehicle = State()
    awaiting_sms_bomber = State()
    awaiting_tg_username = State()
    awaiting_insta_username = State()
    in_continuous_lookup = State()
    awaiting_payment_verification = State()

class AdminStates(StatesGroup):
    awaiting_add_time = State()
    awaiting_remove_time = State()
    awaiting_premium_add = State()
    awaiting_premium_remove = State()
    awaiting_history_id = State()
    awaiting_broadcast = State()
    awaiting_ban_id = State()
    awaiting_unban_id = State()
    awaiting_gen_code = State()
    awaiting_add_credits = State()

def generate_unique_amount(base_amount: int) -> str:
    if not FIREBASE_ENABLED:
        paise = secrets.randbelow(90) + 10
        return f"{base_amount}.{paise:02d}"
    
    max_retries = 30
    used_paise_values = []
    
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    
    for attempt in range(max_retries):
        paise = secrets.randbelow(90) + 10
        final_amount = f"{base_amount}.{paise:02d}"
        
        try:
            amounts_ref = db.collection("recent_amounts").where("amount", "==", final_amount).where("timestamp", ">=", ten_minutes_ago)
            docs = list(amounts_ref.stream())
            
            if len(docs) == 0:
                amounts_ref = db.collection("recent_amounts")
                amounts_ref.add({
                    "amount": final_amount,
                    "base_amount": base_amount,
                    "timestamp": datetime.now(),
                    "used": False
                })
                return final_amount
            else:
                used_paise_values.append(paise)
        except Exception as e:
            logger.error(f"Error checking unique amount: {e}")
            paise = secrets.randbelow(90) + 10
            return f"{base_amount}.{paise:02d}"
    
    if used_paise_values:
        paise = secrets.randbelow(90) + 10
        while paise in used_paise_values:
            paise = secrets.randbelow(90) + 10
        final_amount = f"{base_amount}.{paise:02d}"
        try:
            amounts_ref = db.collection("recent_amounts")
            amounts_ref.add({
                "amount": final_amount,
                "base_amount": base_amount,
                "timestamp": datetime.now(),
                "used": False
            })
        except:
            pass
        return final_amount
    
    paise = secrets.randbelow(90) + 10
    return f"{base_amount}.{paise:02d}"

def has_user_started_bot(user_id: int) -> bool:
    if not FIREBASE_ENABLED:
        return True
    
    user_data = get_user_data(user_id)
    return user_data is not None

def get_or_create_user_doc(user_id: int):
    if not FIREBASE_ENABLED:
        return None
    
    try:
        user_ref = db.collection("users").document(str(user_id))
        doc = user_ref.get()
        
        if not doc.exists:
            user_data = {
                "user_id": str(user_id),
                "name": "",
                "username": "",
                "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "credits": FIRST_TIME_BONUS_CREDITS,
                "admin_credits": 0,
                "total_purchased_credits": 0,
                "first_time_bonus_given": True,
                "referred_by": None,
                "referral_count": 0,
                "referral_credits_earned": 0,
                "redeemed_codes": [],
                "last_redeem_timestamp": 0,
                "updated_at": datetime.now().isoformat()
            }
            user_ref.set(user_data)
            return user_data
        else:
            user_data = doc.to_dict()
            if "credits" not in user_data:
                user_data["credits"] = INITIAL_CREDITS
            if "admin_credits" not in user_data:
                user_data["admin_credits"] = 0
            if "total_purchased_credits" not in user_data:
                user_data["total_purchased_credits"] = 0
            if "first_time_bonus_given" not in user_data:
                user_data["first_time_bonus_given"] = False
            
            return user_data
    except Exception as e:
        logger.error(f"Firebase error in get_or_create_user_doc for user {user_id}: {e}")
        return None

def update_user_data(user_id: int, update_data: dict):
    if not FIREBASE_ENABLED:
        return False
    
    try:
        user_ref = db.collection("users").document(str(user_id))
        update_data["updated_at"] = datetime.now().isoformat()
        user_ref.set(update_data, merge=True)
        return True
    except Exception as e:
        logger.error(f"Firebase update error for user {user_id}: {e}")
        return False

def get_user_data(user_id: int):
    if not FIREBASE_ENABLED:
        return None
    
    try:
        user_ref = db.collection("users").document(str(user_id))
        doc = user_ref.get()
        if doc.exists:
            user_data = doc.to_dict()
            
            if "credits" not in user_data:
                user_data["credits"] = INITIAL_CREDITS
            if "admin_credits" not in user_data:
                user_data["admin_credits"] = 0
            if "total_purchased_credits" not in user_data:
                user_data["total_purchased_credits"] = 0
            if "first_time_bonus_given" not in user_data:
                user_data["first_time_bonus_given"] = False
            
            return user_data
        return None
    except Exception as e:
        logger.error(f"Firebase get error for user {user_id}: {e}")
        return None

def load_collection(collection_name: str):
    if not FIREBASE_ENABLED:
        return []
    
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        
        if collection_name in ["admins", "banned_users", "premium_users"]:
            data = []
            for doc in docs:
                try:
                    data.append(int(doc.id))
                except:
                    data.append(doc.id)
            return data
        elif collection_name == "users":
            data = {}
            for doc in docs:
                user_data = doc.to_dict()
                try:
                    user_id = int(doc.id)
                    data[user_id] = user_data
                except:
                    data[doc.id] = user_data
            return data
        else:
            return []
    except Exception as e:
        logger.error(f"Firebase load error for {collection_name}: {e}")
        return []

def save_collection(data: list, collection_name: str):
    if not FIREBASE_ENABLED:
        return
    
    try:
        collection_ref = db.collection(collection_name)
        
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        
        for item in data:
            collection_ref.document(str(item)).set({
                "added_at": datetime.now().isoformat()
            })
                
    except Exception as e:
        logger.error(f"Firebase save error for {collection_name}: {e}")

def log_user_action(user_id: int, action: str, details: str = ""):
    if not FIREBASE_ENABLED:
        return
    
    try:
        history_ref = db.collection("user_history").document(str(user_id))
        doc = history_ref.get()
        
        if doc.exists:
            history_data = doc.to_dict()
            actions = history_data.get("actions", [])
        else:
            actions = []
        
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details
        }
        
        actions.insert(0, log_entry)
        actions = actions[:50]
        
        history_ref.set({
            "user_id": str(user_id),
            "actions": actions,
            "updated_at": datetime.now().isoformat()
        }, merge=True)
    except Exception as e:
        logger.error(f"Firebase history log error for user {user_id}: {e}")

def get_user_credits(user_id: int):
    if not FIREBASE_ENABLED:
        return INITIAL_CREDITS
    
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            return INITIAL_CREDITS
        return user_data.get("credits", INITIAL_CREDITS)
    except Exception as e:
        logger.error(f"Error getting credits for user {user_id}: {e}")
        return INITIAL_CREDITS

def deduct_credits(user_id: int, amount: int) -> bool:
    if not FIREBASE_ENABLED:
        return True
    
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            return False
        
        current_credits = user_data.get("credits", 0)
        if current_credits < amount:
            return False
        
        new_credits = current_credits - amount
        update_user_data(user_id, {"credits": new_credits})
        return True
    except Exception as e:
        logger.error(f"Error deducting credits for user {user_id}: {e}")
        return False

def refund_credits(user_id: int, amount: int) -> bool:
    if not FIREBASE_ENABLED:
        return False
    
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            return False
        
        current_credits = user_data.get("credits", 0)
        new_credits = current_credits + amount
        update_user_data(user_id, {"credits": new_credits})
        return True
    except Exception as e:
        logger.error(f"Error refunding credits for user {user_id}: {e}")
        return False

def add_credits(user_id: int, amount: int, is_purchased: bool = False):
    if not FIREBASE_ENABLED:
        return False
    
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            return False
        
        current_credits = user_data.get("credits", 0)
        new_credits = current_credits + amount
        
        update_data = {"credits": new_credits}
        if is_purchased:
            current_purchased = user_data.get("total_purchased_credits", 0)
            update_data["total_purchased_credits"] = current_purchased + amount
        
        update_user_data(user_id, update_data)
        return True
    except Exception as e:
        logger.error(f"Error adding credits to user {user_id}: {e}")
        return False

def add_admin_credits(user_id: int, amount: int):
    if not FIREBASE_ENABLED:
        return False, 0
    
    try:
        user_data = get_user_data(user_id)
        if not user_data:
            return False, 0
        
        current_admin_credits = user_data.get("admin_credits", 0)
        current_credits = user_data.get("credits", 0)
        
        new_admin_credits = current_admin_credits + amount
        new_total_credits = current_credits + amount
        
        update_user_data(user_id, {
            "admin_credits": new_admin_credits,
            "credits": new_total_credits
        })
        
        return True, new_total_credits
    except Exception as e:
        logger.error(f"Error adding admin credits to user {user_id}: {e}")
        return False, 0

def is_user_admin(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    
    if FIREBASE_ENABLED:
        try:
            admins = load_collection("admins")
            return user_id in admins
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {e}")
            return False
    
    return False

def is_premium_user(user_id: int) -> bool:
    if FIREBASE_ENABLED:
        try:
            premium_users = load_collection("premium_users")
            return user_id in premium_users
        except Exception as e:
            logger.error(f"Error checking premium status for user {user_id}: {e}")
            return False
    
    return False

async def check_membership(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        if "kicked" in str(e).lower() or "forbidden" in str(e).lower():
            return False
        logger.error(f"Error checking membership for user {user_id} in channel {channel_id}: {e}")
        return False

async def is_subscribed(user_id: int) -> bool:
    subscribed_to_1 = await check_membership(user_id, REQUIRED_CHANNEL_1_ID)
    subscribed_to_2 = await check_membership(user_id, REQUIRED_CHANNEL_2_ID)
    subscribed_to_4 = await check_membership(user_id, REQUIRED_CHANNEL_4_ID)
    return subscribed_to_1 and subscribed_to_2 and subscribed_to_4

async def send_join_message(chat_id: int, user_name: str = ""):
    welcome_text = f"Hey there <b>{user_name}</b> and welcome to <b>Number To Information Bot</b>\n\n"
    welcome_text += "<u>⚠ Due to high traffic, only our channel subscribers can use this bot.</u> 👇"
    
    keyboard = [
        [
            InlineKeyboardButton(text="JOIN", url=CHANNEL_2_INVITE_LINK),
            InlineKeyboardButton(text="JOIN", url=CHANNEL_1_INVITE_LINK)
        ],
        [
            InlineKeyboardButton(text="JOIN", url=CHANNEL_4_INVITE_LINK)
        ],
        [
            InlineKeyboardButton(text="Joined ✅", callback_data='joined_callback')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=START_IMAGE_URL,
            caption=welcome_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send join photo: {e}. Falling back to text.")
        await bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=reply_markup, parse_mode="HTML")

def get_main_menu_keyboard(user_id: int):
    credits = get_user_credits(user_id)
    
    caption = f"🛰 Welcome to the Next-Gen OSINT Bot\n\n"
    caption += f"💎 Your Credits: <b>{credits}</b>\n\n"
    caption += f"📡 Search & gather information using powerful OSINT techniques.\n\n"
    caption += f"👇 Start your OSINT journey now:"
    
    keyboard = [
        [InlineKeyboardButton(text="🪪 Search Information", callback_data='search_information')],
        [InlineKeyboardButton(text="✅️ Get Free Credits", callback_data='get_referral')],
        [InlineKeyboardButton(text="Support 👨‍💻", callback_data='support')]
    ]
    
    return caption, InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_search_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="🇮🇳 Mobile (2)", callback_data='search_phone'),
            InlineKeyboardButton(text="🇵🇰 Pak Num (2)", callback_data='search_pak_phone')
        ],
        [
            InlineKeyboardButton(text="🪪 Aadhaar (2)", callback_data='search_aadhaar'),
            InlineKeyboardButton(text="👨‍👩‍👧 Family Info (2)", callback_data='search_family')
        ],
        [
            InlineKeyboardButton(text="🏦 IFSC (1)", callback_data='search_ifsc'),
            InlineKeyboardButton(text="🌐 IP Lookup (1)", callback_data='search_ip')
        ],
        [
            InlineKeyboardButton(text="👤 TG ID (1)", callback_data='search_tg'),
            InlineKeyboardButton(text="🇵🇰 CNIC (Basic) (1)", callback_data='search_cnic')
        ],
        [
            InlineKeyboardButton(text="👨‍👩‍👧 Pak Family (1)", callback_data='search_pak_family'),
            InlineKeyboardButton(text="📦 GSTIN (1)", callback_data='search_gst')
        ],
        [
            InlineKeyboardButton(text="🔖 PAN (1)", callback_data='search_pan'),
            InlineKeyboardButton(text="🚗 Vehicle (2)", callback_data='search_vehicle')
        ],
        [
            InlineKeyboardButton(text="📱 VNUM (5)", callback_data='search_vnum'),
            InlineKeyboardButton(text="📟 IMEI (1)", callback_data='search_imei')
        ],
        [
            InlineKeyboardButton(text="📍 Pincode (1)", callback_data='search_pincode'),
            InlineKeyboardButton(text="🎮 Free Fire UID (1)", callback_data='search_freefire')
        ],
        [
            InlineKeyboardButton(text="📱 TG Username (1)", callback_data='search_tg_username'),
            InlineKeyboardButton(text="📷 Instagram (1)", callback_data='search_instagram')
        ],
        [
            InlineKeyboardButton(text="💣 SMS Bomber (1)", callback_data='search_sms_bomber'),
            InlineKeyboardButton(text="Redeem Code 🎁", callback_data='redeem_code')
        ],
        [
            InlineKeyboardButton(text="< Back", callback_data='back_to_main_menu')
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_buy_credits_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="49 Credits - ₹49", callback_data='buy_credits_49')],
        [InlineKeyboardButton(text="119 Credits - ₹99", callback_data='buy_credits_99')],
        [InlineKeyboardButton(text="199 Credits - ₹149", callback_data='buy_credits_149')],
        [InlineKeyboardButton(text="299 Credits - ₹199", callback_data='buy_credits_199')],
        [InlineKeyboardButton(text="🔙 Back", callback_data='get_referral')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="➕ Add Credits", callback_data='admin_add_credits'),
            InlineKeyboardButton(text="👥 All Users", callback_data='admin_view_all_users')
        ],
        [
            InlineKeyboardButton(text="📜 User History", callback_data='admin_user_history'),
            InlineKeyboardButton(text="📢 Broadcast", callback_data='admin_broadcast')
        ],
        [
            InlineKeyboardButton(text="⭐ Premium List", callback_data='admin_view_premium'),
            InlineKeyboardButton(text="🚫 Block User", callback_data='admin_ban_user')
        ],
        [
            InlineKeyboardButton(text="✅ Unblock User", callback_data='admin_unban_user'),
            InlineKeyboardButton(text="📋 Blocked List", callback_data='admin_view_blocked')
        ],
        [
            InlineKeyboardButton(text="📊 Bot Stats", callback_data='admin_stats'),
            InlineKeyboardButton(text="🎫 Generate Code", callback_data='admin_gen_code')
        ],
        [
            InlineKeyboardButton(text="📈 Referral Stats", callback_data='admin_referral_stats'),
            InlineKeyboardButton(text="📋 Admin List", callback_data='admin_list')
        ],
        [
            InlineKeyboardButton(text="➕ Add Admin", callback_data='admin_add_admin'),
            InlineKeyboardButton(text="➖ Remove Admin", callback_data='admin_remove_admin'),
        ],
        [
            InlineKeyboardButton(text="➕ Add Premium", callback_data='admin_add_premium'),
            InlineKeyboardButton(text="➖ Remove Premium", callback_data='admin_remove_premium'),
        ],
        [
            InlineKeyboardButton(text="🏠 Main Menu", callback_data='back_to_main')
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def increment_referral_count(user_id: int):
    user_data = get_user_data(user_id)
    
    if not user_data:
        user_data = get_or_create_user_doc(user_id)
    
    referral_count = user_data.get("referral_count", 0) + 1
    referral_credits_earned = user_data.get("referral_credits_earned", 0) + REFERRAL_CREDITS
    
    update_user_data(user_id, {
        "referral_count": referral_count,
        "referral_credits_earned": referral_credits_earned
    })
    
    add_credits(user_id, REFERRAL_CREDITS)
    
    logger.info(f"Incremented referral count for user {user_id} to {referral_count}, added {REFERRAL_CREDITS} credits")
    return referral_count

def get_referral_count(user_id: int) -> int:
    user_data = get_user_data(user_id)
    if user_data:
        return user_data.get("referral_count", 0)
    return 0

def process_referral_system(new_user_id: int, referrer_id: int, new_user_name: str):
    try:
        new_user_data = get_user_data(new_user_id)
        if new_user_data and new_user_data.get("referred_by"):
            logger.info(f"User {new_user_id} was already referred, skipping")
            return 0
        
        new_referral_count = increment_referral_count(referrer_id)
        
        if new_user_data:
            update_user_data(new_user_id, {"referred_by": referrer_id})
        else:
            get_or_create_user_doc(new_user_id)
            update_user_data(new_user_id, {"referred_by": referrer_id})
        
        log_user_action(referrer_id, "Referral Success", f"Referred user {new_user_id} ({new_user_name})")
        log_user_action(new_user_id, "Joined via Referral", f"Referred by {referrer_id}")
        
        logger.info(f"Referral processed: {referrer_id} -> {new_user_id}, credits added: {REFERRAL_CREDITS}")
        
        return new_referral_count

    except Exception as e:
        logger.error(f"Error processing referral system: {e}")
        return 0

async def notify_referral_success(referrer_id: int, new_user_name: str, referral_count: int):
    try:
        credits = get_user_credits(referrer_id)
        
        message = f"🙋 User: {html.escape(new_user_name)} joined through your link.\n\n"
        message += f"✅ Reward: You got +{REFERRAL_CREDITS} Credits\n\n"
        message += f"💎 Now, Your Credits: {credits}"

        await bot.send_message(
            chat_id=referrer_id,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Successfully sent referral notification to user {referrer_id}")
    except Exception as e:
        logger.error(f"Could not notify referrer {referrer_id}: {e}")

async def log_new_user_to_channel(user: types.User):
    try:
        try:
            await bot.get_chat(chat_id=LOG_CHANNEL_ID)
        except Exception as e:
            logger.error(f"Log channel not found: {e}")
            return
        
        users = load_collection("users")
        total_users = len(users)
        
        username = f"@{user.username}" if user.username else "(no username)"
        
        message = (
            f"📢 <b>New User started the @IntelSphereX_Bot</b>\n\n"
            f"👤 Name: {html.escape(user.full_name)}\n"
            f"🔗 Username: {username}\n"
            f"🆔 UserID: <code>{user.id}</code>\n\n"
            f"📊 Total Users: <b>{total_users}</b>"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="BOT LINK", 
                url="https://t.me/IntelSphereX_Bot"
            )]
        ])
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        logger.info(f"Logged new user {user.id} to channel.")
        
    except Exception as e:
        logger.error(f"Failed to log new user to channel: {e}")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    
    if FIREBASE_ENABLED:
        try:
            banned_users = load_collection("banned_users")
            if user.id in banned_users:
                return
        except Exception as e:
            logger.error(f"Error checking banned users: {e}")

    if not await is_subscribed(user.id):
        await send_join_message(message.chat.id, user.first_name)
        return

    user_data = get_user_data(user.id)
    is_new_user = not user_data

    referrer_id = None
    if len(message.text.split()) > 1:
        referral_param = message.text.split()[1]
        if referral_param.isdigit():
            potential_referrer_id = int(referral_param)
            
            if potential_referrer_id == user.id:
                await message.answer(
                    "🤧 <i>Do not Use Your Referral Link To earn, Share it with Your Friends!</i>",
                    parse_mode="HTML"
                )
            elif potential_referrer_id != user.id:
                referrer_data = get_user_data(potential_referrer_id)
                if referrer_data or potential_referrer_id in ADMIN_IDS:
                    try:
                        admins = load_collection("admins")
                        if potential_referrer_id in admins:
                            referrer_id = potential_referrer_id
                    except Exception as e:
                        logger.error(f"Error loading admins: {e}")
                        if potential_referrer_id in ADMIN_IDS:
                            referrer_id = potential_referrer_id
                    
                    if is_new_user and referrer_id:
                        referral_count = process_referral_system(user.id, referrer_id, user.first_name)
                        
                        if referral_count > 0:
                            await notify_referral_success(referrer_id, user.first_name, referral_count)

    if is_new_user:
        new_user_data = {
            "user_id": str(user.id),
            "name": user.full_name,
            "username": user.username or "",
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "credits": FIRST_TIME_BONUS_CREDITS,
            "admin_credits": 0,
            "total_purchased_credits": 0,
            "first_time_bonus_given": True,
            "referred_by": referrer_id,
            "referral_count": 0,
            "referral_credits_earned": 0,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "updated_at": datetime.now().isoformat()
        }
        
        update_user_data(user.id, new_user_data)
        log_user_action(user.id, "Joined", f"Referred by: {referrer_id}")
        
        await message.answer(f"🎉 Welcome {user.first_name}!\nYou received *{FIRST_TIME_BONUS_CREDITS} Free Credits* ✅", parse_mode="Markdown")
        
        await log_new_user_to_channel(user)
        
    else:
        update_data = {}
        if user_data.get("name") != user.full_name:
            update_data["name"] = user.full_name
        if user_data.get("username") != (user.username or ""):
            update_data["username"] = user.username or ""
        
        if update_data:
            update_user_data(user.id, update_data)
        
        if referrer_id is not None and ("referred_by" not in user_data or user_data["referred_by"] is None):
            update_user_data(user.id, {"referred_by": referrer_id})
            referral_count = process_referral_system(user.id, referrer_id, user.first_name)
            
            if referral_count > 0:
                await notify_referral_success(referrer_id, user.first_name, referral_count)

    caption, reply_markup = get_main_menu_keyboard(user.id)
    
    try:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=MENU_IMAGE_URL,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send menu photo: {e}. Falling back to text.")
        await message.answer(
            text=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """🔍 IntelSphereX – Credit Based System

💎 Credit Costs per Service:
📱 Mobile Lookup: 2 credits
🪪 Aadhaar Lookup: 2 credits
👨‍👩‍👧 Family Info: 2 credits
🚗 Vehicle RC: 2 credits
📱 Vehicle Mobile: 5 credits
🏦 IFSC Lookup: 1 credit
🌐 IP Lookup: 1 credit
👤 TG ID Lookup: 1 credit
👨‍👩‍👧 Pak Family: 1 credit
📦 GSTIN: 1 credit
🔖 PAN: 1 credit
📟 IMEI: 1 credit
📍 Pincode: 1 credit
🎮 Free Fire: 1 credit
🇵🇰 CNIC: 1 credit
📱 TG Username: 1 credit
📷 Instagram: 1 credit
💣 SMS Bomber: 1 credit

🎁 First-time Bonus: 5 credits (one time only)
🔗 Referral Rewards: 10 credits per referral
💰 Buy Credits: Use the Buy Credits button

👨‍💻 Managed by IntelSphereX"""
    
    await message.answer(help_text)

@dp.callback_query(F.data == "joined_callback")
async def callback_joined(callback: CallbackQuery):
    user = callback.from_user
    
    if not await is_subscribed(user.id):
        await callback.answer("❌ You haven't joined all channels yet.", show_alert=True)
        return
    
    user_data = get_user_data(user.id)
    
    is_new_user = not user_data
    if is_new_user:
        new_user_data = {
            "user_id": str(user.id),
            "name": user.full_name,
            "username": user.username or "",
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "credits": FIRST_TIME_BONUS_CREDITS,
            "admin_credits": 0,
            "total_purchased_credits": 0,
            "first_time_bonus_given": True,
            "referred_by": None,
            "referral_count": 0,
            "referral_credits_earned": 0,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "updated_at": datetime.now().isoformat()
        }
        
        update_user_data(user.id, new_user_data)
        log_user_action(user.id, "Joined", "Verified channels")
        
        await log_new_user_to_channel(user)
        
        await callback.message.answer(f"🎉 Welcome {user.first_name}!\nYou received *{FIRST_TIME_BONUS_CREDITS} Free Credits* ✅", parse_mode="Markdown")
    
    caption, reply_markup = get_main_menu_keyboard(user.id)
    
    try:
        await callback.message.delete()
    except:
        pass
    
    try:
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=MENU_IMAGE_URL,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send menu photo on verify: {e}. Falling back to text.")
        await callback.message.answer(
            text=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
    await callback.answer()

@dp.callback_query(F.data == "verify_join")
async def callback_verify_join(callback: CallbackQuery):
    user = callback.from_user
    if await is_subscribed(user.id):
        try:
            await callback.message.delete()
        except:
            pass

        user_data = get_user_data(user.id)
        is_new_user = not user_data
        
        if is_new_user:
            new_user_data = {
                "user_id": str(user.id),
                "name": user.full_name,
                "username": user.username or "",
                "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "credits": FIRST_TIME_BONUS_CREDITS,
                "admin_credits": 0,
                "total_purchased_credits": 0,
                "first_time_bonus_given": True,
                "referred_by": None,
                "referral_count": 0,
                "referral_credits_earned": 0,
                "redeemed_codes": [],
                "last_redeem_timestamp": 0,
                "updated_at": datetime.now().isoformat()
            }
            
            update_user_data(user.id, new_user_data)
            log_user_action(user.id, "Joined", "Verified channels")
            
            await log_new_user_to_channel(user)

        caption, reply_markup = get_main_menu_keyboard(user.id)
        
        try:
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=MENU_IMAGE_URL,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send menu photo on verify: {e}. Falling back to text.")
            await callback.message.answer(
                text=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

    else:
        await callback.answer("❌ You haven't joined all channels yet.", show_alert=True)

@dp.callback_query(F.data == "back_to_main_menu")
async def callback_back_to_main_menu(callback: CallbackQuery):
    user = callback.from_user
    caption, reply_markup = get_main_menu_keyboard(user.id)
    
    try:
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")
        try:
            await callback.message.delete()
        except:
            pass
        
        try:
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=MENU_IMAGE_URL,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await callback.message.answer(
                text=caption,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
    
    await callback.answer()

@dp.callback_query(F.data == "search_information")
async def callback_search_information(callback: CallbackQuery):
    user = callback.from_user
    
    if not await is_subscribed(user.id):
        await callback.answer("❌ You must join all channels first.", show_alert=True)
        return
    
    credits = get_user_credits(user.id)
    if credits <= 0:
        await callback.answer(f"❌ You have no credits left. Buy more credits to continue.", show_alert=True)
        return
    
    search_caption = f"*🔥 Here are the available services 👇*\n\n💎 Your Credits: *{credits}*\n\n_⚠ Number in brackets shows credit cost per lookup_"
    
    try:
        await callback.message.edit_caption(
            caption=search_caption,
            reply_markup=get_search_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")
    
    await callback.answer()

@dp.callback_query(F.data == "get_referral")
async def callback_get_referral(callback: CallbackQuery):
    user = callback.from_user
    referral_link = f"https://t.me/{BOT_USERNAME.lstrip('@')}?start={user.id}"
    current_ref_count = get_referral_count(user.id)
    user_data = get_user_data(user.id)
    referral_credits = user_data.get("referral_credits_earned", 0) if user_data else 0

    message_text = (
        f"✅️ <b>Get Free Credits</b>\n\n"
        f"<b>Your Referral Link:</b>\n<code>{referral_link}</code>\n\n"
        f"<b>Current Stats:</b>\n"
        f"📊 Total Referrals: <b>{current_ref_count}</b>\n"
        f"💎 Credits Earned: <b>{referral_credits}</b>\n\n"
        f"<b>🎁 Rewards:</b>\n"
        f"✅ Each referral: <b>{REFERRAL_CREDITS} credits</b>\n\n"
        f"<b>You'll get instant notifications</b> when someone joins using your link!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Buy Paid Credits", callback_data='buy_credits')],
        [InlineKeyboardButton(text="🔙 Back", callback_data='back_to_main_menu')]
    ])
    
    await callback.message.edit_caption(
        caption=message_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "buy_credits")
async def callback_buy_credits(callback: CallbackQuery):
    buy_caption = "💎 <b>Buy Credits Packages</b>\n\n"
    buy_caption += "• 49 Credits = ₹49\n"
    buy_caption += "• 119 Credits = ₹99 (20 bonus)\n"
    buy_caption += "• 199 Credits = ₹149 (50 bonus)\n"
    buy_caption += "• 299 Credits = ₹199 (100 bonus)\n\n"
    buy_caption += "👇 Select a package to proceed with payment"
    
    try:
        await callback.message.edit_caption(
            caption=buy_caption,
            reply_markup=get_buy_credits_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to edit caption: {e}")
    
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_credits_"))
async def callback_select_credit_package(callback: CallbackQuery):
    package_str = callback.data.replace("buy_credits_", "")
    try:
        base_amount = int(package_str)
        credits = CREDIT_PACKAGES.get(base_amount, 0)
        
        if credits == 0:
            await callback.answer("❌ Invalid package selected.", show_alert=True)
            return
        
        user = callback.from_user
        
        try:
            final_amount = generate_unique_amount(base_amount)
            
            params = {
                "key": PAYMENT_API_KEY,
                "user_id": user.id,
                "amount": final_amount
            }
            
            response = requests.get(CREATE_SESSION_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("Status") == "OK":
                session_id = data.get("session_id")
                
                user_data = get_user_data(user.id)
                if user_data:
                    update_user_data(user.id, {
                        "pending_payment": {
                            "session_id": session_id,
                            "credits": credits,
                            "amount": final_amount,
                            "timestamp": time.time()
                        }
                    })
                
                payment_text = f"💳 <b>Payment Details</b>\n\n"
                payment_text += f"Package: <b>{credits} Credits</b>\n"
                payment_text += f"Amount: <b>₹{final_amount}</b>\n"
                payment_text += f"Session ID: <code>{session_id}</code>\n\n"
                payment_text += f"<b>Payment Methods:</b>\n"
                payment_text += f"1. UPI ID: <code>gaurav.intel@fam</code>\n"
                payment_text += f"2. QR Code: https://ibb.co/RknmxtSb\n\n"
                payment_text += f"<b>Important:</b>\n"
                payment_text += f"1. Send exact amount: ₹{final_amount}\n"
                payment_text += f"2. Use UPI ID: gaurav.intel@fam\n"
                payment_text += f"3. After payment, click Verify Payment below\n"
                payment_text += f"4. Payments are auto-verified\n\n"
                payment_text += f"<i>Payment will be verified automatically. Credits will be added instantly.</i>"
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Verify Payment", callback_data=f"verify_payment_{session_id}")],
                    [InlineKeyboardButton(text="👨‍💻 Support", url="https://t.me/ZephrexXx")],
                    [InlineKeyboardButton(text="🔙 Back", callback_data='buy_credits')]
                ])
                
                await callback.message.edit_caption(
                    caption=payment_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                await callback.answer("❌ Failed to create payment session. Please try again.", show_alert=True)
                
        except Exception as e:
            logger.error(f"Payment session creation error: {e}")
            await callback.answer("❌ Payment service is temporarily unavailable. Please try again later.", show_alert=True)
            
    except ValueError:
        await callback.answer("❌ Invalid package.", show_alert=True)

@dp.callback_query(F.data.startswith("verify_payment_"))
async def callback_verify_payment(callback: CallbackQuery):
    session_id = callback.data.replace("verify_payment_", "")
    user = callback.from_user
    
    try:
        params = {
            "key": PAYMENT_API_KEY,
            "session_id": session_id,
            "user_id": user.id
        }
        
        response = requests.get(VERIFY_PAYMENT_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Status") == "APPROVED":
            user_data = get_user_data(user.id)
            if user_data and "pending_payment" in user_data:
                credits_to_add = user_data["pending_payment"].get("credits", 0)
                amount = user_data["pending_payment"].get("amount", 0)
                
                # ✅ FIXED: add_credits function को सही parameters दें
                add_credits(user.id, credits_to_add, True)
                
                update_data = user_data.copy()
                if "pending_payment" in update_data:
                    del update_data["pending_payment"]
                update_user_data(user.id, update_data)
                
                new_credits = get_user_credits(user.id)
                
                success_text = f"✅ <b>Payment Verified Successfully!</b>\n\n"
                success_text += f"🎉 Added: <b>{credits_to_add} Credits</b>\n"
                success_text += f"💰 Amount: ₹{data.get('Amount', 'N/A')}\n"
                success_text += f"📋 Transaction ID: {data.get('Transaction_id', 'N/A')}\n"
                success_text += f"👤 Name: {data.get('Name', 'N/A')}\n\n"
                success_text += f"💎 Your Total Credits: <b>{new_credits}</b>\n\n"
                success_text += f"Thank you for your purchase! 🎊"
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_main_menu')]
                ])
                
                await callback.message.edit_caption(
                    caption=success_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                
                log_user_action(user.id, "Purchased Credits", f"{credits_to_add} credits for ₹{amount}")
            else:
                await callback.message.edit_caption("❌ Payment data not found. Please contact support.", parse_mode="HTML")
        elif data.get("Status") == "NOT_FOUND":
            await callback.message.edit_caption(
                "⏳ Payment not verified yet. Please wait a moment and try again.\n\n"
                "If you have made the payment, it may take 1-2 minutes to verify.\n"
                "Click Verify Payment again after a minute.",
                parse_mode="HTML"
            )
        elif data.get("Status") == "FAILED":
            await callback.message.edit_caption("❌ Payment session already used. Please start a new payment.", parse_mode="HTML")
        else:
            await callback.message.edit_caption(
                "⏳ Payment not verified yet. Please wait a moment and try again.\n\n"
                "If you have made the payment, it may take 1-2 minutes to verify.\n"
                "Click Verify Payment again after a minute.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        await callback.message.edit_caption(
            "❌ Error verifying payment. Please try again or contact support if the issue persists.",
            parse_mode="HTML"
        )
                
                log_user_action(user.id, "Purchased Credits", f"{credits_to_add} credits for ₹{amount}")
            else:
                await callback.message.edit_caption("❌ Payment data not found. Please contact support.", parse_mode="HTML")
        elif data.get("Status") == "NOT_FOUND":
            await callback.message.edit_caption(
                "⏳ Payment not verified yet. Please wait a moment and try again.\n\n"
                "If you have made the payment, it may take 1-2 minutes to verify.\n"
                "Click Verify Payment again after a minute.",
                parse_mode="HTML"
            )
        elif data.get("Status") == "FAILED":
            await callback.message.edit_caption("❌ Payment session already used. Please start a new payment.", parse_mode="HTML")
        else:
            await callback.message.edit_caption(
                "⏳ Payment not verified yet. Please wait a moment and try again.\n\n"
                "If you have made the payment, it may take 1-2 minutes to verify.\n"
                "Click Verify Payment again after a minute.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        await callback.message.edit_caption(
            "❌ Error verifying payment. Please try again or contact support if the issue persists.",
            parse_mode="HTML"
        )

@dp.callback_query(F.data == "support")
async def callback_support(callback: CallbackQuery):
    support_text = "Click the button below to contact the admin directly for any help or queries."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Contact Admin 👨‍💻", url=f"tg://user?id={SUPPORT_USER_ID}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data='back_to_main_menu')]
    ])
    await callback.message.edit_caption(support_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    user = callback.from_user
    welcome_text = f"""
╔═══════════════════════╗
🏠 <b>MAIN MENU</b> 🏠
╚═══════════════════════╝

👤 <b>User:</b> {html.escape(user.full_name)}
🆔 <b>ID:</b> <code>{user.id}</code>

Use buttons below to navigate 👇
"""
    try:
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=MENU_IMAGE_URL,
            caption=welcome_text,
            reply_markup=get_search_keyboard(),
            parse_mode="HTML"
        )
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Failed to send menu photo on back_to_main: {e}. Falling back to text.")
        await callback.message.answer(welcome_text, reply_markup=get_search_keyboard(), parse_mode="HTML")
    
    await callback.answer()

@dp.callback_query(F.data.in_([
    'search_phone', 'search_pak_phone', 'search_aadhaar', 'search_family',
    'search_ifsc', 'search_ip', 'search_tg', 'search_pak_family',
    'search_gst', 'search_pan', 'search_vnum', 'search_imei', 
    'search_pincode', 'search_freefire', 'search_cnic', 'search_vehicle', 
    'search_sms_bomber', 'search_tg_username', 'search_instagram'
]))
async def handle_search_callback(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user

    if not await is_subscribed(user.id):
        await callback.answer(
            "❌ You must join all channels first.",
            show_alert=True
        )
        return
    
    service_map = {
        'search_phone': 'num',
        'search_pak_phone': 'paknum',
        'search_aadhaar': 'aadhaar',
        'search_family': 'family',
        'search_vehicle': 'vehicle',
        'search_vnum': 'vnum',
        'search_ifsc': 'ifsc',
        'search_ip': 'ip',
        'search_tg': 'tgid',
        'search_pak_family': 'pakfamily',
        'search_gst': 'gst',
        'search_pan': 'pan',
        'search_imei': 'imei',
        'search_pincode': 'pincode',
        'search_freefire': 'freefire',
        'search_cnic': 'cnic',
        'search_sms_bomber': 'smsbomber',
        'search_tg_username': 'tg',
        'search_instagram': 'insta',
    }
    
    service_name = service_map.get(callback.data)
    if not service_name:
        await callback.answer("❌ Invalid service.", show_alert=True)
        return
    
    credit_cost = SERVICE_CREDIT_COSTS.get(service_name, 1)
    user_credits = get_user_credits(user.id)
    
    if user_credits < credit_cost:
        await callback.answer(
            f"❌ Insufficient credits. You need {credit_cost} credits but have only {user_credits}.",
            show_alert=True
        )
        return

    lookup_prompts = {
        'search_phone': ("10-digit Indian mobile number", "🇮🇳 Mobile Lookup"),
        'search_pak_phone': ("10-digit Pakistani number", "🇵🇰 Pak Num Lookup"),
        'search_aadhaar': ("12-digit Aadhaar number", "🪪 Aadhaar Lookup"),
        'search_family': ("12-digit Aadhaar number", "👨‍👩‍👧 Family Info Lookup"),
        'search_vehicle': ("vehicle RC number", "🚗 Vehicle Lookup"),
        'search_vnum': ("vehicle RC number", "📱 VNUM Lookup"),
        'search_ifsc': ("bank IFSC code", "🏦 IFSC Lookup"),
        'search_ip': ("IP address", "🌐 IP Lookup"),
        'search_tg': ("Telegram User ID", "👤 TG ID Lookup"),
        'search_pak_family': ("Pakistani CNIC number", "👨‍👩‍👧 Pak Family Lookup"),
        'search_gst': ("15-character GSTIN", "📦 GSTIN Lookup"),
        'search_pan': ("10-character PAN number", "🔖 PAN Lookup"),
        'search_imei': ("15-digit IMEI number", "📟 IMEI Lookup"),
        'search_pincode': ("6-digit Pincode", "📍 Pincode Lookup"),
        'search_freefire': ("Free Fire UID", "🎮 Free Fire UID Lookup"),
        'search_cnic': ("13-digit Pakistani CNIC", "🇵🇰 CNIC (Basic) Lookup"),
        'search_sms_bomber': ("10-digit mobile number", "💣 SMS Bomber"),
        'search_tg_username': ("Telegram username", "📱 Telegram Username Lookup"),
        'search_instagram': ("Instagram username", "📷 Instagram Lookup"),
    }
    
    if callback.data in lookup_prompts:
        input_description, lookup_name = lookup_prompts[callback.data]
        
        state_mapping = {
            'search_phone': UserStates.awaiting_phone,
            'search_pak_phone': UserStates.awaiting_pak_phone,
            'search_aadhaar': UserStates.awaiting_aadhaar,
            'search_family': UserStates.awaiting_family,
            'search_vehicle': UserStates.awaiting_vehicle,
            'search_vnum': UserStates.awaiting_vnum,
            'search_ifsc': UserStates.awaiting_ifsc,
            'search_ip': UserStates.awaiting_ip,
            'search_tg': UserStates.awaiting_tg,
            'search_pak_family': UserStates.awaiting_pak_family,
            'search_gst': UserStates.awaiting_gst,
            'search_pan': UserStates.awaiting_pan,
            'search_imei': UserStates.awaiting_imei,
            'search_pincode': UserStates.awaiting_pincode,
            'search_freefire': UserStates.awaiting_freefire,
            'search_cnic': UserStates.awaiting_cnic,
            'search_sms_bomber': UserStates.awaiting_sms_bomber,
            'search_tg_username': UserStates.awaiting_tg_username,
            'search_instagram': UserStates.awaiting_insta_username,
        }
        
        lookup_func_mapping = {
            'search_phone': perform_phone_lookup,
            'search_pak_phone': perform_pak_phone_lookup,
            'search_aadhaar': perform_aadhaar_lookup,
            'search_family': perform_family_lookup,
            'search_vehicle': perform_vehicle_lookup,
            'search_vnum': perform_vnum_lookup,
            'search_ifsc': perform_ifsc_lookup,
            'search_ip': perform_ip_lookup,
            'search_tg': perform_tg_lookup,
            'search_pak_family': perform_pak_family_lookup,
            'search_gst': perform_gst_lookup,
            'search_pan': perform_pan_lookup,
            'search_imei': perform_imei_lookup,
            'search_pincode': perform_pincode_lookup,
            'search_freefire': perform_freefire_lookup,
            'search_cnic': perform_cnic_lookup,
            'search_sms_bomber': perform_sms_bomber_action,
            'search_tg_username': perform_tg_username_lookup,
            'search_instagram': perform_instagram_lookup,
        }
        
        lookup_func = lookup_func_mapping.get(callback.data)
        
        await state.update_data(
            lookup_func=lookup_func,
            lookup_name=lookup_name,
            user_id=user.id,
            chat_id=callback.message.chat.id,
            chat_type=callback.message.chat.type,
            credit_cost=credit_cost,
            service_name=service_name
        )
        
        state_class = state_mapping.get(callback.data, UserStates.in_continuous_lookup)
        await state.set_state(state_class)
        
        prompt_msg = f"🔍 <b>{lookup_name}</b>\n\n"
        prompt_msg += f"💎 Cost: <b>{credit_cost} credit(s)</b>\n"
        prompt_msg += f"💎 Your Credits: <b>{user_credits}</b>\n\n"
        prompt_msg += f"➡️ Please send the <b>{input_description}</b> to look up."
        
        await callback.message.answer(prompt_msg, parse_mode="HTML")
        await callback.answer()

@dp.callback_query(F.data == 'redeem_code')
async def handle_redeem_callback(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    if not await is_subscribed(user.id):
        await callback.answer("❌ You must join all channels first.", show_alert=True)
        return
    
    await state.set_state(UserStates.awaiting_redeem_code)
    await callback.message.answer("🎁 Please send your redeem code:", parse_mode="HTML")
    await callback.answer()

@dp.message(UserStates.awaiting_phone)
async def handle_phone_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_phone_lookup)

@dp.message(UserStates.awaiting_pak_phone)
async def handle_pak_phone_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_pak_phone_lookup)

@dp.message(UserStates.awaiting_aadhaar)
async def handle_aadhaar_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_aadhaar_lookup)

@dp.message(UserStates.awaiting_family)
async def handle_family_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_family_lookup)

@dp.message(UserStates.awaiting_vehicle)
async def handle_vehicle_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_vehicle_lookup)

@dp.message(UserStates.awaiting_vnum)
async def handle_vnum_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_vnum_lookup)

@dp.message(UserStates.awaiting_ifsc)
async def handle_ifsc_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_ifsc_lookup)

@dp.message(UserStates.awaiting_ip)
async def handle_ip_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_ip_lookup)

@dp.message(UserStates.awaiting_tg)
async def handle_tg_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_tg_lookup)

@dp.message(UserStates.awaiting_pak_family)
async def handle_pak_family_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_pak_family_lookup)

@dp.message(UserStates.awaiting_gst)
async def handle_gst_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_gst_lookup)

@dp.message(UserStates.awaiting_pan)
async def handle_pan_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_pan_lookup)

@dp.message(UserStates.awaiting_imei)
async def handle_imei_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_imei_lookup)

@dp.message(UserStates.awaiting_pincode)
async def handle_pincode_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_pincode_lookup)

@dp.message(UserStates.awaiting_freefire)
async def handle_freefire_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_freefire_lookup)

@dp.message(UserStates.awaiting_cnic)
async def handle_cnic_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_cnic_lookup)

@dp.message(UserStates.awaiting_sms_bomber)
async def handle_sms_bomber_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_sms_bomber_action)

@dp.message(UserStates.awaiting_tg_username)
async def handle_tg_username_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_tg_username_lookup)

@dp.message(UserStates.awaiting_insta_username)
async def handle_insta_username_input(message: Message, state: FSMContext):
    await handle_lookup_input(message, state, perform_instagram_lookup)

async def handle_lookup_input(message: Message, state: FSMContext, lookup_func):
    state_data = await state.get_data()
    user_id = state_data.get('user_id')
    chat_id = state_data.get('chat_id')
    chat_type = state_data.get('chat_type')
    credit_cost = state_data.get('credit_cost', 1)
    service_name = state_data.get('service_name', '')
    lookup_name = state_data.get('lookup_name', 'Lookup')
    
    await state.clear()
    
    user_credits = get_user_credits(user_id)
    if user_credits < credit_cost:
        await message.answer(f"❌ Insufficient credits. You need {credit_cost} credits but have only {user_credits}.")
        return
    
    if deduct_credits(user_id, credit_cost):
        log_user_action(user_id, f"Used {service_name}", f"Deducted {credit_cost} credits")
        await lookup_func(message.text, user_id, chat_id, chat_type, credit_cost=credit_cost)
    else:
        await message.answer("❌ Failed to deduct credits. Please try again.")

@dp.callback_query(F.data == 'stop_continuous_lookup')
async def stop_continuous_lookup(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✅ Continuous lookup stopped. You can now choose another option.", parse_mode="HTML")
    await callback.answer()

@dp.message(UserStates.in_continuous_lookup)
async def handle_continuous_lookup(message: Message, state: FSMContext):
    if message.text and message.text.lower() in ['/stop', 'stop', '❌', 'exit', '/exit']:
        await state.clear()
        await message.answer("✅ Continuous lookup stopped. You can now choose another option.")
        return
    
    state_data = await state.get_data()
    lookup_func = state_data.get('lookup_func')
    user_id = state_data.get('user_id')
    chat_id = state_data.get('chat_id')
    chat_type = state_data.get('chat_type')
    credit_cost = state_data.get('credit_cost', 1)
    service_name = state_data.get('service_name', '')
    
    user_credits = get_user_credits(user_id)
    if user_credits < credit_cost:
        await message.answer(f"❌ Insufficient credits. You need {credit_cost} credits but have only {user_credits}.")
        await state.clear()
        return
    
    if lookup_func:
        if deduct_credits(user_id, credit_cost):
            log_user_action(user_id, f"Used {service_name}", f"Deducted {credit_cost} credits")
            await lookup_func(message.text, user_id, chat_id, chat_type, credit_cost=credit_cost)
        else:
            await message.answer("❌ Failed to deduct credits. Please try again.")
            await state.clear()
    else:
        await message.answer("❌ Lookup function not found. Please start over.")
        await state.clear()

def get_info_footer(user_id: int, chat_type: str = "private", credit_cost: int = 0, refunded: bool = False) -> str:
    if chat_type in ["group", "supergroup"]:
        return ""
    
    credits = get_user_credits(user_id)
    footer = f"\n\n💎 <b>Remaining Credits:</b> {credits}"
    if refunded:
        footer += f"\n💰 <b>Refunded:</b> {credit_cost} credit(s) (no data found)"
    else:
        footer += f"\n💎 <b>Cost:</b> {credit_cost} credit(s)"
    return footer

async def generic_lookup(term: str, user_id: int, chat_id: int, api_endpoint: str, action_name: str, display_name: str, chat_type: str, sent_message: types.Message = None, input_validator=None, credit_cost: int = 1):
    term = term.strip().upper() if action_name in ['GST Search', 'PAN Search', 'VNUM Search', 'Vehicle Search'] else term.strip()

    if input_validator and not input_validator(term):
        if sent_message:
            await sent_message.edit_text(f"❌ <b>Invalid Input:</b> {display_name} validation failed.", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, f"❌ <b>Invalid Input:</b> {display_name} validation failed.", parse_mode="HTML")
        return
    
    if not sent_message:
        sent_message = await bot.send_message(chat_id, f"🔍 Searching for {display_name} details...")

    try:
        final_api_endpoint = api_endpoint.format(term=term)
        logger.info(f"Calling API: {final_api_endpoint}")
        
        response = requests.get(final_api_endpoint, timeout=20)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            logger.warning(f"HTML response received from API: {final_api_endpoint}")
            await sent_message.edit_text(f"🔌 The {display_name} API service returned an HTML page (might be down or blocked)." + get_info_footer(user_id, chat_type, credit_cost, True))
            refund_credits(user_id, credit_cost)
            return
        
        try:
            data = response.json()
            
            should_refund = False
            if not data or isinstance(data, str) and 'error' in data.lower():
                should_refund = True
            elif isinstance(data, dict):
                error_msg = data.get('error') or data.get('msg') or data.get('message') or data.get('Error')
                if error_msg or data.get('status') == False or data.get('success') == False:
                    should_refund = True
                elif len(data) == 0 or (len(data) == 1 and any(key in data for key in ['status', 'message', 'error'])):
                    should_refund = True
            
            if should_refund:
                await sent_message.edit_text(f"🤷 No details found for {display_name}: <code>{html.escape(term)}</code>." + get_info_footer(user_id, chat_type, credit_cost, True), parse_mode="HTML")
                refund_credits(user_id, credit_cost)
                log_user_action(user_id, f"Refunded {action_name}", f"Refunded {credit_cost} credits - no data found")
                return
                    
        except json.JSONDecodeError:
            text_response = response.text[:200]
            if 'error' in text_response.lower() or 'not found' in text_response.lower():
                await sent_message.edit_text(f"🤷 No details found for {display_name}: <code>{html.escape(term)}</code>." + get_info_footer(user_id, chat_type, credit_cost, True), parse_mode="HTML")
                refund_credits(user_id, credit_cost)
                log_user_action(user_id, f"Refunded {action_name}", f"Refunded {credit_cost} credits - JSON error")
                return
            else:
                data = {"response": text_response}
        
        if isinstance(data, (dict, list)):
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            formatted_data = str(data)
                
        if len(formatted_data) > 4000:
            filename = f"{action_name.replace(' ', '_').lower()}_{term.replace('-', '')}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(formatted_data)
                    
                caption = f"🔍 <b>{display_name} Details for {term}</b>\n\nResponse too long, sent as file." + get_info_footer(user_id, chat_type, credit_cost)
                
                await sent_message.delete()
                await bot.send_document(
                    chat_id=chat_id,
                    document=FSInputFile(filename),
                    caption=caption,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Error creating file {filename}: {e}")
                await sent_message.edit_text(f"❌ Error saving results to file. Please try again.")
                return
            finally:
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except:
                        pass
        else:
            result_text = f"🔍 <b>{display_name} Details for <code>{html.escape(term)}</code></b>\n\n<pre>{html.escape(formatted_data)}</pre>"
            result_text += get_info_footer(user_id, chat_type, credit_cost)
            
            await sent_message.edit_text(result_text, parse_mode="HTML")

    except requests.exceptions.Timeout:
        logger.error(f"{action_name} API Timeout: {api_endpoint}")
        await sent_message.edit_text(f"⏰ The {display_name} search timed out. Please try again later." + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)
    except requests.exceptions.ConnectionError:
        logger.error(f"{action_name} Connection Error: {api_endpoint}")
        await sent_message.edit_text(f"🔌 The {display_name} service is unreachable. Please try again later." + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)
    except requests.exceptions.RequestException as e:
        logger.error(f"{action_name} API Error: {e}")
        await sent_message.edit_text(f"🔌 The {display_name} search service is having issues. Please try again later." + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)
    except Exception as e:
        logger.error(f"{action_name} General Error: {e}")
        await sent_message.edit_text(f"🔌 An unexpected error occurred during {display_name} search. Error: {str(e)}" + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)

def is_valid_upi(upi: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9.-_]{2,256}@[a-zA-Z0-9]{2,64}$', upi))

def is_valid_gstin(gst: str) -> bool:
    return bool(re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gst))

def is_valid_pan(pan: str) -> bool:
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan))

def is_valid_imei(imei: str) -> bool:
    return imei.isdigit() and len(imei) == 15

def is_valid_pincode(pincode: str) -> bool:
    return pincode.isdigit() and len(pincode) == 6

def is_valid_cnic(cnic: str) -> bool:
    cnic_clean = cnic.replace('-', '')
    return cnic_clean.isdigit() and len(cnic_clean) == 13

def is_valid_pak_num(phone: str) -> bool:
    return phone.isdigit() and len(phone) == 10

def is_valid_telegram_username(username: str) -> bool:
    username = username.lstrip('@')
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$', username))

def is_valid_instagram_username(username: str) -> bool:
    username = username.lstrip('@')
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9._]{0,29}$', username))

async def perform_phone_lookup(phone_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 2):
    if not (phone_number.isdigit() and (len(phone_number) == 10 or (phone_number.startswith("91") and len(phone_number) == 12))):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 10-digit Indian mobile number.", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit Indian mobile number.", parse_mode="HTML")
        return
    phone_number = phone_number[-10:]
    await generic_lookup(phone_number, user_id, chat_id, PHONE_API_ENDPOINT, "Phone Search", "Indian Phone Number", chat_type, sent_message, lambda x: x.isdigit() and len(x) == 10, credit_cost=credit_cost)

async def perform_pak_phone_lookup(phone_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 2):
    if not (phone_number.isdigit() and len(phone_number) == 10):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 10-digit Pakistani number.", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit Pakistani number.", parse_mode="HTML")
        return
    await generic_lookup(phone_number, user_id, chat_id, PAK_PHONE_API_ENDPOINT, "Pak Number Search", "Pakistani Phone Number", chat_type, sent_message, is_valid_pak_num, credit_cost=credit_cost)

async def perform_aadhaar_lookup(aadhaar_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 2):
    if not (aadhaar_number.isdigit() and len(aadhaar_number) == 12):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML")
        return
    await generic_lookup(aadhaar_number, user_id, chat_id, AADHAAR_API_ENDPOINT, "Aadhaar Search", "Aadhaar", chat_type, sent_message, lambda x: x.isdigit() and len(x) == 12, credit_cost=credit_cost)

async def perform_family_lookup(aadhaar_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 2):
    if not (aadhaar_number.isdigit() and len(aadhaar_number) == 12):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML")
        return
    await generic_lookup(aadhaar_number, user_id, chat_id, FAMILY_INFO_API_ENDPOINT, "Family Info Search", "Family Information (by Aadhaar)", chat_type, sent_message, lambda x: x.isdigit() and len(x) == 12, credit_cost=credit_cost)

async def perform_vehicle_lookup(rc_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 2):
    await generic_lookup(rc_number, user_id, chat_id, VEHICLE_BASIC_API_ENDPOINT, "Vehicle Search", "Vehicle RC", chat_type, sent_message, lambda x: 4 <= len(x) <= 15, credit_cost=credit_cost)

async def perform_vnum_lookup(rc_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 5):
    await generic_lookup(rc_number, user_id, chat_id, RC_MOBILE_API_ENDPOINT, "VNUM Search", "Vehicle RC Mobile", chat_type, sent_message, lambda x: 4 <= len(x) <= 15, credit_cost=credit_cost)

async def perform_ifsc_lookup(ifsc_code: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    ifsc_code = ifsc_code.strip().upper()
    await generic_lookup(ifsc_code, user_id, chat_id, IFSC_API_ENDPOINT, "IFSC Search", "Bank IFSC", chat_type, sent_message, lambda x: len(x) == 11 and x.isalnum(), credit_cost=credit_cost)

async def perform_ip_lookup(ip_address: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(ip_address, user_id, chat_id, IP_API_ENDPOINT, "IP Search", "IP Address", chat_type, sent_message, lambda x: 7 <= len(x) <= 15, credit_cost=credit_cost)

async def perform_tg_lookup(user_input: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(user_input, user_id, chat_id, TG_INFO_API_ENDPOINT, "TG ID Search", "Telegram User ID", chat_type, sent_message, lambda x: len(x) > 0, credit_cost=credit_cost)

async def perform_pak_family_lookup(cnic: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    if not is_valid_cnic(cnic):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 13-digit Pakistani CNIC number (dashes optional).", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 13-digit Pakistani CNIC number (dashes optional).", parse_mode="HTML")
        return
    await generic_lookup(cnic, user_id, chat_id, PAK_FAMILY_API_ENDPOINT, "Pak Family Search", "Pakistani Family Information", chat_type, sent_message, is_valid_cnic, credit_cost=credit_cost)

async def perform_gst_lookup(gst: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(gst, user_id, chat_id, GST_API_ENDPOINT, "GST Search", "GSTIN", chat_type, sent_message, is_valid_gstin, credit_cost=credit_cost)

async def perform_pan_lookup(pan: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(pan, user_id, chat_id, PAN_API_ENDPOINT, "PAN Search", "PAN Card", chat_type, sent_message, is_valid_pan, credit_cost=credit_cost)

async def perform_imei_lookup_with_retry(imei: str, max_retries: int = 2):
    for attempt in range(max_retries + 1):
        try:
            wait_time = 2 ** attempt
            if attempt > 0:
                logger.info(f"IMEI API retry attempt {attempt} after {wait_time} seconds")
                await asyncio.sleep(wait_time)
            
            response = requests.get(IMEI_API_ENDPOINT.format(term=imei), timeout=15)
            response.raise_for_status()
            
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                if 'error' in response.text.lower():
                    return {"error": response.text}
                return {"response": response.text[:200]}
                
        except requests.exceptions.Timeout:
            logger.warning(f"IMEI API timeout on attempt {attempt}")
            if attempt == max_retries:
                return {"error": "API timeout after multiple attempts"}
        except requests.exceptions.ConnectionError:
            logger.warning(f"IMEI API connection error on attempt {attempt}")
            if attempt == max_retries:
                return {"error": "API connection failed after multiple attempts"}
        except requests.exceptions.RequestException as e:
            logger.warning(f"IMEI API request error on attempt {attempt}: {e}")
            if attempt == max_retries:
                return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in IMEI lookup attempt {attempt}: {e}")
            if attempt == max_retries:
                return {"error": f"Unexpected error: {str(e)}"}
    
    return {"error": "Maximum retry attempts exceeded"}

async def perform_imei_lookup(imei: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    if not is_valid_imei(imei):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 15-digit IMEI number.", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 15-digit IMEI number.", parse_mode="HTML")
        return
    
    if not sent_message:
        sent_message = await bot.send_message(chat_id, "🔍 Searching for IMEI details...")

    try:
        data = await perform_imei_lookup_with_retry(imei)
        
        should_refund = False
        if 'error' in data:
            error_msg = data['error']
            await sent_message.edit_text(f"❌ IMEI lookup failed: {error_msg}" + get_info_footer(user_id, chat_type, credit_cost, True))
            should_refund = True
        elif not data or (isinstance(data, dict) and ('error' in data or 'Error' in data or 'msg' in data or 'message' in data)):
            await sent_message.edit_text(f"🤷 No details found for IMEI: <code>{html.escape(imei)}</code>." + get_info_footer(user_id, chat_type, credit_cost, True), parse_mode="HTML")
            should_refund = True
        
        if should_refund:
            refund_credits(user_id, credit_cost)
            log_user_action(user_id, "Refunded IMEI Search", f"Refunded {credit_cost} credits - no data found")
            return
        
        if isinstance(data, (dict, list)):
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            formatted_data = str(data)
        
        result_text = f"🔍 <b>IMEI Details for <code>{html.escape(imei)}</code></b>\n\n<pre>{html.escape(formatted_data)}</pre>"
        result_text += get_info_footer(user_id, chat_type, credit_cost)
        
        await sent_message.edit_text(result_text, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"IMEI lookup general error: {e}")
        await sent_message.edit_text(f"❌ An unexpected error occurred during IMEI search: {str(e)}" + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)

async def perform_pincode_lookup(pincode: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(pincode, user_id, chat_id, PINCODE_API_ENDPOINT, "Pincode Search", "Pincode", chat_type, sent_message, is_valid_pincode, credit_cost=credit_cost)

async def perform_freefire_lookup(uid: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(uid, user_id, chat_id, FREEFIRE_API_ENDPOINT, "Free Fire Search", "Free Fire UID", chat_type, sent_message, lambda x: x.isdigit() and 5 <= len(x) <= 15, credit_cost=credit_cost)

async def perform_cnic_lookup(cnic: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    await generic_lookup(cnic, user_id, chat_id, CNIC_API_ENDPOINT, "CNIC Search", "Pakistani CNIC Basic", chat_type, sent_message, is_valid_cnic, credit_cost=credit_cost)

async def perform_tg_username_lookup(username: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    username = username.lstrip('@')
    if not is_valid_telegram_username(username):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid Telegram username (without @).", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid Telegram username (without @).", parse_mode="HTML")
        return
    await generic_lookup(username, user_id, chat_id, TELEGRAM_USERNAME_API_ENDPOINT, "Telegram Username Search", "Telegram Username", chat_type, sent_message, is_valid_telegram_username, credit_cost=credit_cost)

async def perform_instagram_lookup(username: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    username = username.lstrip('@')
    if not is_valid_instagram_username(username):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid Instagram username (without @).", parse_mode="HTML")
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid Instagram username (without @).", parse_mode="HTML")
        return
    await generic_lookup(username, user_id, chat_id, INSTAGRAM_API_ENDPOINT, "Instagram Search", "Instagram", chat_type, sent_message, is_valid_instagram_username, credit_cost=credit_cost)

async def perform_sms_bomber_action(phone_number: str, user_id: int, chat_id: int, chat_type: str = "private", sent_message: types.Message = None, credit_cost: int = 1):
    phone_number = phone_number.strip()
    if not (phone_number.isdigit() and len(phone_number) == 10):
        if sent_message:
            await sent_message.edit_text("❌ <b>Invalid Input:</b> Please send a valid 10-digit mobile number.", parse_mode='HTML')
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit mobile number.", parse_mode='HTML')
        return

    if not sent_message:
        sent_message = await bot.send_message(chat_id, "💣 Initializing SMS Bomber on target...")

    try:
        response = requests.get(SMS_BOMBER_API_ENDPOINT.format(term=phone_number), timeout=15)
        response.raise_for_status()
        
        data = response.json()
        result_text = f"💣 <b>SMS Bomber Initiated!</b>\n\nTarget: <code>{html.escape(phone_number)}</code>\n\n"
        result_text += f"API Response: <pre>{html.escape(json.dumps(data, indent=2, ensure_ascii=False))}</pre>"
        result_text += get_info_footer(user_id, chat_type, credit_cost)
        
        await sent_message.edit_text(result_text, parse_mode="HTML")

    except requests.exceptions.RequestException as e:
        logger.error(f"SMS Bomber API Error: {e}")
        await sent_message.edit_text("❌ The SMS Bomber service is currently unavailable." + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)
    except Exception as e:
        logger.error(f"SMS Bomber General Error: {e}")
        await sent_message.edit_text("❌ An unexpected error occurred during SMS Bomber initiation." + get_info_footer(user_id, chat_type, credit_cost, True))
        refund_credits(user_id, credit_cost)

@dp.message(UserStates.awaiting_redeem_code)
async def handle_redeem_code(message: Message, state: FSMContext):
    code_text = message.text.strip()
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user_data = get_user_data(user_id)

    if not user_data:
        await message.answer("Please /start the bot first to create an account.")
        await state.clear()
        return

    last_redeem_time = user_data.get("last_redeem_timestamp", 0)
    current_time = time.time()

    if current_time - last_redeem_time < 3600:
        time_left = int((3600 - (current_time - last_redeem_time)) / 60)
        await message.answer(f"⏳ You are on a cooldown. Please try again in about {time_left+1} minutes.")
        await state.clear()
        return

    code = code_text.upper()
    
    try:
        code_ref = db.collection("redeem_codes").document(code)
        code_doc = code_ref.get()
        
        if not code_doc.exists:
            await message.answer("❌ Invalid code.")
            await state.clear()
            return
            
        code_data = code_doc.to_dict()
        if code in user_data.get("redeemed_codes", []):
            await message.answer("⚠️ You have already used this code.")
            await state.clear()
            return
        
        if code_data.get("uses_left", 0) <= 0:
            await message.answer("⌛ This code has no uses left.")
            await state.clear()
            return

        credits_to_add = code_data.get("credits", 10)
        
        add_credits(user_id, credits_to_add)
        
        redeemed_codes = user_data.get("redeemed_codes", [])
        redeemed_codes.append(code)
        
        update_user_data(user_id, {
            "redeemed_codes": redeemed_codes,
            "last_redeem_timestamp": current_time
        })
        
        code_ref.update({"uses_left": code_data.get("uses_left", 0) - 1})
        
        log_user_action(user_id, "Redeemed Code", f"Code: {code}, Credits: {credits_to_add}")
        await message.answer(f"✅ Success! <b>{credits_to_add} credits</b> have been added to your account.", parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Firebase redeem code error: {e}")
        await message.answer("❌ Error processing redeem code. Please try again later.")
    
    await state.clear()

@dp.message(Command("credits"))
async def cmd_credits(message: Message):
    user = message.from_user
    user_data = get_user_data(user.id)
    
    if not user_data:
        await message.answer("❌ Please /start the bot first.")
        return
    
    credits = get_user_credits(user.id)
    purchased_credits = user_data.get("total_purchased_credits", 0)
    admin_credits = user_data.get("admin_credits", 0)
    referral_credits = user_data.get("referral_credits_earned", 0)
    first_time_bonus = "✅ Given" if user_data.get("first_time_bonus_given", False) else "❌ Not given"
    
    credits_text = f"💎 <b>Your Credit Balance</b>\n\n"
    credits_text += f"👤 User ID: <code>{user.id}</code>\n"
    credits_text += f"💎 Total Credits: <b>{credits}</b>\n\n"
    credits_text += f"<b>Breakdown:</b>\n"
    credits_text += f"• First-time Bonus: {first_time_bonus}\n"
    credits_text += f"• Purchased Credits: {purchased_credits}\n"
    credits_text += f"• Admin Granted Credits: {admin_credits}\n"
    credits_text += f"• Referral Credits Earned: {referral_credits}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅️ Get Free Credits", callback_data='get_referral')]
    ])
    
    await message.answer(credits_text, parse_mode="HTML", reply_markup=keyboard)

@dp.message(Command("referral"))
async def cmd_referral(message: Message):
    user = message.from_user
    referral_link = f"https://t.me/{BOT_USERNAME.lstrip('@')}?start={user.id}"
    current_ref_count = get_referral_count(user.id)
    user_data = get_user_data(user.id)
    referral_credits = user_data.get("referral_credits_earned", 0) if user_data else 0

    message_text = (
        f"✅️ <b>Get Free Credits</b>\n\n"
        f"<b>Your Referral Link:</b>\n<code>{referral_link}</code>\n\n"
        f"<b>Current Stats:</b>\n"
        f"📊 Total Referrals: <b>{current_ref_count}</b>\n"
        f"💎 Credits Earned: <b>{referral_credits}</b>\n\n"
        f"<b>🎁 Rewards:</b>\n"
        f"✅ Each referral: <b>{REFERRAL_CREDITS} credits</b>\n\n"
        f"<b>You'll get instant notifications</b> when someone joins using your link!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Buy Paid Credits", callback_data='buy_credits')]
    ])
    
    await message.answer(message_text, parse_mode="HTML", reply_markup=keyboard)

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return

    await message.answer(
        "👑 <b>Welcome to the Admin Panel</b>\n\nSelect an option to manage the bot.",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )

@dp.message(Command("addadmin"))
async def cmd_addadmin(message: Message):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Usage: /addadmin <user_id>")
        return
    
    try:
        new_admin_id = int(parts[1])
        admins = load_collection("admins")
        
        if new_admin_id in admins:
            await message.answer(f"User {new_admin_id} is already an admin.")
        else:
            admins.append(new_admin_id)
            save_collection(admins, "admins")
            await message.answer(f"✅ User {new_admin_id} has been added as admin.")
            log_user_action(user.id, "Add Admin", f"Added user {new_admin_id} as admin")
    except ValueError:
        await message.answer("❌ Invalid user ID.")

@dp.message(Command("removeadmin"))
async def cmd_removeadmin(message: Message):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Usage: /removeadmin <user_id>")
        return
    
    try:
        admin_id = int(parts[1])
        admins = load_collection("admins")
        
        if admin_id not in admins:
            await message.answer(f"User {admin_id} is not an admin.")
        else:
            admins.remove(admin_id)
            save_collection(admins, "admins")
            await message.answer(f"✅ User {admin_id} has been removed from admins.")
            log_user_action(user.id, "Remove Admin", f"Removed user {admin_id} from admins")
    except ValueError:
        await message.answer("❌ Invalid user ID.")

@dp.message(Command("addcredit"))
async def cmd_addcredit(message: Message):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return
    
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("❌ Usage: /addcredit <user_id> <amount>")
        return
    
    try:
        target_id = int(parts[1])
        amount = int(parts[2])
        
        if amount <= 0:
            await message.answer("❌ Amount must be positive.")
            return
        
        success, total_credits = add_admin_credits(target_id, amount)
        
        if success:
            await message.answer(f"✅ Added {amount} permanent admin credits to user {target_id}. Total credits: {total_credits}")
            log_user_action(user.id, "Add Credits", f"User {target_id}: +{amount} permanent credits")
        else:
            await message.answer(f"❌ Failed to add credits to user {target_id}.")
    except ValueError:
        await message.answer("❌ Invalid user ID or amount.")

@dp.message(Command("adminlist"))
async def cmd_adminlist(message: Message):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return
    
    admins = load_collection("admins")
    admin_list = "\n".join([f"• {admin_id}" for admin_id in admins])
    
    if admin_list:
        await message.answer(f"📋 <b>Admin List:</b>\n\n{admin_list}", parse_mode="HTML")
    else:
        await message.answer("📋 <b>No additional admins found.</b>", parse_mode="HTML")

@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Usage: /broadcast <message>")
        return
    
    broadcast_text = parts[1]
    await state.set_state(AdminStates.awaiting_broadcast)
    await state.update_data(broadcast_text=broadcast_text)
    await message.answer(f"📢 Ready to broadcast:\n\n{broadcast_text}\n\nConfirm? (yes/no)")

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    user = message.from_user
    if not is_user_admin(user.id):
        await message.answer("❌ Admin access required!")
        return
    
    try:
        user_data = load_collection("users")
        premium_users = load_collection("premium_users")
        banned_users = load_collection("banned_users")
        admins = load_collection("admins")
    except Exception as e:
        logger.error(f"Error loading collections for stats: {e}")
        await message.answer("❌ Error loading statistics.")
        return
    
    today_str = datetime.now().strftime("%Y-%m-%d")    
    active_users_today = set()    
    active_users_week = set()    
    
    week_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)    
    
    for user_id_str, user_data_item in user_data.items():    
        join_date = user_data_item.get("join_date", "")
        if join_date.startswith(today_str):    
            active_users_today.add(user_id_str)
        
        try:
            join_timestamp = datetime.strptime(join_date, "%Y-%m-%d %H:%M:%S").timestamp()
            if join_timestamp >= week_ago:
                active_users_week.add(user_id_str)
        except ValueError:
            pass
    
    total_credits = 0
    total_purchased_credits = 0
    for uid, udata in user_data.items():
        total_credits += udata.get("credits", 0)
        total_purchased_credits += udata.get("total_purchased_credits", 0)

    stats_message = (    
        f"📊 <b>Bot Statistics</b>\n\n"    
        f"<b>Overall:</b>\n"    
        f"👥 Total Users: <b>{len(user_data)}</b>\n"    
        f"💎 Total Credits in System: <b>{total_credits}</b>\n"    
        f"💰 Total Purchased Credits: <b>{total_purchased_credits}</b>\n"    
        f"⭐ Permanent Premium Users: <b>{len(premium_users)}</b>\n"    
        f"👑 Admins: <b>{len(admins)}</b>\n"    
        f"🚫 Banned Users: <b>{len(banned_users)}</b>\n\n"    
            
        f"<b>Activity (Today):</b>\n"    
        f"📈 New Users Today: <b>{len(active_users_today)}</b>\n\n"    
            
        f"<b>Activity (Week):</b>\n"    
        f"🏃‍♂️ New Users This Week: <b>{len(active_users_week)}</b>"    
    )    
    await message.answer(stats_message, parse_mode="HTML")

@dp.callback_query(F.data.startswith("admin_"))
async def handle_admin_callback(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    if not is_user_admin(user.id):
        await callback.answer("❌ Admin access required!", show_alert=True)
        return

    data = callback.data

    if data == 'admin_stats':
        try:
            user_data = load_collection("users")
            premium_users = load_collection("premium_users")
            banned_users = load_collection("banned_users")
            admins = load_collection("admins")
        except Exception as e:
            logger.error(f"Error loading collections for stats: {e}")
            await callback.answer("❌ Error loading statistics.", show_alert=True)
            return
        
        today_str = datetime.now().strftime("%Y-%m-%d")    
        searches_today = 0    
        total_searches = 0    
        active_users_today = set()    
        active_users_week = set()    
        search_type_counts = defaultdict(int)    

        week_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)    
        
        try:
            history_ref = db.collection("user_history")
            history_docs = history_ref.stream()
            
            for doc in history_docs:
                history_data = doc.to_dict()
                actions = history_data.get("actions", [])
                user_id_str = doc.id
                
                for action in actions:
                    if "Search" in action['action']:
                        total_searches += 1
                        search_type_counts[action['action']] += 1
                    
                    try:
                        action_time = datetime.strptime(action['timestamp'], "%Y-%m-%d %H:%M:%S").timestamp()
                        if action['timestamp'].startswith(today_str):
                            active_users_today.add(user_id_str)
                            if "Search" in action['action']:
                                searches_today += 1
                            
                        if action_time >= week_ago:
                            active_users_week.add(user_id_str)
                    except ValueError:
                        logger.warning(f"Skipping badly formatted timestamp: {action['timestamp']}")
        except Exception as e:
            logger.error(f"Error loading history: {e}")
        
        active_codes = 0
        try:
            codes_ref = db.collection("redeem_codes")
            codes_docs = codes_ref.stream()
            for doc in codes_docs:
                code_data = doc.to_dict()
                if code_data.get('uses_left', 0) > 0:
                    active_codes += 1
        except Exception as e:
            logger.error(f"Error counting active codes: {e}")

        most_common_search = max(search_type_counts, key=search_type_counts.get) if search_type_counts else "None"

        total_credits = 0
        total_purchased_credits = 0
        total_admin_credits = 0
        for uid, udata in user_data.items():
            total_credits += udata.get("credits", 0)
            total_purchased_credits += udata.get("total_purchased_credits", 0)
            total_admin_credits += udata.get("admin_credits", 0)

        stats_message = (
            f"📊 <b>Bot Statistics</b>\n\n"
            f"<b>Overall:</b>\n"
            f"👥 Total Users: <b>{len(user_data)}</b>\n"
            f"💎 Total Credits: <b>{total_credits}</b>\n"
            f"💰 Purchased Credits: <b>{total_purchased_credits}</b>\n"
            f"👑 Admin Credits: <b>{total_admin_credits}</b>\n"
            f"⭐ Permanent Premium Users: <b>{len(premium_users)}</b>\n"
            f"👑 Admins: <b>{len(admins)}</b>\n"
            f"🚫 Banned Users: <b>{len(banned_users)}</b>\n"
            f"🎫 Active Codes: <b>{active_codes}</b>\n\n"
                
            f"<b>Activity (Today):</b>\n"
            f"📈 Searches Today: <b>{searches_today}</b>\n"
            f"🏃‍♂️ Active Users Today: <b>{len(active_users_today)}</b>\n\n"
                
            f"<b>Activity (All Time):</b>\n"
            f"💹 Total Searches: <b>{total_searches}</b>\n"
            f"🏃‍♂️ Active Users (Week): <b>{len(active_users_week)}</b>\n"
            f"🔝 Top Search: <b>{most_common_search}</b>"
        )
        await callback.message.edit_caption(stats_message, reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == 'admin_referral_stats':
        try:
            user_data = load_collection("users")
        except Exception as e:
            logger.error(f"Error loading users for referral stats: {e}")
            await callback.answer("❌ Error loading referral statistics.", show_alert=True)
            return

        total_referrals = sum(user.get('referral_count', 0) for user in user_data.values())
        total_referral_credits = sum(user.get('referral_credits_earned', 0) for user in user_data.values())
        users_with_referrals = sum(1 for user in user_data.values() if user.get('referral_count', 0) > 0)
        top_referrers = sorted([(uid, user.get('referral_count', 0), user.get('referral_credits_earned', 0)) for uid, user in user_data.items()],
                              key=lambda x: x[1], reverse=True)[:10]
        
        stats_message = (
            f"📈 <b>Referral Statistics</b>\n\n"
            f"<b>Overall:</b>\n"
            f"🔗 Total Referrals: <b>{total_referrals}</b>\n"
            f"💎 Total Referral Credits: <b>{total_referral_credits}</b>\n"
            f"👥 Users with Referrals: <b>{users_with_referrals}</b>\n\n"
            f"<b>Top Referrers:</b>\n"
        )
        
        for i, (uid, count, credits) in enumerate(top_referrers, 1):
            stats_message += f"{i}. User {uid}: <b>{count}</b> referrals ({credits} credits)\n"
        
        await callback.message.edit_caption(stats_message, reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == 'admin_view_all_users':
        try:
            users = load_collection("users")
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            await callback.answer("❌ Error loading users.", show_alert=True)
            return
            
        if not users:
            await callback.answer("No users found.", show_alert=True)
            return

        user_list_text = "👥 **All Users**\n\n"
        for uid, udata in users.items():
            try:
                premium_users = load_collection("premium_users")
                premium_status = "⭐" if int(uid) in premium_users else ""
                
                credits = udata.get('credits', 0)
                purchased_credits = udata.get('total_purchased_credits', 0)
                admin_credits = udata.get('admin_credits', 0)
                
                referral_count = udata.get('referral_count', 0)
                ref_status = f"🔗{referral_count}" if referral_count > 0 else ""
                
                credits_status = f"💎{credits}"
                if purchased_credits > 0:
                    credits_status += f"(P{purchased_credits})"
                if admin_credits > 0:
                    credits_status += f"(A{admin_credits})"
                
                user_list_text += f"`{uid}` - {credits_status} {premium_status} {ref_status}\n"
            except Exception as e:
                logger.error(f"Error processing user {uid}: {e}")
                continue
        
        if len(user_list_text) > 4000:
            with open("all_users.txt", "w") as f:
                f.write(user_list_text)
            await bot.send_document(chat_id=callback.from_user.id, document=FSInputFile("all_users.txt"), caption="User list is too long.")
            os.remove("all_users.txt")
        else:
            await callback.message.edit_caption(user_list_text, reply_markup=get_admin_keyboard(), parse_mode='Markdown')

    elif data == 'admin_view_blocked':
        try:
            blocked = load_collection("banned_users")
        except Exception as e:
            logger.error(f"Error loading blocked users: {e}")
            await callback.answer("❌ Error loading blocked users.", show_alert=True)
            return
            
        if not blocked:
            await callback.answer("No blocked users.", show_alert=True)
            return

        text = "🚫 **Blocked Users**\n\n`" + '`\n`'.join(map(str, blocked)) + '`'
        await callback.message.edit_caption(text, reply_markup=get_admin_keyboard(), parse_mode='Markdown')

    elif data == 'admin_view_premium':
        try:
            premium = load_collection("premium_users")
        except Exception as e:
            logger.error(f"Error loading premium users: {e}")
            await callback.answer("❌ Error loading premium users.", show_alert=True)
            return

        if not premium:
            text = "⭐ **Premium Users**\n\nNo permanent premium users."
        else:
            users = '`\n`'.join(map(str, premium))
            text = f"⭐ **Permanent Premium Users**\n\n`{users}`"

        await callback.message.edit_caption(
            text,
            reply_markup=get_admin_keyboard(),
            parse_mode='Markdown'
        )

    elif data == 'admin_list':
        try:
            admins = load_collection("admins")
        except Exception as e:
            logger.error(f"Error loading admins: {e}")
            await callback.answer("❌ Error loading admin list.", show_alert=True)
            return
            
        admin_list = "\n".join([f"• {admin_id}" for admin_id in admins])
        
        if admin_list:
            await callback.message.edit_caption(f"📋 <b>Admin List:</b>\n\n{admin_list}", parse_mode="HTML", reply_markup=get_admin_keyboard())
        else:
            await callback.message.edit_caption("📋 <b>No additional admins found.</b>", parse_mode="HTML", reply_markup=get_admin_keyboard())

    elif data == 'admin_add_credits':
        await state.set_state(AdminStates.awaiting_add_credits)
        await callback.message.edit_caption("➕ <b>Add Permanent Admin Credits</b>\n\nSend user ID and amount separated by space (e.g., 12345678 5)", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data='back_to_main')]
        ]))

    else:
        prompts = {
            'admin_add_time': (AdminStates.awaiting_add_time, "➡️ Send the User ID and Days, separated by a space (e.g., 12345678 7)."),
            'admin_remove_time': (AdminStates.awaiting_remove_time, "➡️ Send the User ID and Days to remove (e.g., 12345678 3)."),
            'admin_add_premium': (AdminStates.awaiting_premium_add, "➡️ Send the User ID to make a premium member."),
            'admin_remove_premium': (AdminStates.awaiting_premium_remove, "➡️ Send the User ID to remove from premium."),
            'admin_add_admin': (AdminStates.awaiting_add_time, "➡️ Send the User ID to add as admin."),
            'admin_remove_admin': (AdminStates.awaiting_remove_time, "➡️ Send the User ID to remove from admins."),
            'admin_user_history': (AdminStates.awaiting_history_id, "➡️ Send the User ID to view their history."),
            'admin_broadcast': (AdminStates.awaiting_broadcast, "➡️ Send the message you want to broadcast (supports HTML)."),
            'admin_ban_user': (AdminStates.awaiting_ban_id, "➡️ Send the User ID to ban."),
            'admin_unban_user': (AdminStates.awaiting_unban_id, "➡️ Send the User ID to unban."),
            'admin_gen_code': (AdminStates.awaiting_gen_code, "🎫 Send credits and uses separated by space (e.g., 50 5 for 50 credits with 5 uses)"),
        }
        if data in prompts:
            state_class, message_text = prompts[data]
            await state.set_state(state_class)
            await callback.message.edit_caption(message_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Back", callback_data='back_to_main')]
            ]))

    await callback.answer()

@dp.message(AdminStates.awaiting_add_credits)
async def handle_admin_add_credits(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Invalid format")

        target_id, amount = int(parts[0]), int(parts[1])
        
        if amount <= 0:
            await message.answer("❌ Amount must be positive.")
            return
        
        success, total_credits = add_admin_credits(target_id, amount)
        
        if success:
            await message.answer(f"✅ Added {amount} permanent admin credits to user {target_id}. Total credits: {total_credits}", parse_mode='Markdown')
            log_user_action(message.from_user.id, "Admin Add Credits", f"User {target_id}: +{amount} permanent credits")
        else:
            await message.answer(f"❌ Failed to add credits to user {target_id}.", parse_mode='Markdown')
    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: USER_ID AMOUNT")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_broadcast)
async def handle_admin_broadcast(message: Message, state: FSMContext):
    try:
        user_ids = list(load_collection("users").keys())
    except Exception as e:
        logger.error(f"Error loading users for broadcast: {e}")
        await message.answer("❌ Error loading users for broadcast.")
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())
        return
        
    await message.answer(f"📢 Starting broadcast to {len(user_ids)} users...")

    s_count, f_count = 0, 0
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=int(uid), text=message.text, parse_mode="HTML")
            s_count += 1
        except Exception:
            f_count += 1
        await asyncio.sleep(0.02)

    await message.answer(f"Broadcast finished!\n\n✅ Sent: {s_count}\n❌ Failed: {f_count}")
    log_user_action(message.from_user.id, "Admin Broadcast", f"Sent: {s_count}, Failed: {f_count}")
    await state.clear()
    await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_history_id)
async def handle_admin_history_id(message: Message, state: FSMContext):
    target_id_str = message.text.strip()
    
    try:
        history_ref = db.collection("user_history").document(target_id_str)
        doc = history_ref.get()
        
        if not doc.exists:
            await message.answer(f"No history found for user `{target_id_str}`.", parse_mode='Markdown')
        else:
            history_data = doc.to_dict()
            history = history_data.get("actions", [])
            
            if not history:
                await message.answer(f"No history found for user `{target_id_str}`.", parse_mode='Markdown')
            else:
                history_text = f"📜 History for User `{target_id_str}`\n\n"
                for entry in history[:20]:
                    history_text += f"• `{entry['timestamp']}` - **{entry['action']}**: {entry['details']}\n"
                if len(history) > 20:
                    history_text += f"\n... and {len(history) - 20} more entries"
                await message.answer(history_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        await message.answer(f"Error loading history for user `{target_id_str}`.", parse_mode='Markdown')

    await state.clear()
    await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_ban_id)
async def handle_admin_ban_id(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        banned_users = load_collection("banned_users")

        if target_id in banned_users:
            await message.answer(f"User {target_id} is already banned.", parse_mode='Markdown')
        else:
            banned_users.append(target_id)
            save_collection(banned_users, "banned_users")
            await message.answer(f"🚫 User {target_id} has been banned.", parse_mode='Markdown')
            log_user_action(message.from_user.id, "Admin Ban User", f"User {target_id}")

    except ValueError:
        await message.answer("❌ Invalid user ID.")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_unban_id)
async def handle_admin_unban_id(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        banned_users = load_collection("banned_users")

        if target_id not in banned_users:
            await message.answer(f"User {target_id} is not banned.", parse_mode='Markdown')
        else:
            banned_users.remove(target_id)
            save_collection(banned_users, "banned_users")
            await message.answer(f"✅ User {target_id} has been unbanned.", parse_mode='Markdown')
            log_user_action(message.from_user.id, "Admin Unban User", f"User {target_id}")

    except ValueError:
        await message.answer("❌ Invalid user ID.")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_gen_code)
async def handle_admin_gen_code(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Invalid format")

        credits, uses = int(parts[0]), int(parts[1])

        code = f"CREDIT-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
        
        try:
            code_ref = db.collection("redeem_codes").document(code)
            code_ref.set({
                "credits": credits,
                "uses_left": uses,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            await message.answer(
                f"✅ Code generated successfully!\n\n"
                f"Code: `{code}`\n"
                f"Credits: {credits}\n"
                f"Uses: {uses}",
                parse_mode='Markdown'
            )
            log_user_action(message.from_user.id, "Admin Generate Code", f"Code: {code}, Credits: {credits}, Uses: {uses}")
        except Exception as e:
            logger.error(f"Firebase save code error: {e}")
            await message.answer("❌ Failed to save code to database.")

    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: CREDITS USES")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

async def main():
    logger.info("🚀 Starting Credit-Based OSINT Bot...")

    global BOT_USERNAME
    try:
        me = await bot.get_me()
        BOT_USERNAME = f"@{me.username}"
        logger.info(f"Bot username: {BOT_USERNAME}")
    except Exception as e:
        logger.warning(f"Could not fetch bot username: {e}. Using hardcoded value: {BOT_USERNAME}")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
