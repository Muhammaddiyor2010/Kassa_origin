from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from loader import db, bot
from keyboards.keyboards import main_menu
import io
from google import genai
from google.genai import types
import mimetypes
from aiogram.types import InputFile
import io
import tempfile
import os
client = genai.Client(api_key="AIzaSyAv5lanqXW9KjLFtUhlrGdPvgfdcBz-s4Y")

from utils.gemini import Geminiutils

chiqim_router: Router = Router()

gemini = Geminiutils()


@chiqim_router.message(F.voice)
async def audio_msg(message: Message):
    file_id = message.voice.file_id
    
    file = await bot.get_file(file_id)

    file_obj = io.BytesIO()
 

    file_obj.seek(0)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
        await bot.download_file(file.file_path, destination=temp_file)
        temp_file_path = temp_file.name

    try:
        chiqimtext = gemini.get_text(temp_file_path)
        await message.reply(f"🎤 Transkripsiya: {chiqimtext}")
        
        # Check if transcribed text contains money-related keywords
        text_lower = chiqimtext.lower().strip()
        money_keywords = ['so\'m', 'sum', 'pul', 'harajat', 'chiqim', 'daromad', 'kirim', 'olim', 'berdim', 'sarfladim', 'to\'ladim', 'oldim', 'ish haqi', 'oylik', 'va', 'ham', 'bugun', 'kecha']
        
        if any(keyword in text_lower for keyword in money_keywords):
            # Check user plan and limits
            user_id = message.from_user.id
            user_name = message.from_user.full_name or "Foydalanuvchi"
            plan, _ = db.get_user_plan(user_id)
            
            if plan == 'free':
                # Check AI usage limit for free users (3 AI tests)
                ai_usage_count = db.get_user_ai_usage_count(user_id)
                
                if ai_usage_count >= 3:  # Free plan AI limit
                    limit_text = f"""⚠️ **TEKIN TARIF CHEGARASI** ⚠️

🤖 **AI test limiti:**
• Siz 3 marta AI dan foydalandingiz
• Tekin tarifda faqat 3 ta AI test mumkin

💎 **PRO tarif olish:**
• Cheksiz AI testlar
• Cheksiz daromad/harajat qo'shish
• Batafsil hisobotlar
• VIP qo'llab-quvvatlash

🔑 **PRO olish uchun:** /sozlamalar → 💎 PRO olish"""
                    
                    # Create inline button for PRO upgrade
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    upgrade_keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="💎 PRO olish",
                                    callback_data="upgrade_to_pro"
                                )
                            ]
                        ]
                    )
                    
                    await message.reply(limit_text, reply_markup=upgrade_keyboard, parse_mode="Markdown")
                    return
            
            # Increment AI usage count for free users
            if plan == 'free':
                db.increment_ai_usage_count(user_id)
                print(f"AI usage incremented for user {user_id}, current count: {db.get_user_ai_usage_count(user_id)}")
            
            # Process the transcribed text for both income and expense
            result = gemini.process_text_message(chiqimtext, user_id, user_name)
            await message.reply(result, reply_markup=main_menu)
        else:
            await message.reply("""💬 Bu ovozli xabar harajat/daromad haqida emas.

💰 Harajat/daromad haqida gapiring:
• "Ovqat uchun 50000 so'm sarf qildim"
• "Ish haqim 2000000 so'm oldim"
• "Transport uchun 15000 so'm to'ladim"

🔄 Bir xabarda ikkalasini ham gapiring:
• "Bugun ovqat uchun 50000 so'm sarf qildim va ish haqim 2000000 so'm oldim"
• "Kiyim uchun 150000 so'm to'ladim, savdo daromadim 300000 so'm"

📝 Yoki matnli xabar yuboring!""", reply_markup=main_menu)
        # # Gemini'ga yuklash
        # myfile = client.files.upload(file=temp_file_path)
        # # myfile = client.files.upload(file=file_obj, config={ mime_type: "audio/ogg" })

        # prompt = "Ushbu o'zbek tilidagi audioni matnga aylantir"

        # response = client.models.generate_content(
        # model='gemini-2.5-flash',
        # contents=[prompt, myfile]
        # )
        # print(response.text)
        # await message.reply(f" {response.text}")

    except Exception as e:
  # Temporary file'ni o'chiramiz
        print(f"errors: {e}")
        await message.reply(f"error: {e}")
    finally:
      
        os.unlink(temp_file_path)

