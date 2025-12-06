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
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- ⚙️ CONFIGURATION ---

BOT_TOKEN = os.getenv("BOT_TOKEN", "7893988621:AAH5RGk7O5jjHG29PVBGBt-cmywIdFv5w0c")
BOT_USERNAME = "@GG_B4N_Bot"

# Your numeric Telegram User ID. Add multiple IDs separated by commas.
ADMIN_IDS = [7704212317]

# This ID is for the direct "Contact Admin" or "Support" button.
SUPPORT_USER_ID = 7704212317

# Log Channel ID (New Requirement)
LOG_CHANNEL_ID = -1003027221674

# Image URLs (New Requirement)
START_IMAGE_URL = "https://i.postimg.cc/g2Z04CyS/IMG-20250927-192202-536.jpg"
MENU_IMAGE_URL = "https://postimg.cc/c6tGj2W8"

# --- CHANNEL JOIN CONFIGURATION ---

CHANNEL_1_INVITE_LINK = "https://t.me/DarkByteNet"
REQUIRED_CHANNEL_1_ID = -1002906038515

CHANNEL_2_INVITE_LINK = "https://t.me/BinaryRebel"
REQUIRED_CHANNEL_2_ID = -1002801307481

CHANNEL_3_INVITE_LINK = "https://t.me/+nxKQdZMYJ4s3Y2M1"
REQUIRED_CHANNEL_3_ID = -1003417241446

CHANNEL_4_INVITE_LINK = "https://t.me/TrueXFinder"
REQUIRED_CHANNEL_4_ID = -1003072370472

# File ID for the welcome video (Kept for fallback/alternative usage)
WELCOME_VIDEO_FILE_ID = os.getenv("WELCOME_VIDEO_FILE_ID", "BAACAgUAAxkBAAIHnmjJPy8bkHgXv8GPYOiXmykEwH8OAAJDFwAC4eVIVqPjvh9F68VQNgQ")

# --- 🛰️ API ENDPOINTS (EXISTING) ---

PHONE_API_ENDPOINT = "https://gauravapi.gauravyt492.workers.dev/?mobile={num}"
PAK_PHONE_API_ENDPOINT = "https://pak-info.gauravyt566.workers.dev/?num={num}"
AADHAAR_API_ENDPOINT = "https://aadhar.gauravyt492.workers.dev/?aadhar={aadhar}"
FAMILY_INFO_API_ENDPOINT = "https://ration-info.vercel.app/fetch?key=paidchx&aadhaar={aadhaar}"
VEHICLE_API_ENDPOINT = "https://challan-api.gauravyt566.workers.dev/?vehicle={rc_number}"
IFSC_API_ENDPOINT = "https://ifsc-info.gauravyt492.workers.dev/?ifsc={ifsc}"
IP_API_ENDPOINT = "https://ip-info.gauravyt566.workers.dev/?ip={ip}"
TG_INFO_API_ENDPOINT = "https://tg-info-neon.vercel.app/user-details?user={user_id}"
PAK_FAMILY_API_ENDPOINT = "https://paknuminfo-by-narcos.vercel.app/api/familyinfo?cnic={cnic}"

# --- 🛰️ API ENDPOINTS (NEWLY ADDED) ---

UPI_API_ENDPOINT = 'https://gaurav-upi-inf.gauravyt566.workers.dev/?upi={term}'
GST_API_ENDPOINT = 'https://gst.gauravyt492.workers.dev/?gst={term}'
PAN_API_ENDPOINT = 'https://pan.gauravyt566.workers.dev/?pan={term}'
PAN_GST_API_ENDPOINT = 'https://pan-gst.gauravyt566.workers.dev/?pan={term}'
RC_MOBILE_API_ENDPOINT = 'https://veh.gauravyt566.workers.dev/vehicle?key=GAU123&vno={term}'
IMEI_API_ENDPOINT = 'https://imei-info.gauravyt566.workers.dev/?imei={term}'
PINCODE_API_ENDPOINT = 'https://pincode-info.gauravyt566.workers.dev/?pincode={term}'
FREEFIRE_API_ENDPOINT = 'https://ff-info.gauravyt566.workers.dev/?uid={term}'
PAK_NUM_API_ENDPOINT_NEW = 'https://pak-info.gauravyt566.workers.dev/?num={term}'
CNIC_API_ENDPOINT = 'https://pak-info.gauravyt566.workers.dev/?cnic={term}'
VEHICLE_BASIC_API_ENDPOINT = 'https://vehicle.gauravyt566.workers.dev/?vehicle_no={term}'
SMS_BOMBER_API_ENDPOINT = 'https://sms-bomber.gauravyt566.workers.dev/?num={term}'

# --- 💾 DATA FILES ---

USER_DATA_FILE = "users.json"
REDEEM_CODES_FILE = "redeem_codes.json"
BANNED_USERS_FILE = "banned_users.json"
PREMIUM_USERS_FILE = "premium_users.json"
FREE_MODE_FILE = "free_mode.json"
USER_HISTORY_FILE = "user_history.json"

# --- CREDITS SETTINGS ---

INITIAL_CREDITS = 3
REFERRAL_CREDITS = 2
SEARCH_COST = 1
RC_MOBILE_COST = 2
REDEEM_COOLDOWN_SECONDS = 3600
DAILY_GROUP_CREDITS = 2  # Daily credits for group users

# --- END OF CONFIGURATION ---

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# States

class UserStates(StatesGroup):
    awaiting_phone = State()
    awaiting_pak_phone = State()
    awaiting_aadhaar = State()
    awaiting_family = State()
    awaiting_vehicle = State()
    awaiting_ifsc = State()
    awaiting_ip = State()
    awaiting_tg = State()
    awaiting_pak_family = State()
    awaiting_redeem_code = State()
    awaiting_upi = State()
    awaiting_gst = State()
    awaiting_pan = State()
    awaiting_pan_gst = State()
    awaiting_rc_mobile = State()
    awaiting_imei = State()
    awaiting_pincode = State()
    awaiting_freefire = State()
    awaiting_cnic = State()
    awaiting_vehicle_basic = State()
    awaiting_sms_bomber = State()

class AdminStates(StatesGroup):
    awaiting_add_credit = State()
    awaiting_remove_credit = State()
    awaiting_premium_add = State()
    awaiting_premium_remove = State()
    awaiting_history_id = State()
    awaiting_broadcast = State()
    awaiting_ban_id = State()
    awaiting_unban_id = State()
    awaiting_gen_code = State()

# --- 💾 Data Management ---

def load_data(filename):
    """Loads data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if 'banned' in filename or 'premium' in filename:
            return []
        if 'free_mode' in filename:
            return {"active": False}
        return {}

def save_data(data, filename):
    """Saves data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {e}")

def is_free_mode_active():
    return load_data(FREE_MODE_FILE).get("active", False)

def set_free_mode(status: bool):
    save_data({"active": status}, FREE_MODE_FILE)

def log_user_action(user_id, action, details=""):
    history = load_data(USER_HISTORY_FILE)
    user_id_str = str(user_id)
    if user_id_str not in history:
        history[user_id_str] = []

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details
    }
    history[user_id_str].insert(0, log_entry)
    history[user_id_str] = history[user_id_str][:50]
    save_data(history, USER_HISTORY_FILE)

async def is_banned(user_id: int) -> bool:
    banned_users = load_data(BANNED_USERS_FILE)
    return user_id in banned_users

async def is_premium(user_id: int) -> bool:
    premium_users = load_data(PREMIUM_USERS_FILE)
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id in premium_users:
        return True

    if user_id_str in user_data:
        user_info = user_data[user_id_str]
        if "premium_until" in user_info:
            premium_until = datetime.fromisoformat(user_info["premium_until"])
            if datetime.now() < premium_until:
                return True
            else:
                if "premium_until" in user_data[user_id_str]:
                    del user_data[user_id_str]["premium_until"]
                    save_data(user_data, USER_DATA_FILE)

    return False

def add_premium_days(user_id: int, days: int):
    """Add premium days to a user"""
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "credits": INITIAL_CREDITS, 
            "referred_by": None, 
            "redeemed_codes": [], 
            "last_redeem_timestamp": 0, 
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }

    premium_until = datetime.now() + timedelta(days=days)
    user_data[user_id_str]["premium_until"] = premium_until.isoformat()
    save_data(user_data, USER_DATA_FILE)

def add_referral_credit(user_id: int, credits: int):
    """Add credits to user for referral"""
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "credits": INITIAL_CREDITS,
            "referred_by": None,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }

    user_data[user_id_str]["credits"] += credits
    save_data(user_data, USER_DATA_FILE)
    logger.info(f"Added {credits} credits to user {user_id} via referral.")

def increment_referral_count(user_id: int):
    """Increment referral count for user"""
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "credits": INITIAL_CREDITS,
            "referred_by": None,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }

    if "referral_count" not in user_data[user_id_str]:
        user_data[user_id_str]["referral_count"] = 0

    user_data[user_id_str]["referral_count"] += 1
    save_data(user_data, USER_DATA_FILE)

    new_count = user_data[user_id_str]["referral_count"]
    logger.info(f"Incremented referral count for user {user_id} to {new_count}")
    return new_count

def get_referral_count(user_id: int) -> int:
    """Get referral count for user"""
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id_str in user_data:
        return user_data[user_id_str].get("referral_count", 0)
    return 0

