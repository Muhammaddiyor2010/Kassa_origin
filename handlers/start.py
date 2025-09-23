from aiogram import Router, F
from aiogram.types import Message
from keyboards.keyboards import phone, main_menu
from aiogram.filters.command import Command

from loader import db
from lexicon.lexicon_ru import LEXICON_RU
from lexicon.lexicon_en import LEXICON_EN


start_router: Router = Router()



@start_router.message(Command("start"))
async def start_msg(message: Message):
    user_id = message.from_user.id
    user_language = message.from_user.language_code or 'uz'
    
    # Check if user exists and get their start count
    existing_user = db.select_user(id=user_id)
    
    if existing_user:
        # User exists, increment start count
        db.update_user_start_count(user_id)
        start_count = db.get_user_start_count(user_id)
        
        # If user has started more than 1 time, show welcome back message
        if start_count > 1:
            welcome_message = "Qaytib kelganingizdan xursandmiz! 😊\n\nKassa AI sizga yana xizmat qilishga tayyor!"
            await message.reply(welcome_message, reply_markup=main_menu)
            return
        else:
            # First time user (start_count = 1), ask for phone number
            phone_message = """🎉 Kassa AI ga xush kelibsiz!

📱 Iltimos telefon raqamingizni kiriting (yoki tugmani bosing)

Bu ma'lumot faqat sizning profil ma'lumotlaringiz uchun saqlanadi."""
            await message.reply(phone_message, reply_markup=phone)
            return
    else:
        # New user, add to database with start_count = 1
        try:
            db.add_user(id=user_id, name=message.from_user.full_name, language=user_language)
            print(f"New user added: {user_id} - {message.from_user.full_name}")
        except Exception as e:
            print("Error adding user:", e)
        
        # First time user, ask for phone number
        phone_message = """🎉 Kassa AI ga xush kelibsiz!

📱 Iltimos telefon raqamingizni kiriting (yoki tugmani bosing)

Bu ma'lumot faqat sizning profil ma'lumotlaringiz uchun saqlanadi."""
        await message.reply(phone_message, reply_markup=phone)

@start_router.message(F.contact)
async def phone_msg(message: Message):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number
    
    # Save phone number to database
    db.update_user_phone(phone=phone_number, id=user_id)
    print(f"Phone number saved for user {user_id}: {phone_number}")

    await message.reply("""✅ Telefon raqam saqlandi!

🎉 Kassa AI ga xush kelibsiz! 

Endi siz quyidagi imkoniyatlardan foydalanishingiz mumkin:
• 💸 Harajatlaringizni qo'shish va ko'rish
• 💰 Daromadlaringizni kiritish va kuzatish  
• 📊 Batafsil hisobotlar olish
• 📝 Ovozli yoki matnli xabarlar yuborish

Quyidagi tugmalardan foydalaning yoki harajat/daromad haqida gapiring!""", reply_markup=main_menu)