@chiqim_router.message(F.text & ~F.text.startswith('/') & ~F.text.in_(["💸 Harajatlari", "💰 Daromadlari", "📊 Hisobot", "⚙️ Sozlamalar", "📊 Statistika", "👥 Foydalanuvchilar", "📢 Reklama yuborish", "👑 Adminlar", "🔙 Asosiy menyu", "👤 Profil ma'lumotlari", "💎 Tarif", "💎 PRO olish", "👑 Admin olish", "🗑️ Ma'lumotlarni tozalash", "🗑️ Daromadlarni o'chirish", "🗑️ Harajatlarni o'chirish", "🗑️ Barcha ma'lumotlarni o'chirish", "ℹ️ Yordam", "🔙 Sozlamalar"]))
async def text_msg(message: Message):
    """
    Handle text messages for income and expense processing
    """
    try:
        # Get user information
        user_id = message.from_user.id
        user_name = message.from_user.full_name or "Foydalanuvchi"
        text = message.text.lower().strip()
        
        # Skip processing if user is admin and might be sending broadcast message
        # This prevents admin broadcast messages from being processed as income/expense
        if db.is_admin(user_id):
            # Check if this looks like a broadcast message (not income/expense related)
            money_keywords = ['so\'m', 'sum', 'pul', 'harajat', 'chiqim', 'daromad', 'kirim', 'olim', 'berdim', 'sarfladim', 'to\'ladim', 'oldim', 'ish haqi', 'oylik', 'va', 'ham', 'bugun', 'kecha']
            if not any(keyword in text for keyword in money_keywords):
                # This is likely a broadcast message, don't process it
                return
        
        # Check user plan and AI usage limits
        plan, _ = db.get_user_plan(user_id)
        
        if plan == 'free':
            # Check AI usage limit for free users (3 AI tests)
            ai_usage_count = db.get_user_ai_usage_count(user_id)
            
            if ai_usage_count >= 3:  # Free plan AI limit
                limit_text = f"""⚠️ **TEKIN TARIF CHEGARASI** ⚠️

🤖 **AI test limiti:**
• Siz 3 marta AI dan foydalandingiz
• Tekin tarifda faqat 3 ta AI test mumkin

💎 **PRO tarif olish:**
• Cheksiz AI testlar
• Cheksiz daromad/harajat qo'shish
• Batafsil hisobotlar
• VIP qo'llab-quvvatlash

🔑 **PRO olish uchun:** /sozlamalar → 💎 PRO olish"""
                
                # Create inline button for PRO upgrade
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                upgrade_keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="💎 PRO olish",
                                callback_data="upgrade_to_pro"
                            )
                        ]
                    ]
                )
                
                await message.reply(limit_text, reply_markup=upgrade_keyboard, parse_mode="Markdown")
                return
        
        # Check if the message looks like it might be about income/expense
        # Simple keyword detection - expanded for multiple operations
        money_keywords = ['so\'m', 'sum', 'pul', 'harajat', 'chiqim', 'daromad', 'kirim', 'olim', 'berdim', 'sarfladim', 'to\'ladim', 'oldim', 'ish haqi', 'oylik', 'va', 'ham', 'bugun', 'kecha']
        
        if any(keyword in text for keyword in money_keywords):
            # Increment AI usage count for free users
            if plan == 'free':
                db.increment_ai_usage_count(user_id)
                print(f"AI usage incremented for user {user_id}, current count: {db.get_user_ai_usage_count(user_id)}")
            
            # Process the text message using Gemini AI
            result = gemini.process_text_message(message.text, user_id, user_name)
            await message.reply(result, reply_markup=main_menu)
        else:
            # Not related to money, show helpful message
            await message.reply("""💬 Bu xabar harajat/daromad haqida emas.

💰 Harajat/daromad qo'shish uchun quyidagicha yozing:
• "Ovqat uchun 50000 so'm sarf qildim"
• "Ish haqim 2000000 so'm oldim"
• "Transport uchun 15000 so'm to'ladim"

🔄 Bir xabarda ikkalasini ham:
• "Bugun ovqat uchun 50000 so'm sarf qildim va ish haqim 2000000 so'm oldim"
• "Kiyim uchun 150000 so'm to'ladim, savdo daromadim 300000 so'm"

📝 Yoki ovozli xabar yuboring!""", reply_markup=main_menu)
        
    except Exception as e:
        print(f"Error processing text message: {e}")
        await message.reply(f"""❌ Xatolik yuz berdi: {str(e)}

🔧 Texnik xatolik. Iltimos:
• Xabarni qayta yuboring
• Agar muammo davom etsa, admin bilan bog'laning""")

    
    
        
      