async def check_membership(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        # If bot is kicked from channel, assume user is not a member
        if "kicked" in str(e).lower() or "forbidden" in str(e).lower():
            return False
        logger.error(f"Error checking membership for user {user_id} in channel {channel_id}: {e}")
        return False

async def is_subscribed(user_id: int) -> bool:
    subscribed_to_1 = await check_membership(user_id, REQUIRED_CHANNEL_1_ID)
    subscribed_to_2 = await check_membership(user_id, REQUIRED_CHANNEL_2_ID)
    subscribed_to_3 = await check_membership(user_id, REQUIRED_CHANNEL_3_ID)
    subscribed_to_4 = await check_membership(user_id, REQUIRED_CHANNEL_4_ID)
    return subscribed_to_1 and subscribed_to_2 and subscribed_to_3 and subscribed_to_4

async def send_join_message(chat_id: int):
    keyboard = [
        [InlineKeyboardButton(text="➡️ Join Channel 1", url=CHANNEL_1_INVITE_LINK)],
        [InlineKeyboardButton(text="➡️ Join Channel 2", url=CHANNEL_2_INVITE_LINK)],
        [InlineKeyboardButton(text="➡️ Join Channel 3", url=CHANNEL_3_INVITE_LINK)],
        [InlineKeyboardButton(text="➡️ Join Channel 4", url=CHANNEL_4_INVITE_LINK)],
        [InlineKeyboardButton(text="✅ Verify", callback_data='verify_join')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    message_text = "<b>You must join all of our channels to use this bot.</b>\n\nPlease join them and then click Verify."
    
    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=START_IMAGE_URL,
            caption=message_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send join photo: {e}. Falling back to text.")
        await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup, parse_mode="HTML")

# --- CREDIT DEDUCTION FUNCTIONS (FIXED) ---

async def deduct_credits(user_id: int, chat_type: str, cost: int = SEARCH_COST) -> bool:
    # Check if it's a group chat
    if chat_type in ["group", "supergroup"]:
        return True

    if is_free_mode_active():
        return True
    if user_id in ADMIN_IDS or await is_premium(user_id):
        return True

    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "credits": INITIAL_CREDITS,
            "referred_by": None,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }
        save_data(user_data, USER_DATA_FILE)

    if user_data[user_id_str].get("credits", 0) >= cost:
        user_data[user_id_str]["credits"] -= cost
        save_data(user_data, USER_DATA_FILE)
        return True
    return False

async def deduct_credits_with_override(user_id: int, chat_type: str, action_name: str) -> bool:
    cost = RC_MOBILE_COST if action_name == "RC Mobile Search" else SEARCH_COST
    
    # Check if it's a group chat
    if chat_type in ["group", "supergroup"]:
        # Check if user has daily credits for RC Mobile in group
        if action_name == "RC Mobile Search":
            user_data = load_data(USER_DATA_FILE)
            user_id_str = str(user_id)
            
            if user_id_str not in user_data:
                user_data[user_id_str] = {
                    "credits": 0,
                    "referred_by": None,
                    "redeemed_codes": [],
                    "last_redeem_timestamp": 0,
                    "referral_count": 0,
                    "last_daily_credits": None,
                    "group_credits": 0
                }
            
            # Check daily credits
            if "group_credits" not in user_data[user_id_str]:
                user_data[user_id_str]["group_credits"] = DAILY_GROUP_CREDITS
            
            if user_data[user_id_str]["group_credits"] >= cost:
                user_data[user_id_str]["group_credits"] -= cost
                save_data(user_data, USER_DATA_FILE)
                return True
            else:
                return False
        return True

    if is_free_mode_active():
        return True
    if user_id in ADMIN_IDS or await is_premium(user_id):
        return True

    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)

    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "credits": INITIAL_CREDITS,
            "referred_by": None,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }

    if user_data[user_id_str].get("credits", 0) >= cost:
        user_data[user_id_str]["credits"] -= cost
        save_data(user_data, USER_DATA_FILE)
        return True
    return False

def get_info_footer(user_id: int, chat_type: str = "private") -> str:
    # For group chats, don't show credits footer
    if chat_type in ["group", "supergroup"]:
        return ""

    if is_free_mode_active():
        return "\n\n✨ <b>Free Mode is ACTIVE!</b> No credits were used for this search."

    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user_id)
    
    if user_id_str not in user_data:
        credits = 0
        group_credits = 0
    else:
        credits = user_data[user_id_str].get("credits", 0)
        group_credits = user_data[user_id_str].get("group_credits", 0)
    
    referral_count = get_referral_count(user_id)

    premium_users = load_data(PREMIUM_USERS_FILE)
    premium_status = ""
    
    if user_id in ADMIN_IDS:
        premium_status = "👑 <b>Admin User</b>"
    elif user_id in premium_users:
        premium_status = "⭐ <b>Premium User</b>"
    else:
        user_info = user_data.get(str(user_id), {})
        if "premium_until" in user_info:
            premium_until = datetime.fromisoformat(user_info["premium_until"])
            if datetime.now() < premium_until:
                time_left = premium_until - datetime.now()
                hours_left = int(time_left.total_seconds() / 3600)
                premium_status = f"⭐ <b>Premium ({hours_left}h left)</b>"

    footer = f"\n\n💰 Credits Remaining: <b>{credits}</b>"
    if chat_type in ["group", "supergroup"] and group_credits > 0:
        footer += f" | 🎯 Group RC Credits: <b>{group_credits}</b>"
    if premium_status:
        footer += f" | {premium_status}"
    if referral_count > 0:
        footer += f"\n📊 Referrals: <b>{referral_count}</b>"

    return footer

async def notify_referral_success(referrer_id: int, new_user_name: str, referral_count: int):
    """Notify referrer about successful referral"""
    try:
        message = f"🎉 <b>New Referral Success!</b>\n\n👤 {html.escape(new_user_name)} joined using your link!\n\n"
        message += f"✅ You've received <b>{REFERRAL_CREDITS} credits</b>\n"
        message += f"📊 Total referrals: <b>{referral_count}</b>"

        await bot.send_message(
            chat_id=referrer_id,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Successfully sent referral notification to user {referrer_id}")
    except Exception as e:
        logger.error(f"Could not notify referrer {referrer_id}: {e}")

def process_referral_system(new_user_id: int, referrer_id: int, new_user_name: str):
    """Process referral system"""
    try:
        add_referral_credit(referrer_id, REFERRAL_CREDITS)
        new_referral_count = increment_referral_count(referrer_id)
        
        log_user_action(referrer_id, "Referral Success", f"Referred user {new_user_id} ({new_user_name})")
        log_user_action(new_user_id, "Joined via Referral", f"Referred by {referrer_id}")
        
        logger.info(f"Referral processed: {referrer_id} -> {new_user_id}, credits added: {REFERRAL_CREDITS}")
        
        return new_referral_count

    except Exception as e:
        logger.error(f"Error processing referral system: {e}")
        return 0

async def log_new_user_to_channel(user: types.User):
    try:
        # Check if log channel exists
        try:
            await bot.get_chat(chat_id=LOG_CHANNEL_ID)
        except Exception as e:
            logger.error(f"Log channel not found: {e}")
            return
            
        user_data = load_data(USER_DATA_FILE)
        total_users = len(user_data)
        
        username = f"@{user.username}" if user.username else "(no username)"
        
        message = (
            f"📢 <b>New User started the @{BOT_USERNAME.lstrip('@')}</b>\n\n"
            f"👤 Name: {html.escape(user.full_name)}\n"
            f"🔗 Username: {username}\n"
            f"🆔 UserID: <code>{user.id}</code>\n\n"
            f"📊 Total Users: <b>{total_users}</b>"
        )
        
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"Logged new user {user.id} to channel.")
        
    except Exception as e:
        logger.error(f"Failed to log new user to channel: {e}")

