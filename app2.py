import asyncio
import random
import json
import os
import logging
from telegram import Update, Bot, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ChatMemberHandler,
    filters
)

# Logging Setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION & STORAGE ---
TOKEN = "9116044625:AAG5jTvKuPEFVmBJUHfYEQp9PEUEYNA7hco"
OWNER_ID = 8912043173

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "bot_database_v24.json")

class BotDatabase:
    def __init__(self):
        self.normal_replies = []
        self.active_attacks = {} 
        self.known_chats = set()
        self.authorized_users = {OWNER_ID}
        
        self.custom_welcomes = {}
        self.custom_goodbyes = {}
        
        self.load()

    def save(self):
        data = {
            "normal_replies": self.normal_replies,
            "known_chats": list(self.known_chats),
            "authorized_users": list(self.authorized_users),
            "custom_welcomes": self.custom_welcomes,
            "custom_goodbyes": self.custom_goodbyes
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Save error: {e}")

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.normal_replies = data.get("normal_replies", self.normal_replies)
                    self.known_chats = set(data.get("known_chats", []))
                    saved_users = data.get("authorized_users", [OWNER_ID])
                    self.authorized_users = set(saved_users)
                    self.authorized_users.add(OWNER_ID)
                    self.custom_welcomes = data.get("custom_welcomes", {})
                    self.custom_goodbyes = data.get("custom_goodbyes", {})
            except Exception as e:
                logger.error(f"Load error: {e}")

db = BotDatabase()

async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    if user.id == OWNER_ID or user.id in db.authorized_users:
        return True
    
    chat = update.effective_chat
    if chat.type != "private":
        try:
            member = await chat.get_member(user.id)
            if member.status in ["administrator", "creator"]:
                return True
        except Exception:
            pass
    return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db.known_chats.add(chat_id)
    db.save()
    
    msg = (
        "⚡ 𝓝𝓮𝓿𝓮𝓻𝓶𝓸𝓻𝓮 𝓐𝓽𝓽𝓪𝕔𝓴 & 𝓜𝓪𝓷𝓪𝓰𝓮𝓶𝓮𝓷𝓽 𝓑𝓸𝓽 ⚡\n\n"
        "✨ ဘော့အသုံးပြုရန် Command များကို ကြည့်ရန် `list` ဟု ရိုက်ပါရှင်။"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "╔══════════════════════╗\n"
        "   👑 **𝓑𝓞𝓣 𝓒𝓞𝓜𝓜𝓐𝓝𝓓 𝓛𝓘𝓢𝓣** 👑\n"
        "╚══════════════════════╝\n\n"
        "🎯 **Turbo Multi-Target Attack Commands:**\n"
        "• `လီးဖြစ်တာလား` - (Reply လုပ်ပြီး) အလွန်မြန်သောနှုန်းဖြင့် အသေစာထောက်မည်။\n"
        "• `သူကိုဆဲ` - (Reply လုပ်ပြီး) Target ကို MT ဖြင့် အမြန်ဆုံး အသေဆဲမည်။\n"
        "• `ရပ်` - တိုက်ခိုက်မှုများကို ချက်ချင်းရပ်မည်။\n\n"
        "📥 **Manage Replies Commands:**\n"
        "• `++` သို့မဟုတ် `/addreply` - ဆဲစာထည့်ရန်။\n"
        "• `/stopaddreply` - ဆဲစာထည့်ခြင်းကို ရပ်ရန်။\n"
        "• `/remove` - ဆဲစာဖျက်ရန်။\n"
        "• `/stopremove` - ဆဲစာဖျက်ခြင်းကို ရပ်ရန်။\n"
        "• `သတ်ပီ` - ဆဲစာစာရင်း ကြည့်ရန်။\n"
        "• `/remove_all_replies` - ဆဲစာ အားလုံးရှင်းရန်။\n\n"
        "⚙️ **Custom Welcome & Goodbye Settings:**\n"
        "• `/setwelcome [စာသား]` - ဂရု၏ ကြိုဆိုစာကို ကိုယ်ပိုင်သတ်မှတ်ရန်။\n"
        "• `/setgoodbye [စာသား]` - ဂရု၏ ထွက်သွားသောစာကို ကိုယ်ပိုင်သတ်မှတ်ရန်။\n"
        "• `/resetwelcome` - မူလ Welcome စာသို့ ပြန်ပြောင်းရန်။\n"
        "• `/resetgoodbye` - မူလ Goodbye စာသို့ ပြန်ပြောင်းရန်။\n\n"
        "👑 **Owner & Admin Authorization:**\n"
        "• `သုံး` - (Reply လုပ်ပြီး) အက်မင်ပါမစ် ပေးမည်။\n\n"
        "🛠️ **Rose Bot Style Community Tools:**\n"
        "• `/ban` သို့မဟုတ် `ban` - Member ကို Ban မည်။\n"
        "• `/mute` သို့မဟုတ် `mute` - Mute လုပ်မည်။\n"
        "• `/unmute` သို့မဟုတ် `unmute` - Mute ဖြေမည်။\n"
        "• `/kick` သို့မဟုတ် `kick` - Group မှ ကစ်ထုတ်မည်။\n"
        "• `/pin` - မက်ဆေ့ခ်ျ Pin တင်မည်။\n"
        "• `/unpin` - Pin ဖြုတ်မည်။\n"
        "• `/delete` သို့မဟုတ် `/del` - မက်ဆေ့ခ်ျဖျက်မည်။\n\n"
        "📢 **Broadcast System:**\n"
        "• `/send` - (Reply လုပ်ပြီး) Group အားလုံးထံ Forward မည်။"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# --- TURBO INFINITE ATTACK WORKER (ULTRA FAST & NEVER STOPS UNTIL 'ရပ်') ---
async def attack_worker(application):
    while True:
        try:
            if db.active_attacks and db.normal_replies:
                for chat_id, targets in list(db.active_attacks.items()):
                    if not targets:
                        continue
                    
                    for info in targets:
                        reply_text = random.choice(db.normal_replies)
                        try:
                            if info["mode"] == "spam":
                                await application.bot.send_message(
                                    chat_id=chat_id,
                                    text=reply_text,
                                    reply_to_message_id=info["target_msg_id"]
                                )
                            elif info["mode"] == "mt":
                                target_name = info.get("target_name", "User")
                                target_id = info.get("target_id")
                                mention = f"[{target_name}](tg://user?id={target_id})"
                                final_str = f"{mention} {reply_text}"
                                
                                await application.bot.send_message(
                                    chat_id=chat_id,
                                    text=final_str,
                                    parse_mode="Markdown"
                                )
                        except Exception as e:
                            # Telegram Rate Limit သို့မဟုတ် Error တက်ရင်တောင် Loop မရပ်ဘဲ ဆက်သွားရန်
                            pass
                
                # အမြန်ဆုံး အရှိန် (Delay လုံးဝမရှိသလောက် နည်းအောင် လုပ်ထားသည်)
                await asyncio.sleep(0.02)
            else:
                await asyncio.sleep(0.2)
        except Exception as err:
            logger.error(f"Worker general error: {err}")
            await asyncio.sleep(0.2)

# --- DEDICATED STOP COMMAND HANDLERS ---
async def stop_add_reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["adding_mode"] = False
    db.save()
    await update.message.reply_text(f"✅ ဆဲစာထည့်ခြင်း ပြီးဆုံးပါပြီ။ (စုစုပေါင်း ဆဲစာ - {len(db.normal_replies)} ခု)")

async def stop_remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["removing_mode"] = False
    db.save()
    await update.message.reply_text(f"✅ ဆဲစာဖျက်ခြင်း ပြီးဆုံးပါပြီ။ (လက်ကျန်: {len(db.normal_replies)} ခု)")

async def set_welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        await update.message.reply_text("⚠️ ဤ Command ကို အသုံးပြုရန် Admin ဖြစ်ရန် လိုအပ်ပါသည်။")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ သတ်မှတ်လိုသော Welcome စာကို ထည့်ပါ။ ဥပမာ: `/setwelcome မင်္ဂလာပါရှင် {name}`")
        return
    chat_id = str(update.effective_chat.id)
    db.custom_welcomes[chat_id] = text
    db.save()
    await update.message.reply_text("✅ ဤ Group အတွက် Custom Welcome စာကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။ ✨")

async def set_goodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        await update.message.reply_text("⚠️ ဤ Command ကို အသုံးပြုရန် Admin ဖြစ်ရန် လိုအပ်ပါသည်။")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ သတ်မှတ်လိုသော Goodbye စာကို ထည့်ပါ။ ဥပမာ: `/setgoodbye နောက်ထပ်တွေ့မယ် {name}`")
        return
    chat_id = str(update.effective_chat.id)
    db.custom_goodbyes[chat_id] = text
    db.save()
    await update.message.reply_text("✅ ဤ Group အတွက် Custom Goodbye စာကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။ ✨")

async def reset_welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    chat_id = str(update.effective_chat.id)
    if chat_id in db.custom_welcomes:
        del db.custom_welcomes[chat_id]
        db.save()
    await update.message.reply_text("🔄 Welcome စာကို မူလပုံစံသို့ ပြန်ပြောင်းလိုက်ပါပြီ။")

async def reset_goodbye_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    chat_id = str(update.effective_chat.id)
    if chat_id in db.custom_goodbyes:
        del db.custom_goodbyes[chat_id]
        db.save()
    await update.message.reply_text("🔄 Goodbye စာကို မူလပုံစံသို့ ပြန်ပြောင်းလိုက်ပါပြီ။")

# --- TEXT & COMMAND LISTENER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    db.known_chats.add(chat_id)

    if context.user_data.get("adding_mode"):
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            db.normal_replies.extend(lines)
            db.save()
            await update.message.reply_text(f"📥 ဆဲစာအသစ် {len(lines)} ခု ထပ်တိုးသိမ်းပြီးပါပြီ။ (စုစုပေါင်း: {len(db.normal_replies)})")
        return

    if context.user_data.get("removing_mode"):
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        removed = 0
        for line in lines:
            if line in db.normal_replies:
                db.normal_replies.remove(line)
                removed += 1
        db.save()
        await update.message.reply_text(f"🗑️ ဆဲစာ {removed} ခု ဖျက်ပြီးပါပြီ။ (လက်ကျန်: {len(db.normal_replies)})")
        return

    if text in ["list", "အကူအညီ", "help", "/help"]:
        await help_command(update, context)
        return
    if text in ["စရန်", "/start"]:
        await start_command(update, context)
        return

    if text == "သုံး":
        if user_id != OWNER_ID:
            await update.message.reply_text("⚠️ ဤ Command သည် Bot Owner တစ်ယောက်တည်းသာ အသုံးပြုနိုင်ပါသည်။")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ဘော့အသုံးပြုခွင့်ပေးလိုသူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပြီးမှ `သုံး` ဟု ရိုက်ပါ။")
            return

        target_user = update.message.reply_to_message.from_user
        if not target_user:
            return

        db.authorized_users.add(target_user.id)
        db.save()
        
        await update.message.reply_text(f"✅ အဲ့ဒီလူ [{target_user.first_name}] ကို ဘော့အသုံးပြုခွင့် အက်မင်အဖြစ် သတ်မှတ်ပြီးပါပြီ။")
        await update.message.reply_text("🎉 အခုလို ဘော့ကို အသုံးပြုပေးလို့ ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။ 🙏✨")
        return

    if not await is_authorized(update, context):
        return

    # Turbo Spam Attack: လီးဖြစ်တာလား
    if text == "လီးဖြစ်တာလား":
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ဆဲလိုသူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပြီးမှ 'လီးဖြစ်တာလား' ဟု ရိုက်ပါ။")
            return
        
        if not db.normal_replies:
            await update.message.reply_text("⚠️ ဆဲစာများ မရှိသေးပါ။ `++` သို့မဟုတ် `/addreply` ဖြင့် အရင်ထည့်ပါ။")
            return
        
        reply_msg = update.message.reply_to_message
        new_target = {
            "mode": "spam",
            "target_msg_id": reply_msg.id,
            "target_id": reply_msg.from_user.id if reply_msg.from_user else 0
        }
        
        if chat_id not in db.active_attacks:
            db.active_attacks[chat_id] = []
        
        db.active_attacks[chat_id].append(new_target)
        await update.message.reply_text(f"🔥 **Turbo Spam Attack Activated!** (Targets: {len(db.active_attacks[chat_id])})")
        return

    # Turbo MT Attack: သူကိုဆဲ
    if text == "သူကိုဆဲ":
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ မန်းရှင်းခေါ်ပြီး ဆဲမည့်သူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပြီးမှ 'သူကိုဆဲ' ဟု ရိုက်ပါ။")
            return

        if not db.normal_replies:
            await update.message.reply_text("⚠️ ဆဲစာများ မရှိသေးပါ။ `++` သို့မဟုတ် `/addreply` ဖြင့် အရင်ထည့်ပါ။")
            return

        reply_msg = update.message.reply_to_message
        target_user = reply_msg.from_user
        if not target_user:
            return
            
        new_target = {
            "mode": "mt",
            "target_id": target_user.id,
            "target_name": target_user.first_name or "User"
        }
        
        if chat_id not in db.active_attacks:
            db.active_attacks[chat_id] = []
            
        db.active_attacks[chat_id].append(new_target)
        await update.message.reply_text(f"🔥 **Turbo MT Attack Activated** for {target_user.first_name} (Targets: {len(db.active_attacks[chat_id])})")
        return

    if text == "ရပ်":
        if chat_id in db.active_attacks:
            del db.active_attacks[chat_id]
        await update.message.reply_text("🔴 **တိုက်ခိုက်မှုများကို အပြီးအပိုင် ရပ်တန့်လိုက်ပါပြီ။**")
        return

    if text in ["++", "/addreply"]:
        context.user_data["adding_mode"] = True
        context.user_data["removing_mode"] = False
        await update.message.reply_text("✍️ ဆဲစာထည့်သွင်းခြင်း စတင်ပါပြီ။ စာများကို ပို့နိုင်ပါပြီ။ ပြီးလျှင် `/stopaddreply` ဟု ရိုက်ပါ။")
        return

    if text == "/remove":
        context.user_data["removing_mode"] = True
        context.user_data["adding_mode"] = False
        await update.message.reply_text("🗑️ ဆဲစာဖျက်မုဒ် စတင်ပါပြီ။ ဖျက်ချင်သောစာများကို ပို့ပါ။ ပြီးလျှင် `/stopremove` ဟု ရိုက်ပါ။")
        return

    if text == "သတ်ပီ":
        norm_list = "\n".join([f"{i+1}. {r}" for i, r in enumerate(db.normal_replies[:30])]) or "မရှိသေးပါ"
        await update.message.reply_text(f"📋 **သိမ်းဆည်းထားသော ဆဲစာစာရင်းများ:**\n{norm_list}")
        return

    if text == "/remove_all_replies":
        db.normal_replies.clear()
        db.save()
        await update.message.reply_text("🗑️ ဆဲစာအားလုံးကို ရှင်းလင်းပြီးပါပြီ။")
        return

# --- ROSE BOT STYLE COMMUNITY TOOLS ---
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Mute လုပ်မည့်သူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပါ။")
        return
    chat = update.effective_chat
    target_user = update.message.reply_to_message.from_user
    try:
        await chat.restrict_member(target_user.id, permissions=ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"🔇 User [{target_user.first_name}](tg://user?id={target_user.id}) ကို Mute လုပ်လိုက်ပါပြီ။", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Unmute လုပ်မည့်သူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပါ။")
        return
    chat = update.effective_chat
    target_user = update.message.reply_to_message.from_user
    try:
        await chat.restrict_member(
            target_user.id,
            permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True)
        )
        await update.message.reply_text(f"🔊 User [{target_user.first_name}](tg://user?id={target_user.id}) ၏ Mute ကို ဖြေပေးလိုက်ပါပြီ။", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Ban လုပ်မည့်သူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပါ။")
        return
    chat = update.effective_chat
    target_user = update.message.reply_to_message.from_user
    try:
        await chat.ban_member(target_user.id)
        await update.message.reply_text(f"🔨 User [{target_user.first_name}](tg://user?id={target_user.id}) ကို Ban လိုက်ပါပြီ။", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kick လုပ်မည့်သူ၏ မက်ဆေ့ခ်ျကို Reply လုပ်ပါ။")
        return
    chat = update.effective_chat
    target_user = update.message.reply_to_message.from_user
    try:
        await chat.ban_member(target_user.id)
        await chat.unban_member(target_user.id)
        await update.message.reply_text(f"👢 User [{target_user.first_name}](tg://user?id={target_user.id}) ကို ဂရုထဲကနေ ကစ်ထုတ်လိုက်ပါပြီ။ 🚀", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def delete_msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    if not update.message.reply_to_message:
        return
    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception as e:
        logger.error(f"Delete error: {e}")

async def pin_msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Pin တင်လိုသော မက်ဆေ့ခ်ျကို Reply လုပ်ပါ။")
        return
    try:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 မက်ဆေ့ခ်ျကို Pin တင်ပြီးပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def unpin_msg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    try:
        await update.effective_chat.unpin_all_messages()
        await update.message.reply_text("🔓 Pin အားလုံးကို ဖြုတ်ပြီးပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- BROADCAST SYSTEM (`/send`) ---
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⚠️ ဤ Command သည် Bot Owner သာ အသုံးပြုနိုင်ပါသည်။")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Forward လုပ်လိုသော မက်ဆေ့ခ်ျကို Reply လုပ်ပြီးမှ `/send` ဟု ရိုက်ပါ။")
        return

    success_count = 0
    fail_count = 0
    
    target_chats = list(db.known_chats)
    if not target_chats:
        target_chats = [update.effective_chat.id]

    msg_to_forward = update.message.reply_to_message

    for chat_id in target_chats:
        try:
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=update.effective_chat.id,
                message_id=msg_to_forward.id
            )
            success_count += 1
            await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Forward fail to {chat_id}: {e}")
            fail_count += 1

    await update.message.reply_text(
        f"📢 **Broadcast ပြီးစီးပါပြီ။**\n"
        f"ဂရုဘယ်နှစ်ခုကို ပို့ပြီးပြီလဲဆိုရင် - စုစုပေါင်း Chat {len(target_chats)} ခုဆီသို့ ပို့ခဲ့ပါသည်။\n"
        f"✅ အောင်မြင်သည့် Chat: {success_count}\n"
        f"❌ မအောင်မြင်သည့် Chat: {fail_count}"
    )

# --- DYNAMIC WELCOME & GOODBYE SYSTEM (CUSTOMIZABLE PER GROUP) ---
async def track_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    chat = result.chat
    chat_id = str(chat.id)
    db.known_chats.add(chat.id)
    db.save()

    new_member = result.new_chat_member
    old_member = result.old_chat_member
    group_name = chat.title or "ဤ Group"

    if old_member.status in ["left", "banned"] and new_member.status in ["member", "administrator"]:
        user = new_member.user
        user_mention = f"[{user.first_name}](tg://user?id={user.id})"
        
        if chat_id in db.custom_welcomes:
            custom_template = db.custom_welcomes[chat_id]
            welcome_text = custom_template.replace("{name}", user_mention).replace("{group}", group_name)
        else:
            welcome_text = (
                f"🌟 **WELCOME TO FAMILY** 🌟\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ မင်္ဂလာပါရှင် လူသစ်လေး {user_mention}\n"
                f"📌 **{group_name}** ဂရုထဲသို့ အပျော်ဆုံးနဲ့ အခန့်ဆုံး ဝင်ရောက်လာပါပြီခင်ဗျာ။ 🔥"
            )
        try:
            await context.bot.send_message(chat_id=chat.id, text=welcome_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Welcome error: {e}")

    elif old_member.status in ["member", "administrator"] and new_member.status in ["left", "banned"]:
        user = new_member.user
        user_mention = f"[{user.first_name}](tg://user?id={user.id})"
        
        if chat_id in db.custom_goodbyes:
            custom_template = db.custom_goodbyes[chat_id]
            goodbye_text = custom_template.replace("{name}", user_mention).replace("{group}", group_name)
        else:
            if new_member.status == "banned":
                goodbye_text = (
                    f"🚨 **BANNED / KICKED ALERT** 🚨\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ {user_mention} ကို ဂရုထဲကနေ ကစ်ထုတ်လိုက်ပါပြီ။ ခရီးဦးကောင်းပါစေဗျာ။ 🚮"
                )
            else:
                goodbye_text = (
                    f"👋 **GOODBYE MEMBER** 👋\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🚶‍♂️ {user_mention} ကတော့ ဤ Group လေးကနေ ထွက်သွားပါပြီ။ နောက်မှ ပြန်တွေ့ကြမယ်လေ။ ✨"
                )
        try:
            await context.bot.send_message(chat_id=chat.id, text=goodbye_text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Goodbye error: {e}")

# --- MAIN APP SETUP ---
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", help_command))
    
    application.add_handler(CommandHandler("stopaddreply", stop_add_reply_command))
    application.add_handler(CommandHandler("stopremove", stop_remove_command))
    
    application.add_handler(CommandHandler("setwelcome", set_welcome_command))
    application.add_handler(CommandHandler("setgoodbye", set_goodbye_command))
    application.add_handler(CommandHandler("resetwelcome", reset_welcome_command))
    application.add_handler(CommandHandler("resetgoodbye", reset_goodbye_command))
    
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("delete", delete_msg_command))
    application.add_handler(CommandHandler("del", delete_msg_command))
    application.add_handler(CommandHandler("pin", pin_msg_command))
    application.add_handler(CommandHandler("unpin", unpin_msg_command))
    application.add_handler(CommandHandler("send", broadcast_command))
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(ChatMemberHandler(track_chat_members, ChatMemberHandler.CHAT_MEMBER))

    loop = asyncio.get_event_loop()
    loop.create_task(attack_worker(application))

    print("🤖 Telegram Bot is running successfully with Turbo Infinite Attack Mode...")
    application.run_polling()

if __name__ == "__main__":
    main()