from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loader import db
from keyboards.keyboards import main_menu

sozlamalar_router: Router = Router()

# States for token input
class TokenStates(StatesGroup):
    waiting_for_token = State()

class AdminTokenStates(StatesGroup):
    waiting_for_admin_token = State()

# Settings menu keyboard
settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👤 Profil ma'lumotlari"),
            KeyboardButton(text="📊 Statistika")
        ],
        [
            KeyboardButton(text="💎 Tarif"),
            KeyboardButton(text="🗑️ Ma'lumotlarni tozalash")
        ],
        [
            KeyboardButton(text="💎 PRO olish"),
            KeyboardButton(text="👑 Admin olish")
        ],
        [
            KeyboardButton(text="ℹ️ Yordam"),
            KeyboardButton(text="🔙 Asosiy menyu")
        ]
    ],
    resize_keyboard=True,
    persistent=True
)


@sozlamalar_router.message(Command("sozlamalar"))
@sozlamalar_router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message):
    """
    Show settings menu
    """
    try:
        user_id = message.from_user.id
        user_info = db.select_user(id=user_id)
        
        if user_info:
            user_name = user_info[1]
            user_phone = user_info[3] or "Kiritilmagan"
            user_language = user_info[2] or "uz"
            start_count = user_info[6] if len(user_info) > 6 else 0
            
            # Get user plan
            plan, _ = db.get_user_plan(user_id)
            plan_emoji = "💎" if plan == 'pro' else "🆓"
            plan_text = "PRO" if plan == 'pro' else "TEKIN"
            
            settings_text = f"""⚙️ **SOZLAMALAR** ⚙️

👤 **Profil ma'lumotlari:**
• Ism: {user_name}
• Telefon: {user_phone}
• Til: {user_language.upper()}
• Bot ishlatish soni: {start_count} marta

💎 **Tarif:** {plan_emoji} {plan_text}

📊 **Statistika:**
• Daromadlar soni: {len(db.get_user_kirim(user_id)) if db.get_user_kirim(user_id) else 0} ta
• Harajatlar soni: {len(db.get_user_chiqim(user_id)) if db.get_user_chiqim(user_id) else 0} ta

🔧 **Sozlamalar:**
Quyidagi tugmalardan foydalaning:"""
        else:
            settings_text = """⚙️ **SOZLAMALAR** ⚙️

❌ Profil ma'lumotlari topilmadi.

🔧 **Sozlamalar:**
Quyidagi tugmalardan foydalaning:"""
        
        await message.reply(settings_text, reply_markup=settings_menu, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error showing settings: {e}")
        await message.reply(
            f"❌ Sozlamalarni ko'rsatishda xatolik: {str(e)}",
            reply_markup=main_menu
        )


@sozlamalar_router.message(F.text == "👤 Profil ma'lumotlari")
async def show_profile(message: Message):
    """
    Show detailed profile information
    """
    try:
        user_id = message.from_user.id
        user_info = db.select_user(id=user_id)
        
        if user_info:
            user_name = user_info[1]
            user_phone = user_info[3] or "Kiritilmagan"
            user_language = user_info[2] or "uz"
            start_count = user_info[6] if len(user_info) > 6 else 0
            
            profile_text = f"""👤 **PROFIL MA'LUMOTLARI** 👤

🆔 **ID:** {user_id}
👤 **Ism:** {user_name}
📞 **Telefon:** {user_phone}
🌐 **Til:** {user_language.upper()}
🚀 **Bot ishlatish soni:** {start_count} marta

📊 **Ma'lumotlar:**
• Daromadlar: {len(db.get_user_kirim(user_id)) if db.get_user_kirim(user_id) else 0} ta
• Harajatlar: {len(db.get_user_chiqim(user_id)) if db.get_user_chiqim(user_id) else 0} ta

💡 **Maslahat:**
Telefon raqamingizni yangilash uchun /start buyrug'ini qayta ishlatishingiz mumkin."""
        else:
            profile_text = """👤 **PROFIL MA'LUMOTLARI** 👤

❌ Profil ma'lumotlari topilmadi.

💡 **Yechim:**
/start buyrug'ini qayta ishlatib, profilni qayta yarating."""
        
        await message.reply(profile_text, reply_markup=settings_menu, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error showing profile: {e}")
        await message.reply(
            f"❌ Profil ma'lumotlarini ko'rsatishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    """
    Show detailed statistics
    """
    try:
        user_id = message.from_user.id
        
        # Get data
        income_data = db.get_user_kirim(user_id)
        expenses_data = db.get_user_chiqim(user_id)
        
        # Calculate statistics
        total_income = 0
        total_expenses = 0
        
        if income_data:
            for inc in income_data:
                try:
                    amount = int(inc[1].replace(' ', '').replace(',', ''))
                    total_income += amount
                except (ValueError, AttributeError):
                    pass
        
        if expenses_data:
            for exp in expenses_data:
                try:
                    amount = int(exp[1].replace(' ', '').replace(',', ''))
                    total_expenses += amount
                except (ValueError, AttributeError):
                    pass
        
        # Calculate averages
        avg_income = total_income // len(income_data) if income_data else 0
        avg_expenses = total_expenses // len(expenses_data) if expenses_data else 0
        
        # Get categories
        income_categories = {}
        expense_categories = {}
        
        if income_data:
            for inc in income_data:
                category = inc[3] or "Kategoriya yo'q"
                income_categories[category] = income_categories.get(category, 0) + 1
        
        if expenses_data:
            for exp in expenses_data:
                category = exp[3] or "Kategoriya yo'q"
                expense_categories[category] = expense_categories.get(category, 0) + 1
        
        stats_text = f"""📊 **BATAFSIL STATISTIKA** 📊

💰 **DAROMADLAR:**
• Jami: {total_income:,} so'm
• Soni: {len(income_data) if income_data else 0} ta
• O'rtacha: {avg_income:,} so'm

💸 **HARAJATLAR:**
• Jami: {total_expenses:,} so'm
• Soni: {len(expenses_data) if expenses_data else 0} ta
• O'rtacha: {avg_expenses:,} so'm

📈 **BALANS:**
• Qolgan: {total_income - total_expenses:,} so'm

📂 **KATEGORIYALAR:**

💰 **Daromad kategoriyalari:**
"""
        
        if income_categories:
            for category, count in income_categories.items():
                stats_text += f"• {category}: {count} ta\n"
        else:
            stats_text += "• Kategoriyalar yo'q\n"
        
        stats_text += "\n💸 **Harajat kategoriyalari:**\n"
        
        if expense_categories:
            for category, count in expense_categories.items():
                stats_text += f"• {category}: {count} ta\n"
        else:
            stats_text += "• Kategoriyalar yo'q\n"
        
        if not income_data and not expenses_data:
            stats_text = """📊 **BATAFSIL STATISTIKA** 📊

❌ **Ma'lumot yo'q**

Hali hech qanday daromad yoki harajat kiritilmagan.

💰 Daromad va harajatlar kiritgandan keyin statistika ko'rinadi."""
        
        await message.reply(stats_text, reply_markup=settings_menu, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error showing statistics: {e}")
        await message.reply(
            f"❌ Statistika ko'rsatishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(F.text == "🗑️ Ma'lumotlarni tozalash")
async def clear_data(message: Message):
    """
    Show data clearing options
    """
    clear_menu = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🗑️ Daromadlarni o'chirish"),
                KeyboardButton(text="🗑️ Harajatlarni o'chirish")
            ],
            [
                KeyboardButton(text="🗑️ Barcha ma'lumotlarni o'chirish"),
                KeyboardButton(text="🔙 Sozlamalar")
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    
    await message.reply(
        """🗑️ **MA'LUMOTLARNI TOZALASH** 🗑️

⚠️ **DIQQAT!** Bu amallar qaytarib bo'lmaydi!

🔧 **Tanlang:**
• Daromadlarni o'chirish - faqat daromadlar o'chiriladi
• Harajatlarni o'chirish - faqat harajatlar o'chiriladi  
• Barcha ma'lumotlarni o'chirish - hamma narsa o'chiriladi

💡 **Maslahat:** Ma'lumotlarni saqlab qolish uchun hisobot yarating.""",
        reply_markup=clear_menu,
        parse_mode="Markdown"
    )


@sozlamalar_router.message(F.text == "🗑️ Daromadlarni o'chirish")
async def clear_income(message: Message):
    """
    Clear all income data
    """
    try:
        user_id = message.from_user.id
        
        # Delete all income records for user
        db.execute(
            "DELETE FROM Kirim WHERE user_id = ?",
            parameters=(user_id,),
            commit=True
        )
        
        await message.reply(
            "✅ **Daromadlar o'chirildi!**\n\n"
            "Barcha daromad ma'lumotlari muvaffaqiyatli o'chirildi.",
            reply_markup=settings_menu,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"Error clearing income: {e}")
        await message.reply(
            f"❌ Daromadlarni o'chirishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(F.text == "🗑️ Harajatlarni o'chirish")
async def clear_expenses(message: Message):
    """
    Clear all expense data
    """
    try:
        user_id = message.from_user.id
        
        # Delete all expense records for user
        db.execute(
            "DELETE FROM Chiqim WHERE user_id = ?",
            parameters=(user_id,),
            commit=True
        )
        
        await message.reply(
            "✅ **Harajatlar o'chirildi!**\n\n"
            "Barcha harajat ma'lumotlari muvaffaqiyatli o'chirildi.",
            reply_markup=settings_menu,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"Error clearing expenses: {e}")
        await message.reply(
            f"❌ Harajatlarni o'chirishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(F.text == "🗑️ Barcha ma'lumotlarni o'chirish")
async def clear_all_data(message: Message):
    """
    Clear all user data
    """
    try:
        user_id = message.from_user.id
        
        # Delete all records for user
        db.execute(
            "DELETE FROM Kirim WHERE user_id = ?",
            parameters=(user_id,),
            commit=True
        )
        db.execute(
            "DELETE FROM Chiqim WHERE user_id = ?",
            parameters=(user_id,),
            commit=True
        )
        
        await message.reply(
            "✅ **Barcha ma'lumotlar o'chirildi!**\n\n"
            "Barcha daromad va harajat ma'lumotlari muvaffaqiyatli o'chirildi.\n\n"
            "💡 Yangi ma'lumotlar qo'shish uchun /start buyrug'ini ishlatishingiz mumkin.",
            reply_markup=settings_menu,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"Error clearing all data: {e}")
        await message.reply(
            f"❌ Ma'lumotlarni o'chirishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(F.text == "ℹ️ Yordam")
async def show_help(message: Message):
    """
    Show help information
    """
    help_text = """ℹ️ **YORDAM** ℹ️

🤖 **Kassa AI** - moliyaviy hisob-kitoblar uchun yordamchi bot

📋 **ASOSIY FUNKSIYALAR:**

💰 **Daromad qo'shish:**
• "Ish haqim 2000000 so'm oldim"
• "Savdo daromadim 500000 so'm"
• Ovozli xabar yuboring

💸 **Harajat qo'shish:**
• "Ovqat uchun 50000 so'm sarf qildim"
• "Transport uchun 15000 so'm to'ladim"
• Ovozli xabar yuboring

📊 **Hisobot ko'rish:**
• Barcha daromad va harajatlarni ko'ring
• Balansni hisoblang
• Statistika oling

⚙️ **Sozlamalar:**
• Profil ma'lumotlari
• Statistika
• Ma'lumotlarni tozalash

🎯 **MASLAHATLAR:**
• Harajat/daromad haqida gapiring
• Bir xabarda ikkalasini ham yozing
• Ovozli xabarlar ham qo'llab-quvvatlanadi

📞 **QO'LLAB-QUVVATLASH:**
Agar muammo bo'lsa, admin bilan bog'laning."""
    
    await message.reply(help_text, reply_markup=settings_menu, parse_mode="Markdown")


@sozlamalar_router.message(F.text == "💎 Tarif")
async def show_plan_info(message: Message):
    """
    Show current plan and upgrade options
    """
    try:
        user_id = message.from_user.id
        plan, pro_token = db.get_user_plan(user_id)
        
        if plan == 'pro':
            plan_text = f"""💎 **PRO TARIF** 💎

✅ **Sizning tarifingiz:** PRO
🔑 **Token:** {pro_token[:8]}...{pro_token[-4:] if pro_token and len(pro_token) > 12 else pro_token}

🚀 **PRO imkoniyatlari:**
• Cheksiz daromad/harajat qo'shish
• Batafsil hisobotlar
• Statistika va tahlil
• VIP qo'llab-quvvatlash
• Barcha funksiyalar

🎉 **Rahmat!** Siz PRO tarifdan foydalanmoqdasiz."""
            
            await message.reply(plan_text, reply_markup=settings_menu, parse_mode="Markdown")
        else:
            # Free plan - show upgrade option
            plan_text = """🆓 **TEKIN TARIF** 🆓

📊 **Hozirgi imkoniyatlar:**
• 10 ta daromad/harajat qo'shish
• Asosiy hisobotlar
• Statistika ko'rish
• Ma'lumotlarni tozalash

💎 **PRO tarif imkoniyatlari:**
• Cheksiz daromad/harajat qo'shish
• Batafsil hisobotlar va tahlil
• VIP qo'llab-quvvatlash
• Barcha funksiyalar

🔑 **PRO tarif olish uchun "💎 PRO olish" tugmasini bosing!**"""
            
            await message.reply(plan_text, reply_markup=settings_menu, parse_mode="Markdown")
            
    except Exception as e:
        print(f"Error showing plan info: {e}")
        await message.reply(
            f"❌ Tarif ma'lumotlarini ko'rsatishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(F.text == "👑 Admin olish")
async def handle_admin_upgrade(message: Message, state: FSMContext):
    """
    Handle Admin upgrade button click
    """
    print(f"🔍 ADMIN UPGRADE REQUESTED from user {message.from_user.id}")
    
    try:
        # Get user ID
        user_id = message.from_user.id
        print(f"📱 Processing admin upgrade for user {user_id}")
        
        # Check if user already has admin
        try:
            is_admin = db.is_admin(user_id)
            print(f"📊 User {user_id} is admin: {is_admin}")
        except Exception as db_error:
            print(f"❌ Database error checking admin status: {db_error}")
            await message.reply(
                "❌ Database xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
            return
        
        if is_admin:
            print(f"ℹ️ User {user_id} already has admin access")
            await message.reply(
                "✅ Siz allaqachon admin huquqiga egasiz!",
                reply_markup=settings_menu
            )
            return
        
        # Show admin token input instructions
        print(f"🔑 Showing admin token input for user {user_id}")
        admin_token_text = """👑 **ADMIN TOKEN KIRITISH** 👑

Admin huquqini olish uchun admin token kerak.

📝 **Admin token qanday olish:**
1. Mavjud admin bilan bog'laning
2. "Admin token kerak" deb yozing
3. Admin token oling va bu yerga kiriting

💡 **Admin token kiritish:**
Tokenni matn ko'rinishida yuboring (masalan: ADMIN123456789)

❌ **Bekor qilish:** /cancel"""
        
        await message.reply(admin_token_text, reply_markup=settings_menu)
        
        # Set state to wait for admin token
        try:
            await state.set_state(AdminTokenStates.waiting_for_admin_token)
            print(f"✅ State set to waiting_for_admin_token for user {user_id}")
        except Exception as state_error:
            print(f"❌ State error: {state_error}")
            await message.reply(
                "❌ State xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
        
        print(f"🎉 Admin upgrade request completed successfully for user {user_id}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in admin upgrade: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        await message.reply(
            "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
            reply_markup=settings_menu
        )

@sozlamalar_router.message(F.text == "💎 PRO olish")
async def handle_pro_upgrade(message: Message, state: FSMContext):
    """
    Handle PRO upgrade button click
    """
    print(f"🔍 PRO UPGRADE REQUESTED from user {message.from_user.id}")
    
    try:
        # Get user ID
        user_id = message.from_user.id
        print(f"📱 Processing upgrade for user {user_id}")
        
        # Check if user already has pro
        try:
            plan, _ = db.get_user_plan(user_id)
            print(f"📊 User {user_id} current plan: {plan}")
        except Exception as db_error:
            print(f"❌ Database error getting user plan: {db_error}")
            await message.reply(
                "❌ Database xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
            return
        
        if plan == 'pro':
            print(f"ℹ️ User {user_id} already has PRO plan")
            await message.reply(
                "✅ Siz allaqachon PRO tarifdan foydalanmoqdasiz!",
                reply_markup=settings_menu
            )
            return
        
        # Show token input instructions
        print(f"🔑 Showing token input for user {user_id}")
        token_text = """🔑 **PRO TOKEN KIRITISH** 🔑

Pro tarif olish uchun token kerak.

📝 **Token qanday olish:**
1. @Dier_ai ga yozing
2. "Pro token kerak" deb yozing
3. Token oling va bu yerga kiriting

💡 **Token kiritish:**
Tokenni matn ko'rinishida yuboring (masalan: PRO123456789)

❌ **Bekor qilish:** /cancel"""
        
        await message.reply(token_text, reply_markup=settings_menu)
        
        # Set state to wait for token
        try:
            await state.set_state(TokenStates.waiting_for_token)
            print(f"✅ State set to waiting_for_token for user {user_id}")
        except Exception as state_error:
            print(f"❌ State error: {state_error}")
            await message.reply(
                "❌ State xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
        
        print(f"🎉 PRO upgrade request completed successfully for user {user_id}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in PRO upgrade: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        await message.reply(
            "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
            reply_markup=settings_menu
        )


@sozlamalar_router.message(TokenStates.waiting_for_token)
async def handle_token_input(message: Message, state: FSMContext):
    """
    Handle token input from user
    """
    print(f"🔍 TOKEN INPUT RECEIVED from user {message.from_user.id}: {message.text}")
    
    try:
        user_id = message.from_user.id
        token = message.text.strip()
        print(f"📝 Processing token input from user {user_id}: {token}")
        
        # Check if user wants to cancel
        if token.lower() in ['/cancel', 'bekor', 'cancel']:
            print(f"❌ User {user_id} cancelled token input")
            await state.clear()
            await message.reply(
                "❌ Token kiritish bekor qilindi.",
                reply_markup=settings_menu
            )
            return
        
        # Validate token
        print(f"🔍 Validating token for user {user_id}")
        try:
            is_valid = db.validate_pro_token(token)
            print(f"✅ Token validation result for user {user_id}: {is_valid}")
        except Exception as db_error:
            print(f"❌ Database error validating token: {db_error}")
            await message.reply(
                "❌ Token tekshirishda xatolik. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
            await state.clear()
            return
        
        if is_valid:
            print(f"✅ Valid token for user {user_id}, upgrading to PRO")
            try:
                # Update user to pro plan
                db.update_user_plan(user_id, 'pro', token)
                print(f"🎉 User {user_id} upgraded to PRO with token: {token}")
                
                success_text = f"""✅ **PRO TARIF FAOL QILINDI!** ✅

🎉 **Tabriklaymiz!** Siz endi PRO tarifdan foydalanmoqdasiz!

💎 **PRO imkoniyatlari:**
• Cheksiz daromad/harajat qo'shish
• Batafsil hisobotlar va tahlil
• VIP qo'llab-quvvatlash
• Barcha funksiyalar

🔑 **Token:** {token}

🚀 Endi barcha funksiyalardan to'liq foydalaning!"""
                
                await message.reply(success_text, reply_markup=settings_menu, parse_mode="Markdown")
                await state.clear()
                print(f"✅ Success message sent to user {user_id}")
                
            except Exception as update_error:
                print(f"❌ Error updating user plan: {update_error}")
                await message.reply(
                    "❌ Tarif yangilashda xatolik. Qayta urinib ko'ring.",
                    reply_markup=settings_menu
                )
                await state.clear()
            
        else:
            # Invalid token - redirect to @Dier_ai
            print(f"❌ Invalid token for user {user_id}: {token}")
            invalid_text = f"""❌ **NOTO'G'RI TOKEN** ❌

🔑 Kiritilgan token noto'g'ri yoki ishlatilgan.

💡 **Yechim:**
@Dier_ai ga yozing va yangi token so'rang.

📞 **@Dier_ai ga yozish:**
1. @Dier_ai ni bosing
2. "Pro token kerak" deb yozing
3. Yangi token oling

🔄 Token olingandan keyin qayta urinib ko'ring."""
            
            # Create inline button to contact @Dier_ai
            contact_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📞 @Dier_ai ga yozish",
                            url="https://t.me/Dier_ai"
                        )
                    ]
                ]
            )
            
            await message.reply(invalid_text, reply_markup=contact_keyboard)
            print(f"✅ Invalid token message sent to user {user_id}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR in token input handler: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        await message.reply(
            f"❌ Token kiritishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )
        try:
            await state.clear()
            print("✅ State cleared after error")
        except Exception as clear_error:
            print(f"❌ Error clearing state: {clear_error}")


@sozlamalar_router.message(AdminTokenStates.waiting_for_admin_token)
async def handle_admin_token_input(message: Message, state: FSMContext):
    """
    Handle admin token input
    """
    print(f"🔍 ADMIN TOKEN INPUT from user {message.from_user.id}")
    
    try:
        # Get user ID and token
        user_id = message.from_user.id
        token = message.text.strip()
        print(f"📱 Processing admin token for user {user_id}: {token}")
        
        # Check if user wants to cancel
        if token.lower() in ['/cancel', 'cancel', 'bekor', 'отмена']:
            await state.clear()
            await message.reply(
                "❌ Admin token kiritish bekor qilindi.",
                reply_markup=settings_menu
            )
            return
        
        # Validate admin token
        print(f"🔍 Validating admin token: {token}")
        try:
            token_info = db.validate_admin_token(token)
            is_valid = token_info is not None
            print(f"📊 Admin token validation result: {is_valid}")
        except Exception as db_error:
            print(f"❌ Database error validating admin token: {db_error}")
            await message.reply(
                "❌ Database xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
            await state.clear()
            return
        
        if is_valid:
            print(f"✅ Valid admin token for user {user_id}, granting admin access")
            try:
                # Mark token as used
                db.use_admin_token(token, user_id)
                
                # Add user as admin
                db.add_admin(user_id, added_by=token_info[1], username=message.from_user.full_name)
                
                # Update user's admin status in Users table
                db.execute("UPDATE Users SET is_admin = TRUE WHERE id = ?", parameters=(user_id,), commit=True)
                
                success_text = f"""✅ **ADMIN HUQUQI BERILDI!** ✅

👑 **Tabriklaymiz!** Siz endi admin huquqiga egasiz!

🎯 **Admin imkoniyatlari:**
• 📢 Barcha foydalanuvchilarga reklama yuborish
• 👥 Foydalanuvchilarni boshqarish
• 👑 Adminlar qo'shish/olib tashlash
• 📊 Batafsil statistika
• 🔧 Bot sozlamalari

🚀 **Admin panelga kirish:** /admin

💡 **Eslatma:** Admin huquqi doimiy va bepul!"""
                
                await message.reply(success_text, reply_markup=settings_menu)
                await state.clear()
                print(f"✅ Admin access granted successfully to user {user_id}")
                
            except Exception as update_error:
                print(f"❌ Error granting admin access: {update_error}")
                await message.reply(
                    "❌ Admin huquqini berishda xatolik. Qayta urinib ko'ring.",
                    reply_markup=settings_menu
                )
                await state.clear()
            
        else:
            # Invalid token
            print(f"❌ Invalid admin token for user {user_id}: {token}")
            invalid_text = f"""❌ **NOTO'G'RI ADMIN TOKEN** ❌

🔍 **Kiritilgan token:** `{token}`

❌ **Xatolik sabablari:**
• Token noto'g'ri yoki mavjud emas
• Token allaqachon ishlatilgan
• Token faol emas

💡 **Yechim:**
Mavjud admin bilan bog'laning va yangi admin token so'rang.

📞 **Admin bilan bog'lanish:**
1. Mavjud adminni toping
2. "Admin token kerak" deb yozing
3. Yangi admin token oling

🔄 Token olingandan keyin qayta urinib ko'ring."""
            
            await message.reply(invalid_text, reply_markup=settings_menu)
            print(f"✅ Invalid admin token message sent to user {user_id}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR in admin token input handler: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        await message.reply(
            f"❌ Admin token kiritishda xatolik: {str(e)}",
            reply_markup=settings_menu
        )
        try:
            await state.clear()
            print("✅ State cleared after error")
        except Exception as clear_error:
            print(f"❌ Error clearing state: {clear_error}")


@sozlamalar_router.message(F.text == "🔙 Asosiy menyu")
@sozlamalar_router.message(F.text == "🔙 Sozlamalar")
async def back_to_main(message: Message):
    """
    Return to main menu or settings
    """
    if message.text == "🔙 Asosiy menyu":
        await message.reply(
            "🏠 Asosiy menyuga qaytdingiz",
            reply_markup=main_menu
        )
    else:
        await show_settings(message)


@sozlamalar_router.callback_query(F.data == "upgrade_to_pro")
async def handle_upgrade_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle PRO upgrade callback from limit message
    """
    print(f"🔍 PRO UPGRADE CALLBACK from user {callback.from_user.id}")
    
    try:
        # Get user ID
        user_id = callback.from_user.id
        print(f"📱 Processing upgrade callback for user {user_id}")
        
        # Check if user already has pro
        try:
            plan, _ = db.get_user_plan(user_id)
            print(f"📊 User {user_id} current plan: {plan}")
        except Exception as db_error:
            print(f"❌ Database error getting user plan: {db_error}")
            await callback.message.reply(
                "❌ Database xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
            return
        
        if plan == 'pro':
            print(f"ℹ️ User {user_id} already has PRO plan")
            await callback.message.reply(
                "✅ Siz allaqachon PRO tarifdan foydalanmoqdasiz!",
                reply_markup=settings_menu
            )
            return
        
        # Show token input instructions
        print(f"🔑 Showing token input for user {user_id}")
        token_text = """🔑 **PRO TOKEN KIRITISH** 🔑

Pro tarif olish uchun token kerak.

📝 **Token qanday olish:**
1. @Dier_ai ga yozing
2. "Pro token kerak" deb yozing
3. Token oling va bu yerga kiriting

💡 **Token kiritish:**
Tokenni matn ko'rinishida yuboring (masalan: PRO123456789)

❌ **Bekor qilish:** /cancel"""
        
        await callback.message.reply(token_text, reply_markup=settings_menu)
        
        # Set state to wait for token
        try:
            await state.set_state(TokenStates.waiting_for_token)
            print(f"✅ State set to waiting_for_token for user {user_id}")
        except Exception as state_error:
            print(f"❌ State error: {state_error}")
            await callback.message.reply(
                "❌ State xatoligi. Qayta urinib ko'ring.",
                reply_markup=settings_menu
            )
        
        # Answer the callback query
        await callback.answer()
        print(f"🎉 PRO upgrade callback completed successfully for user {user_id}")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in PRO upgrade callback: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        await callback.message.reply(
            "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
            reply_markup=settings_menu
        )
        await callback.answer()