def get_main_keyboard(user_id: int):
    keyboard = [
        [
            InlineKeyboardButton(text="🇮🇳 Mobile", callback_data='search_phone'),
            InlineKeyboardButton(text="🇵🇰 Pak Num", callback_data='search_pak_phone')
        ],
        [
            InlineKeyboardButton(text="🪪 Aadhaar", callback_data='search_aadhaar'),
            InlineKeyboardButton(text="👨‍👩‍👧 Family Info (IN)", callback_data='search_family')
        ],
        [
            InlineKeyboardButton(text="🏦 IFSC", callback_data='search_ifsc'),
            InlineKeyboardButton(text="🌐 IP Lookup", callback_data='search_ip')
        ],
        [
            InlineKeyboardButton(text="👤 TG ID", callback_data='search_tg'),
            InlineKeyboardButton(text="🇵🇰 CNIC (Basic)", callback_data='search_cnic')
        ],
        [
            InlineKeyboardButton(text="👨‍👩‍👧 Pak Family", callback_data='search_pak_family'),
            InlineKeyboardButton(text="💳 UPI ID", callback_data='search_upi')
        ],
        [
            InlineKeyboardButton(text="📦 GSTIN", callback_data='search_gst'),
            InlineKeyboardButton(text="🔖 PAN", callback_data='search_pan')
        ],
        [
            InlineKeyboardButton(text="🔗 PAN -> GST", callback_data='search_pan_gst'),
            InlineKeyboardButton(text="🚗 Vehicle (Adv)", callback_data='search_vehicle')
        ],
        [
            InlineKeyboardButton(text="🏍️ Vehicle (Basic)", callback_data='search_vehicle_basic'),
            InlineKeyboardButton(text="📲 RC Mobile", callback_data='search_rc_mobile')
        ],
        [
            InlineKeyboardButton(text="📟 IMEI", callback_data='search_imei'),
            InlineKeyboardButton(text="📍 Pincode", callback_data='search_pincode')
        ],
        [
            InlineKeyboardButton(text="🎮 Free Fire UID", callback_data='search_freefire'),
            InlineKeyboardButton(text="💣 SMS Bomber", callback_data='search_sms_bomber')
        ],
        [
            InlineKeyboardButton(text="💰 Check Credit", callback_data='check_credit'),
            InlineKeyboardButton(text="Get Referral Link 🔗", callback_data='get_referral')
        ],
        [
            InlineKeyboardButton(text="Redeem Code 🎁", callback_data='redeem_code'),
            InlineKeyboardButton(text="Support 👨‍💻", callback_data='support')
        ]
    ]

    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton(text="👑 Admin Panel", callback_data='admin_panel')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_group_welcome_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="➕ Add me to your group", url=f"https://t.me/{BOT_USERNAME.lstrip('@')}?startgroup=true")],
        [InlineKeyboardButton(text="🔍 Search Commands", callback_data='group_commands')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_group_footer_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="🤫 Use Privately", url=f"https://t.me/{BOT_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text="➕️ Add me to Your Group", url=f"https://t.me/{BOT_USERNAME.lstrip('@')}?startgroup=true")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- CHANNEL JOIN CHECK FOR GROUP COMMANDS ---

async def check_channel_membership_for_group(user_id: int, chat_id: int, message_id: int = None):
    """Check if user has joined all channels and send join message if not"""
    if not await is_subscribed(user_id):
        missing_channels = []
        keyboard_buttons = []
        
        if not await check_membership(user_id, REQUIRED_CHANNEL_1_ID):
            missing_channels.append("Channel 1")
            keyboard_buttons.append([InlineKeyboardButton(text="➡️ Join Channel 1", url=CHANNEL_1_INVITE_LINK)])
        
        if not await check_membership(user_id, REQUIRED_CHANNEL_2_ID):
            missing_channels.append("Channel 2")
            keyboard_buttons.append([InlineKeyboardButton(text="➡️ Join Channel 2", url=CHANNEL_2_INVITE_LINK)])
        
        if not await check_membership(user_id, REQUIRED_CHANNEL_3_ID):
            missing_channels.append("Channel 3")
            keyboard_buttons.append([InlineKeyboardButton(text="➡️ Join Channel 3", url=CHANNEL_3_INVITE_LINK)])
        
        if not await check_membership(user_id, REQUIRED_CHANNEL_4_ID):
            missing_channels.append("Channel 4")
            keyboard_buttons.append([InlineKeyboardButton(text="➡️ Join Channel 4", url=CHANNEL_4_INVITE_LINK)])
        
        if missing_channels:
            keyboard_buttons.append([InlineKeyboardButton(text="✅ Verify", callback_data='verify_join')])
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            message_text = "❌ <b>You must join all our channels to use this bot:</b>\n\n"
            message_text += "\n".join([f"• {channel}" for channel in missing_channels])
            message_text += "\n\nJoin all channels and then click Verify!"
            
            if message_id:
                await bot.send_message(chat_id=chat_id, text=message_text, parse_mode="HTML", reply_markup=reply_markup, reply_to_message_id=message_id)
            else:
                await bot.send_message(chat_id=chat_id, text=message_text, parse_mode="HTML", reply_markup=reply_markup)
            return False
    return True

# --- Start command for private chats ---

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    if await is_banned(user.id):
        return

    # Check if it's a group chat
    if message.chat.type in ["group", "supergroup"]:
        group_welcome_msg = f"""

🤖 Welcome to ADVANCED OSINT BOT
Uncover the unseen. Trace, track & analyze digital footprints with precision.

━━━━━━━━━━━━━━━

🔍 Lookup Commands

🛰️ /num <number> — Indian number intelligence
🛰️ /paknum <number> — Pakistani number lookup
🪪 /aadhaar <id> — Aadhaar information extraction
👨‍👩‍👧 /family <aadhaar> — Linked family details
🚗 /vehicle <rc> — Vehicle registration lookup (Advanced)
🏍️ /vehiclebasic <rc> — Vehicle registration lookup (Basic)
🏦 /ifsc <code> — Bank IFSC details & branch info
🌐 /ip <address> — IP address trace & geolocation
👤 /tgid <id> — Telegram user intelligence
🇵🇰 /pakfamily <cnic> — Pakistani family record lookup
🇵🇰 /cnic <cnic> — Pakistani CNIC basic lookup
💳 /upi <id> — UPI ID lookup
📦 /gst <gstin> — GSTIN lookup
🔖 /pan <pan> — PAN card lookup
🔗 /pangst <pan> — PAN to GST lookup
📲 /rcmobile <rc> — RC owner mobile lookup (Daily 2 credits in groups)
📟 /imei <imei> — IMEI lookup
📍 /pincode <pincode> — Pincode lookup
🎮 /freefire <uid> — Free Fire UID lookup
💣 /smsbomber <num> — SMS Bomber (Use with caution)

━━━━━━━━━━━━━━━

⚙️ Utility Commands

💰 /credits — Check remaining credits
🔗 /referral — Generate your referral link

━━━━━━━━━━━━━━━
🧠 Powered by: @Farazkhan01x
🛡️ Fast • Accurate • Secure • Confidential
━━━━━━━━━━━━━━━
"""
        await message.answer(
            text=group_welcome_msg,
            reply_markup=get_group_welcome_keyboard(),
            parse_mode="Markdown"
        )
        return

    # Private chat logic
    if not await is_subscribed(user.id):
        await send_join_message(message.chat.id)
        return

    user_id_str = str(user.id)
    user_data = load_data(USER_DATA_FILE)

    base_caption = (
        "I am your advanced OSINT bot. Here's what you can do:\n\n"
        "🔍 <b>Lookups:</b> Phone (🇮🇳/🇵🇰), Aadhaar, Vehicle, IP, Bank IFSC, Telegram ID, PAN, GST, UPI, and Pakistan Family/CNIC info.\n\n"
        "💰 <b>Credit System:</b> You start with free credits. Each search costs one credit (RC Mobile costs 2 credits).\n\n"
        "🔗 <b>Referrals:</b> Share your link to earn 2 credits for each successful referral!"
    )
    final_caption = ""

    if user_id_str not in user_data:
        referrer_id = None

        if len(message.text.split()) > 1:
            referral_param = message.text.split()[1]
            if referral_param.isdigit():
                potential_referrer_id = int(referral_param)
                
                if (potential_referrer_id != user.id and 
                    (str(potential_referrer_id) in user_data or potential_referrer_id in ADMIN_IDS)):
                    referrer_id = potential_referrer_id
                    
                    referral_count = process_referral_system(user.id, referrer_id, user.first_name)
                    
                    if referral_count > 0:
                        await notify_referral_success(referrer_id, user.first_name, referral_count)
                    
                    try:
                        await message.answer(
                            f"🎉 You joined using a referral link! Your referrer has been rewarded with {REFERRAL_CREDITS} credits.",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.warning(f"Could not notify new user about referral: {e}")
        
        user_data[user_id_str] = {
            "credits": INITIAL_CREDITS,
            "referred_by": referrer_id,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }
        final_caption = (f"<b>🎉 Welcome, {user.first_name}!</b>\n\n"
                         f"You have <b>{INITIAL_CREDITS} free credits</b> to get started.\n\n{base_caption}")
        save_data(user_data, USER_DATA_FILE)
        log_user_action(user.id, "Joined", f"Referred by: {referrer_id}")
        
        await log_new_user_to_channel(user)

    else:
        final_caption = f"<b>👋 Welcome back, {user.first_name}!</b>\n\n{base_caption}"

    try:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=START_IMAGE_URL,
            caption=final_caption,
            reply_markup=get_main_keyboard(user.id),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send welcome photo: {e}. Falling back to text.")
        await message.answer(
            text=final_caption,
            reply_markup=get_main_keyboard(user.id),
            parse_mode="HTML"
        )

# --- Admin command ---

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    user = message.from_user
    if user.id not in ADMIN_IDS:
        await message.answer("❌ Admin access required!")
        return

    await message.answer(
        "👑 <b>Welcome to the Admin Panel</b>\n\nSelect an option to manage the bot.",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )

# --- Group commands with channel check ---

@dp.message(Command("num"))
async def cmd_num_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    # Check channel membership
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /num <phone_number>", parse_mode="Markdown")
        return
    phone_number = parts[1]
    await perform_phone_lookup(phone_number, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("paknum"))
async def cmd_paknum_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    # Check channel membership
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /paknum <phone_number>", parse_mode="Markdown")
        return
    phone_number = parts[1]
    await perform_pak_phone_lookup(phone_number, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("rcmobile"))
async def cmd_rc_mobile_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    # Check channel membership
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /rcmobile <rc_number>", parse_mode="Markdown")
        return
    
    # Check and reset daily credits for group users
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user.id)
    
    if user_id_str not in user_data:
        user_data[user_id_str] = {
            "credits": 0,
            "referred_by": None,
            "redeemed_codes": [],
            "last_redeem_timestamp": 0,
            "referral_count": 0,
            "last_daily_credits": None,
            "group_credits": 0
        }
    
    today = datetime.now().date().isoformat()
    last_daily = user_data[user_id_str].get("last_daily_credits")
    
    if last_daily != today:
        user_data[user_id_str]["group_credits"] = DAILY_GROUP_CREDITS
        user_data[user_id_str]["last_daily_credits"] = today
        save_data(user_data, USER_DATA_FILE)
    
    rc_number = parts[1]
    await perform_rc_mobile_lookup(rc_number, user.id, message.chat.id, message.chat.type, message.message_id)

# Add similar channel checks for other group commands...

@dp.message(Command("upi"))
async def cmd_upi_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /upi <upi_id>", parse_mode="Markdown")
        return
    await perform_upi_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("gst"))
async def cmd_gst_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /gst <gstin>", parse_mode="Markdown")
        return
    await perform_gst_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("pan"))
async def cmd_pan_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /pan <pan_number>", parse_mode="Markdown")
        return
    await perform_pan_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("pangst"))
async def cmd_pan_gst_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /pangst <pan_number>", parse_mode="Markdown")
        return
    await perform_pan_gst_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("imei"))
async def cmd_imei_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /imei <imei_number>", parse_mode="Markdown")
        return
    await perform_imei_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("pincode"))
async def cmd_pincode_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /pincode <pincode>", parse_mode="Markdown")
        return
    await perform_pincode_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("freefire"))
async def cmd_freefire_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /freefire <uid>", parse_mode="Markdown")
        return
    await perform_freefire_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("cnic"))
async def cmd_cnic_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /cnic <cnic_number>", parse_mode="Markdown")
        return
    await perform_cnic_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("vehiclebasic"))
async def cmd_vehicle_basic_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /vehiclebasic <rc_number>", parse_mode="Markdown")
        return
    await perform_vehicle_basic_lookup(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("smsbomber"))
async def cmd_sms_bomber_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /smsbomber <phone_number>", parse_mode="Markdown")
        return
    await perform_sms_bomber_action(parts[1], user.id, message.chat.id, message.chat.type, message.message_id)

# Other group commands with channel check...

@dp.message(Command("aadhaar"))
async def cmd_aadhaar_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /aadhaar <aadhaar_number>", parse_mode="Markdown")
        return
    aadhaar_number = parts[1]
    await perform_aadhaar_lookup(aadhaar_number, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("family"))
async def cmd_family_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /family <aadhaar_number>", parse_mode="Markdown")
        return
    aadhaar_number = parts[1]
    await perform_family_lookup(aadhaar_number, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("vehicle"))
async def cmd_vehicle_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /vehicle <rc_number>", parse_mode="Markdown")
        return
    rc_number = parts[1]
    await perform_vehicle_lookup(rc_number, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("ifsc"))
async def cmd_ifsc_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /ifsc <ifsc_code>", parse_mode="Markdown")
        return
    ifsc_code = parts[1]
    await perform_ifsc_lookup(ifsc_code, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("ip"))
async def cmd_ip_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /ip <ip_address>", parse_mode="Markdown")
        return
    ip_address = parts[1]
    await perform_ip_lookup(ip_address, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("tgid"))
async def cmd_tgid_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /tgid <user_id>", parse_mode="Markdown")
        return
    user_input = parts[1]
    await perform_tg_lookup(user_input, user.id, message.chat.id, message.chat.type, message.message_id)

@dp.message(Command("pakfamily"))
async def cmd_pakfamily_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    if await is_banned(user.id): 
        return
    
    if not await check_channel_membership_for_group(user.id, message.chat.id, message.message_id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: /pakfamily <cnic>", parse_mode="Markdown")
        return
    cnic = parts[1]
    await perform_pak_family_lookup(cnic, user.id, message.chat.id, message.chat.type, message.message_id)

# --- Group utility commands ---

@dp.message(Command("credits"))
async def cmd_credits_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    user_data = load_data(USER_DATA_FILE)
    
    user_id_str = str(user.id)
    if user_id_str not in user_data:
        credits = 0
        group_credits = 0
    else:
        credits = user_data[user_id_str].get('credits', 0)
        group_credits = user_data[user_id_str].get('group_credits', 0)
    
    referral_count = get_referral_count(user.id)

    if user.id in ADMIN_IDS:
        credit_text = "👑 As an admin, you have unlimited credits."
    elif await is_premium(user.id):
        user_info = user_data.get(str(user.id), {})
        if "premium_until" in user_info:
            premium_until = datetime.fromisoformat(user_info["premium_until"])
            time_left = premium_until - datetime.now()
            hours_left = int(time_left.total_seconds() / 3600)
            credit_text = f"⭐ Premium user with {hours_left} hours remaining. Unlimited searches!"
        else:
            credit_text = "⭐ Premium user with unlimited searches."
    else:
        credit_text = f"💰 Private Credits: {credits}"
        if group_credits > 0:
            credit_text += f"\n🎯 Daily RC Mobile Credits: {group_credits}"

    if referral_count > 0:
        credit_text += f"\n📊 Your referrals: {referral_count}"

    await message.reply(credit_text)

@dp.message(Command("referral"))
async def cmd_referral_group(message: Message):
    if message.chat.type not in ["group", "supergroup"]: 
        return
    user = message.from_user
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={user.id}"
    current_ref_count = get_referral_count(user.id)

    message_text = (
        f"🔗 <b>Referral System</b>\n\n"
        f"<b>Your Referral Link:</b>\n<code>{referral_link}</code>\n\n"
        f"<b>Current Stats:</b>\n"
        f"📊 Total Referrals: <b>{current_ref_count}</b>\n\n"
        f"<b>🎁 Rewards:</b>\n"
        f"✅ Each referral: <b>{REFERRAL_CREDITS} credits</b>\n\n"
        f"<b>You'll get instant notifications</b> when someone joins using your link!"
    )
    await message.reply(message_text, parse_mode="HTML")

# --- Callback query handler ---

@dp.callback_query(F.data == "verify_join")
async def callback_verify_join(callback: CallbackQuery):
    user = callback.from_user
    if await is_subscribed(user.id):
        try:
            await callback.message.delete()
        except:
            pass

        user_id_str = str(user.id)
        user_data = load_data(USER_DATA_FILE)

        base_caption = (
            "I am your advanced OSINT bot. Here's what you can do:\n\n"
            "🔍 <b>Lookups:</b> Phone (🇮🇳/🇵🇰), Aadhaar, Vehicle, IP, Bank IFSC, Telegram ID, PAN, GST, UPI, and Pakistan Family/CNIC info.\n\n"
            "💰 <b>Credit System:</b> You start with free credits. Each search costs one credit (RC Mobile costs 2 credits).\n\n"
            "🔗 <b>Referrals:</b> Share your link to earn 2 credits for each successful referral!"
        )
        final_caption = ""

        if user_id_str not in user_data:
            user_data[user_id_str] = {
                "credits": INITIAL_CREDITS,
                "referred_by": None,
                "redeemed_codes": [],
                "last_redeem_timestamp": 0,
                "referral_count": 0,
                "last_daily_credits": None,
                "group_credits": 0
            }
            final_caption = (f"<b>🎉 Welcome, {user.first_name}!</b>\n\n"
                             f"You have <b>{INITIAL_CREDITS} free credits</b> to get started.\n\n{base_caption}")
            save_data(user_data, USER_DATA_FILE)
            log_user_action(user.id, "Joined", "Verified channels")
            await log_new_user_to_channel(user)
        else:
            final_caption = f"<b>👋 Welcome back, {user.first_name}!</b>\n\n{base_caption}"

        try:
            await callback.message.answer_photo(
                photo=START_IMAGE_URL,
                caption=final_caption,
                reply_markup=get_main_keyboard(user.id),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send welcome photo on verify: {e}. Falling back to text.")
            await callback.message.answer(
                text=final_caption,
                reply_markup=get_main_keyboard(user.id),
                parse_mode="HTML"
            )

    else:
        await callback.answer("❌ You haven't joined all channels yet.", show_alert=True)

@dp.callback_query(F.data == "check_credit")
async def callback_check_credit(callback: CallbackQuery):
    user = callback.from_user
    user_data = load_data(USER_DATA_FILE)
    user_id_str = str(user.id)
    
    if user_id_str not in user_data:
        credits = 0
        group_credits = 0
    else:
        credits = user_data[user_id_str].get('credits', 0)
        group_credits = user_data[user_id_str].get('group_credits', 0)
    
    referral_count = get_referral_count(user.id)

    if user.id in ADMIN_IDS:
        credit_text = "👑 As an admin, you have unlimited credits."
    elif await is_premium(user.id):
        user_info = user_data.get(str(user.id), {})
        if "premium_until" in user_info:
            premium_until = datetime.fromisoformat(user_info["premium_until"])
            time_left = premium_until - datetime.now()
            hours_left = int(time_left.total_seconds() / 3600)
            credit_text = f"⭐ Premium user with {hours_left} hours remaining. Unlimited searches!"
        else:
            credit_text = "⭐ Premium user with unlimited searches."
    else:
        credit_text = f"💰 You have {credits} credits."
        if group_credits > 0:
            credit_text += f"\n🎯 Daily RC Mobile Credits: {group_credits}"

    if referral_count > 0:
        credit_text += f"\n📊 Your referrals: {referral_count}"

    await callback.message.answer(credit_text)
    await callback.answer()

@dp.callback_query(F.data == "get_referral")
async def callback_get_referral(callback: CallbackQuery):
    user = callback.from_user
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={user.id}"
    current_ref_count = get_referral_count(user.id)

    message_text = (
        f"🔗 <b>Referral System</b>\n\n"
        f"<b>Your Referral Link:</b>\n<code>{referral_link}</code>\n\n"
        f"<b>Current Stats:</b>\n"
        f"📊 Total Referrals: <b>{current_ref_count}</b>\n\n"
        f"<b>🎁 Rewards:</b>\n"
        f"✅ Each referral: <b>{REFERRAL_CREDITS} credits</b>\n\n"
        f"<b>You'll get instant notifications</b> when someone joins using your link!"
    )
    await callback.message.answer(message_text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "support")
async def callback_support(callback: CallbackQuery):
    support_text = "Click the button below to contact the admin directly for any help or queries."
    keyboard = [[InlineKeyboardButton(text="Contact Admin 👨‍💻", url=f"tg://user?id={SUPPORT_USER_ID}")]]
    await callback.message.answer(support_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@dp.callback_query(F.data == "group_commands")
async def callback_group_commands(callback: CallbackQuery):
    commands_text = """
Available Group Commands:

🔍 /num <number> - Indian number lookup
🔍 /paknum <number> - Pakistani number lookup (10-digit)
🔍 /aadhaar <id> - Aadhaar details
🔍 /family <aadhaar> - Family information
🔍 /vehicle <rc> - Vehicle information (Advanced)
🔍 /vehiclebasic <rc> - Vehicle information (Basic)
🔍 /ifsc <code> - Bank IFSC details
🔍 /ip <address> - IP address lookup
🔍 /tgid <id> - Telegram user lookup
🔍 /pakfamily <cnic> - Pakistani family info
🔍 /cnic <cnic> - Pakistani CNIC basic lookup
🔍 /upi <id> - UPI ID lookup
🔍 /gst <gstin> - GSTIN lookup
🔍 /pan <pan> - PAN card lookup
🔍 /pangst <pan> - PAN to GST lookup
🔍 /rcmobile <rc> - RC owner mobile lookup (Daily 2 credits in groups)
🔍 /imei <imei> - IMEI lookup
🔍 /pincode <pincode> - Pincode lookup
🔍 /freefire <uid> - Free Fire UID lookup
💣 /smsbomber <num> - SMS Bomber (Deducts credits, is placeholder)

💰 /credits - Check your credits
🔗 /referral - Get referral link

Note: Group searches are unlimited! Only RC Mobile has daily limits (2 credits/day).
"""
    await callback.message.answer(commands_text, parse_mode="Markdown")
    await callback.answer()

# --- Search handlers ---

@dp.callback_query(F.data.in_([
    'search_phone', 'search_pak_phone', 'search_aadhaar', 'search_family',
    'search_vehicle', 'search_ifsc', 'search_ip', 'search_tg', 'search_pak_family',
    'redeem_code', 'search_upi', 'search_gst', 'search_pan', 'search_pan_gst',
    'search_rc_mobile', 'search_imei', 'search_pincode', 'search_freefire',
    'search_cnic', 'search_vehicle_basic', 'search_sms_bomber'
]))
async def handle_search_callback(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user

    if not await is_subscribed(user.id):
        await callback.answer("You must join all channels first.", show_alert=True)
        await send_join_message(callback.message.chat.id)
        return

    actions = {
        'search_phone': (UserStates.awaiting_phone, "➡️ Send me the 10-digit Indian mobile number."),
        'search_pak_phone': (UserStates.awaiting_pak_phone, "➡️ Send me the 10-digit Pakistani number."),
        'search_aadhaar': (UserStates.awaiting_aadhaar, "➡️ Send me the 12-digit Aadhaar number."),
        'search_family': (UserStates.awaiting_family, "➡️ Send me the 12-digit Aadhaar number to fetch family information."),
        'search_vehicle': (UserStates.awaiting_vehicle, "➡️ Send me the vehicle RC number (e.g., DL12AB1234) for Advanced Lookup."),
        'search_ifsc': (UserStates.awaiting_ifsc, "➡️ Send me the bank IFSC code."),
        'search_ip': (UserStates.awaiting_ip, "➡️ Send me the IP address you want to look up."),
        'search_tg': (UserStates.awaiting_tg, "➡️ Send me the Telegram User ID (e.g., 7098436876)."),
        'search_pak_family': (UserStates.awaiting_pak_family, "➡️ Send me the Pakistani CNIC number (e.g., 15601-6938749-3)."),
        'redeem_code': (UserStates.awaiting_redeem_code, "🎁 Send me your redeem code."),
        'search_upi': (UserStates.awaiting_upi, "➡️ Send me the UPI ID (e.g., user@bank)."),
        'search_gst': (UserStates.awaiting_gst, "➡️ Send me the 15-char GSTIN."),
        'search_pan': (UserStates.awaiting_pan, "➡️ Send me the 10-char PAN number."),
        'search_pan_gst': (UserStates.awaiting_pan_gst, "➡️ Send me the 10-char PAN to find linked GSTINs."),
        'search_rc_mobile': (UserStates.awaiting_rc_mobile, f"➡️ Send me the Vehicle RC Number to find the owner's mobile number. (This costs **{RC_MOBILE_COST} credits**)."),
        'search_imei': (UserStates.awaiting_imei, "➡️ Send me the 15-digit IMEI number."),
        'search_pincode': (UserStates.awaiting_pincode, "➡️ Send me the 6-digit Pincode."),
        'search_freefire': (UserStates.awaiting_freefire, "➡️ Send me the Free Fire UID."),
        'search_cnic': (UserStates.awaiting_cnic, "➡️ Send me the 13-digit Pakistani CNIC number for **Basic** Lookup."),
        'search_vehicle_basic': (UserStates.awaiting_vehicle_basic, "➡️ Send me the vehicle RC number (e.g., DL12AB1234) for **Basic** Lookup."),
        'search_sms_bomber': (UserStates.awaiting_sms_bomber, f"⚠️ **WARNING**: This costs **{SEARCH_COST} credit**. Send the 10-digit mobile number for the SMS Bomber. (Service is a placeholder)"),
    }

    if callback.data in actions:
        state_class, message_text = actions[callback.data]
        await state.set_state(state_class)
        await callback.message.answer(message_text, parse_mode='HTML')
        await callback.answer()

# --- Lookup functions ---

async def generic_lookup(term: str, user_id: int, chat_id: int, api_endpoint: str, action_name: str, display_name: str, chat_type: str, reply_to_message_id: int = None, input_validator=None, custom_cost: bool = False):
    term = term.strip().upper() if action_name in ['GST Search', 'PAN Search', 'RC Mobile Search', 'Vehicle Basic Search'] else term.strip()

    if input_validator and not input_validator(term):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, f"❌ <b>Invalid Input:</b> {display_name} validation failed.", parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, f"❌ <b>Invalid Input:</b> {display_name} validation failed.", parse_mode="HTML")
        return

    log_user_action(user_id, action_name, term)
    
    cost_to_deduct = RC_MOBILE_COST if custom_cost and action_name == "RC Mobile Search" else SEARCH_COST
    
    # Send "Searching..." message
    if chat_type in ["group", "supergroup"] and reply_to_message_id:
        sent_message = await bot.send_message(chat_id, f"🔍 Searching for {display_name} details...", reply_to_message_id=reply_to_message_id)
    else:
        sent_message = await bot.send_message(chat_id, f"🔍 Searching for {display_name} details...")

    try:
        if not await deduct_credits_with_override(user_id, chat_type, action_name):
            if action_name == "RC Mobile Search" and chat_type in ["group", "supergroup"]:
                await sent_message.edit_text(f"❌ You've used all your daily RC Mobile credits. You get {DAILY_GROUP_CREDITS} credits per day for RC Mobile in groups.")
            else:
                await sent_message.edit_text(f"❌ You don't have enough credits. Each search costs {cost_to_deduct} credit(s).")
            return
        
        # Format API endpoint
        final_api_endpoint = api_endpoint.format(term=term)
        logger.info(f"Calling API: {final_api_endpoint}")
        
        # API Call with longer timeout
        response = requests.get(final_api_endpoint, timeout=20)
        response.raise_for_status()
        
        # Check if response is HTML (error page)
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            logger.warning(f"HTML response received from API: {final_api_endpoint}")
            await sent_message.edit_text(f"🔌 The {display_name} API service returned an HTML page (might be down or blocked).")
            return
        
        # Try to parse as JSON
        try:
            data = response.json()
            
            # Check for different error formats
            if not data or isinstance(data, str) and 'error' in data.lower():
                await sent_message.edit_text(f"🤷 No details found for {display_name}: <code>{html.escape(term)}</code>." + get_info_footer(user_id, chat_type), parse_mode="HTML")
                return
            
            # Check for empty or error responses
            if isinstance(data, dict):
                error_msg = data.get('error') or data.get('msg') or data.get('message') or data.get('Error')
                if error_msg or data.get('status') == False or data.get('success') == False:
                    await sent_message.edit_text(f"🤷 No details found for {display_name}: <code>{html.escape(term)}</code>." + get_info_footer(user_id, chat_type), parse_mode="HTML")
                    return
                    
                # Check if data is actually empty
                if len(data) == 0 or (len(data) == 1 and any(key in data for key in ['status', 'message', 'error'])):
                    await sent_message.edit_text(f"🤷 No details found for {display_name}: <code>{html.escape(term)}</code>." + get_info_footer(user_id, chat_type), parse_mode="HTML")
                    return
                    
        except json.JSONDecodeError:
            # If not JSON, check if it's a plain text error
            text_response = response.text[:200]
            if 'error' in text_response.lower() or 'not found' in text_response.lower():
                await sent_message.edit_text(f"🤷 No details found for {display_name}: <code>{html.escape(term)}</code>." + get_info_footer(user_id, chat_type), parse_mode="HTML")
                return
            else:
                # If it's valid text response, use it
                data = {"response": text_response}
        
        # Format the response
        if isinstance(data, (dict, list)):
            formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            formatted_data = str(data)
                
        if len(formatted_data) > 4000:
            filename = f"{action_name.replace(' ', '_').lower()}_{term.replace('-', '')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_data)
                
            caption = f"🔍 <b>{display_name} Details for {term}</b>\n\nResponse too long, sent as file." + get_info_footer(user_id, chat_type)
            
            if chat_type in ["group", "supergroup"]:
                await bot.send_document(
                    chat_id=chat_id,
                    document=InputFile(filename),
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=get_group_footer_keyboard()
                )
            else:
                await bot.send_document(
                    chat_id=chat_id,
                    document=InputFile(filename),
                    caption=caption,
                    parse_mode="HTML"
                )
            os.remove(filename)
        else:
            result_text = f"🔍 <b>{display_name} Details for <code>{html.escape(term)}</code></b>\n\n<pre>{html.escape(formatted_data)}</pre>"
            result_text += get_info_footer(user_id, chat_type)
            
            if chat_type in ["group", "supergroup"]:
                await sent_message.edit_text(result_text, parse_mode="HTML", reply_markup=get_group_footer_keyboard())
            else:
                await sent_message.edit_text(result_text, parse_mode="HTML")

    except requests.exceptions.Timeout:
        logger.error(f"{action_name} API Timeout: {api_endpoint}")
        await sent_message.edit_text(f"⏰ The {display_name} search timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        logger.error(f"{action_name} Connection Error: {api_endpoint}")
        await sent_message.edit_text(f"🔌 The {display_name} service is unreachable. Please try again later.")
    except requests.exceptions.RequestException as e:
        logger.error(f"{action_name} API Error: {e}")
        await sent_message.edit_text(f"🔌 The {display_name} search service is having issues. Please try again later.")
    except Exception as e:
        logger.error(f"{action_name} General Error: {e}")
        await sent_message.edit_text(f"🔌 An unexpected error occurred during {display_name} search. Error: {str(e)}")

# Input Validators
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

# Lookup functions
async def perform_upi_lookup(upi: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(upi, user_id, chat_id, UPI_API_ENDPOINT, "UPI Search", "UPI ID", chat_type, reply_to_message_id, lambda x: 3 <= len(x) <= 50)

async def perform_gst_lookup(gst: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(gst, user_id, chat_id, GST_API_ENDPOINT, "GST Search", "GSTIN", chat_type, reply_to_message_id, is_valid_gstin)

async def perform_pan_lookup(pan: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(pan, user_id, chat_id, PAN_API_ENDPOINT, "PAN Search", "PAN Card", chat_type, reply_to_message_id, is_valid_pan)

async def perform_pan_gst_lookup(pan: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(pan, user_id, chat_id, PAN_GST_API_ENDPOINT, "PAN-GST Search", "PAN to GSTIN", chat_type, reply_to_message_id, is_valid_pan)

async def perform_rc_mobile_lookup(rc_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(rc_number, user_id, chat_id, RC_MOBILE_API_ENDPOINT, "RC Mobile Search", "RC Owner Mobile", chat_type, reply_to_message_id, lambda x: 4 <= len(x) <= 15, custom_cost=True)

async def perform_imei_lookup(imei: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(imei, user_id, chat_id, IMEI_API_ENDPOINT, "IMEI Search", "IMEI", chat_type, reply_to_message_id, is_valid_imei)

async def perform_pincode_lookup(pincode: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(pincode, user_id, chat_id, PINCODE_API_ENDPOINT, "Pincode Search", "Pincode", chat_type, reply_to_message_id, is_valid_pincode)

async def perform_freefire_lookup(uid: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(uid, user_id, chat_id, FREEFIRE_API_ENDPOINT, "Free Fire Search", "Free Fire UID", chat_type, reply_to_message_id, lambda x: x.isdigit() and 5 <= len(x) <= 15)

async def perform_cnic_lookup(cnic: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(cnic, user_id, chat_id, CNIC_API_ENDPOINT, "CNIC Search", "Pakistani CNIC Basic", chat_type, reply_to_message_id, is_valid_cnic)

async def perform_vehicle_basic_lookup(rc_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(rc_number, user_id, chat_id, VEHICLE_BASIC_API_ENDPOINT, "Vehicle Basic Search", "Vehicle RC Basic", chat_type, reply_to_message_id, lambda x: 4 <= len(x) <= 15)

async def perform_sms_bomber_action(phone_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    phone_number = phone_number.strip()
    if not (phone_number.isdigit() and len(phone_number) == 10):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit mobile number.", parse_mode='HTML', reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit mobile number.", parse_mode='HTML')
        return

    log_user_action(user_id, "SMS Bomber Action", phone_number)
    
    if chat_type in ["group", "supergroup"] and reply_to_message_id:
        sent_message = await bot.send_message(chat_id, "💣 Initializing SMS Bomber on target...", reply_to_message_id=reply_to_message_id)
    else:
        sent_message = await bot.send_message(chat_id, "💣 Initializing SMS Bomber on target...")

    try:
        if not await deduct_credits(user_id, chat_type):
            await sent_message.edit_text(f"❌ You don't have enough credits. Each search costs {SEARCH_COST} credit.")
            return

        response = requests.get(SMS_BOMBER_API_ENDPOINT.format(term=phone_number), timeout=15)
        response.raise_for_status()
        
        data = response.json()
        result_text = f"💣 <b>SMS Bomber Initiated!</b>\n\nTarget: <code>{html.escape(phone_number)}</code>\n\n"
        result_text += f"API Response: <pre>{html.escape(json.dumps(data, indent=2, ensure_ascii=False))}</pre>"
        result_text += get_info_footer(user_id, chat_type)
        
        if chat_type in ["group", "supergroup"]:
            await sent_message.edit_text(result_text, parse_mode="HTML", reply_markup=get_group_footer_keyboard())
        else:
            await sent_message.edit_text(result_text, parse_mode="HTML")

    except requests.exceptions.RequestException as e:
        logger.error(f"SMS Bomber API Error: {e}")
        await sent_message.edit_text("❌ The SMS Bomber service is currently unavailable.")
    except Exception as e:
        logger.error(f"SMS Bomber General Error: {e}")
        await sent_message.edit_text("❌ An unexpected error occurred during SMS Bomber initiation.")

# Existing Lookup Functions
async def perform_phone_lookup(phone_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    if not (phone_number.isdigit() and (len(phone_number) == 10 or (phone_number.startswith("91") and len(phone_number) == 12))):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit Indian mobile number.", parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit Indian mobile number.", parse_mode="HTML")
        return
    phone_number = phone_number[-10:]
    await generic_lookup(phone_number, user_id, chat_id, PHONE_API_ENDPOINT, "Phone Search", "Indian Phone Number", chat_type, reply_to_message_id, lambda x: x.isdigit() and len(x) == 10)

async def perform_pak_phone_lookup(phone_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    # Fixed for 10-digit Pakistani numbers
    if not (phone_number.isdigit() and len(phone_number) == 10):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit Pakistani number.", parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 10-digit Pakistani number.", parse_mode="HTML")
        return
    await generic_lookup(phone_number, user_id, chat_id, PAK_PHONE_API_ENDPOINT, "Pak Number Search", "Pakistani Phone Number", chat_type, reply_to_message_id, is_valid_pak_num)

async def perform_aadhaar_lookup(aadhaar_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    if not (aadhaar_number.isdigit() and len(aadhaar_number) == 12):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML")
        return
    await generic_lookup(aadhaar_number, user_id, chat_id, AADHAAR_API_ENDPOINT, "Aadhaar Search", "Aadhaar", chat_type, reply_to_message_id, lambda x: x.isdigit() and len(x) == 12)

async def perform_family_lookup(aadhaar_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    if not (aadhaar_number.isdigit() and len(aadhaar_number) == 12):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 12-digit Aadhaar number.", parse_mode="HTML")
        return
    await generic_lookup(aadhaar_number, user_id, chat_id, FAMILY_INFO_API_ENDPOINT, "Family Info Search", "Family Information (by Aadhaar)", chat_type, reply_to_message_id, lambda x: x.isdigit() and len(x) == 12)

async def perform_vehicle_lookup(rc_number: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(rc_number, user_id, chat_id, VEHICLE_API_ENDPOINT, "Vehicle Advanced Search", "Vehicle RC Advanced", chat_type, reply_to_message_id, lambda x: 4 <= len(x) <= 15)

async def perform_ifsc_lookup(ifsc_code: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    ifsc_code = ifsc_code.strip().upper()
    await generic_lookup(ifsc_code, user_id, chat_id, IFSC_API_ENDPOINT, "IFSC Search", "Bank IFSC", chat_type, reply_to_message_id, lambda x: len(x) == 11 and x.isalnum())

async def perform_ip_lookup(ip_address: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(ip_address, user_id, chat_id, IP_API_ENDPOINT, "IP Search", "IP Address", chat_type, reply_to_message_id, lambda x: 7 <= len(x) <= 15)

async def perform_tg_lookup(user_input: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    await generic_lookup(user_input, user_id, chat_id, TG_INFO_API_ENDPOINT, "TG ID Search", "Telegram User ID", chat_type, reply_to_message_id, lambda x: len(x) > 0)

async def perform_pak_family_lookup(cnic: str, user_id: int, chat_id: int, chat_type: str = "private", reply_to_message_id: int = None):
    if not is_valid_cnic(cnic):
        if chat_type in ["group", "supergroup"] and reply_to_message_id:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 13-digit Pakistani CNIC number (dashes optional).", parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            await bot.send_message(chat_id, "❌ <b>Invalid Input:</b> Please send a valid 13-digit Pakistani CNIC number (dashes optional).", parse_mode="HTML")
        return
    await generic_lookup(cnic, user_id, chat_id, PAK_FAMILY_API_ENDPOINT, "Pak Family Search", "Pakistani Family Information", chat_type, reply_to_message_id, is_valid_cnic)

async def process_redeem_code(code_text: str, user_id: int, chat_id: int):
    user_id_str = str(user_id)
    user_data = load_data(USER_DATA_FILE)

    if user_id_str not in user_data:
        await bot.send_message(chat_id, "Please /start the bot first to create an account.")
        return

    last_redeem_time = user_data[user_id_str].get("last_redeem_timestamp", 0)
    current_time = time.time()

    if current_time - last_redeem_time < REDEEM_COOLDOWN_SECONDS:
        time_left = int((REDEEM_COOLDOWN_SECONDS - (current_time - last_redeem_time)) / 60)
        await bot.send_message(chat_id, f"⏳ You are on a cooldown. Please try again in about {time_left+1} minutes.")
        return

    code = code_text.strip().upper()
    redeem_codes = load_data(REDEEM_CODES_FILE)
    if code not in redeem_codes:
        await bot.send_message(chat_id, "❌ Invalid code.")
        return
    if code in user_data[user_id_str].get("redeemed_codes", []):
        await bot.send_message(chat_id, "⚠️ You have already used this code.")
        return
    if redeem_codes[code]["uses_left"] <= 0:
        await bot.send_message(chat_id, "⌛ This code has no uses left.")
        return

    credits_to_add = redeem_codes[code]["credits"]
    user_data[user_id_str]["credits"] += credits_to_add
    if "redeemed_codes" not in user_data[user_id_str]:
        user_data[user_id_str]["redeemed_codes"] = []
    user_data[user_id_str]["redeemed_codes"].append(code)
    user_data[user_id_str]["last_redeem_timestamp"] = current_time
    redeem_codes[code]["uses_left"] -= 1

    save_data(user_data, USER_DATA_FILE)
    save_data(redeem_codes, REDEEM_CODES_FILE)
    log_user_action(user_id, "Redeemed Code", f"Code: {code}, Credits: {credits_to_add}")
    await bot.send_message(chat_id, f"✅ Success! <b>{credits_to_add} credits</b> have been added to your account.", parse_mode="HTML")

# Message handlers for search states
@dp.message(UserStates.awaiting_phone)
async def handle_phone_search(message: Message, state: FSMContext):
    await perform_phone_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_pak_phone)
async def handle_pak_phone_search(message: Message, state: FSMContext):
    await perform_pak_phone_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_aadhaar)
async def handle_aadhaar_search(message: Message, state: FSMContext):
    await perform_aadhaar_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_family)
async def handle_family_search(message: Message, state: FSMContext):
    await perform_family_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_vehicle)
async def handle_vehicle_search(message: Message, state: FSMContext):
    await perform_vehicle_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_ifsc)
async def handle_ifsc_search(message: Message, state: FSMContext):
    await perform_ifsc_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_ip)
async def handle_ip_search(message: Message, state: FSMContext):
    await perform_ip_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_tg)
async def handle_tg_search(message: Message, state: FSMContext):
    await perform_tg_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_pak_family)
async def handle_pak_family_search(message: Message, state: FSMContext):
    await perform_pak_family_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_redeem_code)
async def handle_redeem_code(message: Message, state: FSMContext):
    await process_redeem_code(message.text, message.from_user.id, message.chat.id)
    await state.clear()

@dp.message(UserStates.awaiting_upi)
async def handle_upi_search(message: Message, state: FSMContext):
    await perform_upi_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_gst)
async def handle_gst_search(message: Message, state: FSMContext):
    await perform_gst_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_pan)
async def handle_pan_search(message: Message, state: FSMContext):
    await perform_pan_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_pan_gst)
async def handle_pan_gst_search(message: Message, state: FSMContext):
    await perform_pan_gst_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_rc_mobile)
async def handle_rc_mobile_search(message: Message, state: FSMContext):
    await perform_rc_mobile_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_imei)
async def handle_imei_search(message: Message, state: FSMContext):
    await perform_imei_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_pincode)
async def handle_pincode_search(message: Message, state: FSMContext):
    await perform_pincode_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_freefire)
async def handle_freefire_search(message: Message, state: FSMContext):
    await perform_freefire_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_cnic)
async def handle_cnic_search(message: Message, state: FSMContext):
    await perform_cnic_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_vehicle_basic)
async def handle_vehicle_basic_search(message: Message, state: FSMContext):
    await perform_vehicle_basic_lookup(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

@dp.message(UserStates.awaiting_sms_bomber)
async def handle_sms_bomber_action(message: Message, state: FSMContext):
    await perform_sms_bomber_action(message.text, message.from_user.id, message.chat.id, message.chat.type)
    await state.clear()

# Admin panel functions
def get_admin_keyboard():
    free_mode = is_free_mode_active()
    free_mode_text = "Free Mode (ON ✅)" if free_mode else "Free Mode (OFF ❌)"

    keyboard = [
        [
            InlineKeyboardButton(text="➕ Add Credits", callback_data='admin_add_credits'),
            InlineKeyboardButton(text="➖ Remove Credits", callback_data='admin_remove_credits')
        ],
        [
            InlineKeyboardButton(text="➕ Add Premium", callback_data='admin_add_premium'),
            InlineKeyboardButton(text="➖ Remove Premium", callback_data='admin_remove_premium'),
        ],
        [
            InlineKeyboardButton(text="👥 All Users", callback_data='admin_view_all_users'),
            InlineKeyboardButton(text="📜 User History", callback_data='admin_user_history')
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data='admin_broadcast'),
            InlineKeyboardButton(text="⭐ Premium List", callback_data='admin_view_premium')
        ],
        [
            InlineKeyboardButton(text="🚫 Block User", callback_data='admin_ban_user'),
            InlineKeyboardButton(text="✅ Unblock User", callback_data='admin_unban_user')
        ],
        [
            InlineKeyboardButton(text="📋 Blocked List", callback_data='admin_view_blocked'),
            InlineKeyboardButton(text="📊 Bot Stats", callback_data='admin_stats')
        ],
        [
            InlineKeyboardButton(text="🎫 Generate Code", callback_data='admin_gen_code'),
            InlineKeyboardButton(text=free_mode_text, callback_data='admin_toggle_freemode')
        ],
        [
            InlineKeyboardButton(text="📈 Referral Stats", callback_data='admin_referral_stats')
        ],
        [
            InlineKeyboardButton(text="🏠 Main Menu", callback_data='back_to_main')
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.callback_query(F.data == "admin_panel")
async def callback_admin_panel(callback: CallbackQuery):
    user = callback.from_user
    if user.id not in ADMIN_IDS:
        await callback.answer("❌ Admin access required!", show_alert=True)
        return

    # Send new message instead of editing
    await callback.message.answer(
        "👑 <b>Welcome to the Admin Panel</b>\n\nSelect an option to manage the bot.",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
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
            reply_markup=get_main_keyboard(user.id),
            parse_mode="HTML"
        )
        await callback.message.delete()
    except Exception as e:
        logger.error(f"Failed to send menu photo on back_to_main: {e}. Falling back to text.")
        await callback.message.answer(welcome_text, reply_markup=get_main_keyboard(user.id), parse_mode="HTML")
    
    await callback.answer()

# Admin callback handlers
@dp.callback_query(F.data.startswith("admin_"))
async def handle_admin_callback(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    if user.id not in ADMIN_IDS:
        await callback.answer("❌ Admin access required!", show_alert=True)
        return

    data = callback.data

    if data == 'admin_stats':
        user_data = load_data(USER_DATA_FILE)
        premium_users = load_data(PREMIUM_USERS_FILE)
        banned_users = load_data(BANNED_USERS_FILE)
        user_history = load_data(USER_HISTORY_FILE)
        redeem_codes = load_data(REDEEM_CODES_FILE)

        today_str = datetime.now().strftime("%Y-%m-%d")    
        searches_today = 0    
        total_searches = 0    
        active_users_today = set()    
        active_users_week = set()    
        search_type_counts = defaultdict(int)    

        week_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)    
        
        for user_id_str, actions in user_history.items():    
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
                    
        active_codes = sum(1 for code in redeem_codes.values() if code.get('uses_left', 0) > 0)    
        total_credits_in_codes = sum(code.get('credits', 0) * code.get('uses_left', 0) for code in redeem_codes.values())    

        most_common_search = max(search_type_counts, key=search_type_counts.get) if search_type_counts else "None"    

        stats_message = (    
            f"📊 <b>Bot Statistics</b>\n\n"    
            f"<b>Overall:</b>\n"    
            f"👥 Total Users: <b>{len(user_data)}</b>\n"    
            f"⭐ Permanent Premium Users: <b>{len(premium_users)}</b>\n"    
            f"🚫 Banned Users: <b>{len(banned_users)}</b>\n"    
            f"🎫 Active Codes: <b>{active_codes}</b>\n\n"    
                
            f"<b>Activity (Today):</b>\n"    
            f"📈 Searches Today: <b>{searches_today}</b>\n"    
            f"🏃‍♂️ Active Users Today: <b>{len(active_users_today)}</b>\n\n"    
                
            f"<b>Activity (All Time):</b>\n"    
            f"💹 Total Searches: <b>{total_searches}</b>\n"    
            f"🏃‍♂️ Active Users (Week): <b>{len(active_users_week)}</b>\n"    
            f"🔝 Top Search: <b>{most_common_search}</b>\n\n"    
                
            f"<b>Credits:</b>\n"    
            f"💰 Total Credits in System: <b>{sum(user.get('credits', 0) for user in user_data.values())}</b>\n"    
            f"🎁 Available in Codes: <b>{total_credits_in_codes}</b>"    
        )    
        await callback.message.answer(stats_message, reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == 'admin_toggle_freemode':
        new_status = not is_free_mode_active()
        set_free_mode(new_status)
        await callback.answer(f"✅ Free Mode has been {'ENABLED' if new_status else 'DISABLED'}.", show_alert=True)
        await callback.message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

    elif data == 'admin_referral_stats':
        user_data = load_data(USER_DATA_FILE)

        total_referrals = sum(user.get('referral_count', 0) for user in user_data.values())    
        users_with_referrals = sum(1 for user in user_data.values() if user.get('referral_count', 0) > 0)    
        top_referrers = sorted([(uid, user.get('referral_count', 0)) for uid, user in user_data.items()],     
                              key=lambda x: x[1], reverse=True)[:10]    
        
        stats_message = (    
            f"📈 <b>Referral Statistics</b>\n\n"    
            f"<b>Overall:</b>\n"    
            f"🔗 Total Referrals: <b>{total_referrals}</b>\n"    
            f"👥 Users with Referrals: <b>{users_with_referrals}</b>\n\n"    
            f"<b>Top Referrers:</b>\n"    
        )    
        
        for i, (uid, count) in enumerate(top_referrers, 1):    
            stats_message += f"{i}. User {uid}: <b>{count}</b> referrals\n"    
        
        await callback.message.answer(stats_message, reply_markup=get_admin_keyboard(), parse_mode="HTML")

    elif data == 'admin_view_all_users':
        users = load_data(USER_DATA_FILE)
        if not users:
            await callback.answer("No users found.", show_alert=True)
            return

        user_list_text = "👥 **All Users**\n\n"    
        for uid, udata in users.items():    
            premium_users = load_data(PREMIUM_USERS_FILE)    
            premium_status = "⭐" if int(uid) in premium_users else ""    
            
            if "premium_until" in udata:    
                premium_until = datetime.fromisoformat(udata["premium_until"])    
                if datetime.now() < premium_until:    
                    time_left = premium_until - datetime.now()    
                    hours_left = int(time_left.total_seconds() / 3600)    
                    premium_status = f"⭐({hours_left}h)"    
                
            referral_count = udata.get('referral_count', 0)    
            ref_status = f"🔗{referral_count}" if referral_count > 0 else ""    
            
            user_list_text += f"`{uid}` - Credits: {udata.get('credits', 0)} {premium_status} {ref_status}\n"    
        
        if len(user_list_text) > 4000:    
            with open("all_users.txt", "w") as f:    
                f.write(user_list_text)    
            await bot.send_document(chat_id=callback.from_user.id, document=InputFile("all_users.txt"), caption="User list is too long.")    
            os.remove("all_users.txt")    
        else:    
            await callback.message.answer(user_list_text, reply_markup=get_admin_keyboard(), parse_mode='Markdown')

    elif data == 'admin_view_blocked':
        blocked = load_data(BANNED_USERS_FILE)
        if not blocked:
            await callback.answer("No blocked users.", show_alert=True)
            return

        text = "🚫 **Blocked Users**\n\n`" + '`\n`'.join(map(str, blocked)) + '`'    
        await callback.message.answer(text, reply_markup=get_admin_keyboard(), parse_mode='Markdown')

    elif data == 'admin_view_premium':
        premium = load_data(PREMIUM_USERS_FILE)
        user_data = load_data(USER_DATA_FILE)

        if not premium:    
            text = "⭐ **Premium Users**\n\nNo permanent premium users."    
        else:    
            text = "⭐ **Permanent Premium Users**\n\n`" + '`\n`'.join(map(str, premium)) + '`'    
        
        temp_premium = []    
        for uid, udata in user_data.items():    
            if "premium_until" in udata:    
                premium_until = datetime.fromisoformat(udata["premium_until"])    
                if datetime.now() < premium_until:    
                    time_left = premium_until - datetime.now()    
                    hours_left = int(time_left.total_seconds() / 3600)    
                    temp_premium.append(f"{uid} ({hours_left}h)")    
        
        if temp_premium:    
            text += f"\n\n🕒 **Temporary Premium Users**\n\n" + "\n".join(temp_premium)    
        
        await callback.message.answer(text, reply_markup=get_admin_keyboard(), parse_mode='Markdown')

    elif data == 'admin_gen_code':
        await state.set_state(AdminStates.awaiting_gen_code)
        await callback.message.answer("🎫 Send credits and uses separated by space (e.g., 100 5 for 100 credits with 5 uses)")

    else:
        prompts = {
            'admin_add_credits': (AdminStates.awaiting_add_credit, "➡️ Send the User ID and Amount, separated by a space (e.g., 12345678 100)."),
            'admin_remove_credits': (AdminStates.awaiting_remove_credit, "➡️ Send the User ID and Amount to remove (e.g., 12345678 50)."),
            'admin_add_premium': (AdminStates.awaiting_premium_add, "➡️ Send the User ID to make a premium member."),
            'admin_remove_premium': (AdminStates.awaiting_premium_remove, "➡️ Send the User ID to remove from premium."),
            'admin_user_history': (AdminStates.awaiting_history_id, "➡️ Send the User ID to view their history."),
            'admin_broadcast': (AdminStates.awaiting_broadcast, "➡️ Send the message you want to broadcast (supports HTML)."),
            'admin_ban_user': (AdminStates.awaiting_ban_id, "➡️ Send the User ID to ban."),
            'admin_unban_user': (AdminStates.awaiting_unban_id, "➡️ Send the User ID to unban."),
        }
        if data in prompts:
            state_class, message_text = prompts[data]
            await state.set_state(state_class)
            await callback.message.answer(message_text, parse_mode='Markdown')

    await callback.answer()

# Admin message handlers
@dp.message(AdminStates.awaiting_add_credit)
async def handle_admin_add_credit(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Invalid format")

        target_id, amount = int(parts[0]), int(parts[1])
        target_id_str = str(target_id)
        user_data = load_data(USER_DATA_FILE)

        if target_id_str not in user_data:
            user_data[target_id_str] = {
                "credits": 0,
                "referred_by": None,
                "redeemed_codes": [],
                "last_redeem_timestamp": 0,
                "referral_count": 0,
                "last_daily_credits": None,
                "group_credits": 0
            }
            
        user_data[target_id_str]['credits'] += amount
        save_data(user_data, USER_DATA_FILE)
        await message.answer(f"✅ Success! {amount} credits have been added to user `{target_id}`.", parse_mode='Markdown')
        log_user_action(message.from_user.id, "Admin Add Credits", f"User {target_id}: +{amount} credits")

    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: USER_ID AMOUNT")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_remove_credit)
async def handle_admin_remove_credit(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Invalid format")

        target_id, amount = int(parts[0]), int(parts[1])
        target_id_str = str(target_id)
        user_data = load_data(USER_DATA_FILE)

        if target_id_str not in user_data:
            await message.answer("❌ User not found.")
        else:
            user_data[target_id_str]['credits'] = max(0, user_data[target_id_str]['credits'] - amount)
            save_data(user_data, USER_DATA_FILE)
            await message.answer(f"✅ Success! {amount} credits have been removed from user `{target_id}`.", parse_mode='Markdown')
            log_user_action(message.from_user.id, "Admin Remove Credits", f"User {target_id}: -{amount} credits")

    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: USER_ID AMOUNT")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_premium_add)
async def handle_admin_premium_add(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        premium_users = load_data(PREMIUM_USERS_FILE)

        if target_id in premium_users:
            await message.answer(f"User {target_id} is already a premium member.", parse_mode='Markdown')
        else:
            premium_users.append(target_id)
            user_data = load_data(USER_DATA_FILE)
            if str(target_id) in user_data and "premium_until" in user_data[str(target_id)]:
                del user_data[str(target_id)]["premium_until"]
                save_data(user_data, USER_DATA_FILE)
            
            save_data(premium_users, PREMIUM_USERS_FILE)
            await message.answer(f"⭐ User {target_id} has been added to permanent premium.", parse_mode='Markdown')
            log_user_action(message.from_user.id, "Admin Add Premium", f"User {target_id}")

    except ValueError:
        await message.answer("❌ Invalid user ID.")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_premium_remove)
async def handle_admin_premium_remove(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        premium_users = load_data(PREMIUM_USERS_FILE)

        if target_id not in premium_users:
            await message.answer(f"User {target_id} is not a permanent premium member.", parse_mode='Markdown')
        else:
            premium_users.remove(target_id)
            save_data(premium_users, PREMIUM_USERS_FILE)
            await message.answer(f"✅ User {target_id} has been removed from permanent premium.", parse_mode='Markdown')
            log_user_action(message.from_user.id, "Admin Remove Premium", f"User {target_id}")

    except ValueError:
        await message.answer("❌ Invalid user ID.")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_broadcast)
async def handle_admin_broadcast(message: Message, state: FSMContext):
    user_ids = list(load_data(USER_DATA_FILE).keys())
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
    history = load_data(USER_HISTORY_FILE).get(target_id_str, [])

    if not history:
        await message.answer(f"No history found for user `{target_id_str}`.", parse_mode='Markdown')
    else:
        history_text = f"📜 History for User `{target_id_str}`\n\n"
        for entry in history[:20]:
            history_text += f"• `{entry['timestamp']}` - **{entry['action']}**: {entry['details']}\n"
        if len(history) > 20:
            history_text += f"\n... and {len(history) - 20} more entries"
        await message.answer(history_text, parse_mode='Markdown')

    await state.clear()
    await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

@dp.message(AdminStates.awaiting_ban_id)
async def handle_admin_ban_id(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
        banned_users = load_data(BANNED_USERS_FILE)

        if target_id in banned_users:
            await message.answer(f"User {target_id} is already banned.", parse_mode='Markdown')
        else:
            banned_users.append(target_id)
            save_data(banned_users, BANNED_USERS_FILE)
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
        banned_users = load_data(BANNED_USERS_FILE)

        if target_id not in banned_users:
            await message.answer(f"User {target_id} is not banned.", parse_mode='Markdown')
        else:
            banned_users.remove(target_id)
            save_data(banned_users, BANNED_USERS_FILE)
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

        code = f"OSINT-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
        
        redeem_codes = load_data(REDEEM_CODES_FILE)
        redeem_codes[code] = {"credits": credits, "uses_left": uses}
        save_data(redeem_codes, REDEEM_CODES_FILE)
        
        await message.answer(
            f"✅ Code generated successfully!\n\n"
            f"Code: `{code}`\n"
            f"Credits: {credits}\n"
            f"Uses: {uses}",
            parse_mode='Markdown'
        )
        log_user_action(message.from_user.id, "Admin Generate Code", f"Code: {code}, Credits: {credits}, Uses: {uses}")

    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Please use: CREDITS USES")
    finally:
        await state.clear()
        await message.answer("👑 Admin Panel", reply_markup=get_admin_keyboard())

def initialize_data_files():
    for f in [USER_DATA_FILE, REDEEM_CODES_FILE, BANNED_USERS_FILE, PREMIUM_USERS_FILE, FREE_MODE_FILE, USER_HISTORY_FILE]:
        if not os.path.exists(f):
            default_data = {}
            if 'banned' in f or 'premium' in f:
                default_data = []
            elif 'free_mode' in f:
                default_data = {"active": False}
            save_data(default_data, f)

async def main():
    initialize_data_files()
    logger.info("🚀 Starting Enhanced OSINT Bot with Aiogram...")

    global BOT_USERNAME
    try:
        me = await bot.get_me()
        BOT_USERNAME = me.username
    except Exception as e:
        logger.warning(f"Could not fetch bot username: {e}. Using hardcoded value: {BOT_USERNAME}")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())