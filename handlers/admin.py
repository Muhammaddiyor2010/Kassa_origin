from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loader import db, bot
from keyboards.keyboards import main_menu
import asyncio

admin_router: Router = Router()

# States for admin actions
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_admin_id = State()

# Admin panel keyboard
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📊 Statistika"),
            KeyboardButton(text="👥 Foydalanuvchilar")
        ],
        [
            KeyboardButton(text="📢 Reklama yuborish"),
            KeyboardButton(text="👑 Adminlar")
        ],
        [
            KeyboardButton(text="🔑 Admin Tokenlar"),
            KeyboardButton(text="💎 PRO Tokenlar")
        ],
        [
            KeyboardButton(text="🧪 Test Callback"),
            KeyboardButton(text="🔙 Asosiy menyu")
        ]
    ],
    resize_keyboard=True,
    persistent=True
)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return db.is_admin(user_id)

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    """
    Show admin panel
    """
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    # Get statistics
    total_users = db.get_user_count()
    pro_users = db.get_pro_user_count()
    free_users = db.get_free_user_count()
    total_admins = len(db.get_all_admins())
    
    stats_text = f"""👑 **ADMIN PANEL** 👑

📊 **Statistika:**
• Jami foydalanuvchilar: {total_users}
• PRO foydalanuvchilar: {pro_users}
• TEKIN foydalanuvchilar: {free_users}
• Adminlar soni: {total_admins}

🔧 **Admin funksiyalari:**
• Foydalanuvchilarni boshqarish
• Reklama yuborish
• Adminlar qo'shish/o'chirish
• Statistika ko'rish

Quyidagi tugmalardan foydalaning:"""
    
    await message.reply(stats_text, reply_markup=admin_menu, parse_mode="Markdown")

@admin_router.message(F.text == "📊 Statistika")
async def show_admin_stats(message: Message):
    """
    Show detailed statistics
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    # Get detailed statistics
    total_users = db.get_user_count()
    pro_users = db.get_pro_user_count()
    free_users = db.get_free_user_count()
    total_admins = len(db.get_all_admins())
    
    # Get recent users (last 10)
    all_users = db.get_all_users()
    recent_users = all_users[:10] if all_users else []
    
    # Calculate percentages
    pro_percentage = (pro_users/total_users*100) if total_users > 0 else 0
    free_percentage = (free_users/total_users*100) if total_users > 0 else 0
    
    stats_text = f"""📊 **BATAFSIL STATISTIKA** 📊

👥 **Foydalanuvchilar:**
• Jami: {total_users}
• PRO: {pro_users} ({pro_percentage:.1f}%)
• TEKIN: {free_users} ({free_percentage:.1f}%)

👑 **Adminlar:** {total_admins}

📈 **So'ngi foydalanuvchilar:**
"""
    
    if recent_users:
        for i, user in enumerate(recent_users, 1):
            user_id, name, phone, language, plan, is_admin_flag, start_count = user
            plan_emoji = "💎" if plan == 'pro' else "🆓"
            admin_emoji = "👑" if is_admin_flag else ""
            stats_text += f"{i}. {admin_emoji} {name} {plan_emoji} (ID: {user_id})\n"
    else:
        stats_text += "• Foydalanuvchilar yo'q"
    
    await message.reply(stats_text, reply_markup=admin_menu, parse_mode="Markdown")

@admin_router.message(F.text == "👥 Foydalanuvchilar")
async def show_users(message: Message):
    """
    Show users management
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    all_users = db.get_all_users()
    
    if not all_users:
        await message.reply("❌ Foydalanuvchilar topilmadi!", reply_markup=admin_menu)
        return
    
    # Create inline keyboard for user management
    keyboard_buttons = []
    for user in all_users[:20]:  # Show first 20 users
        user_id, name, phone, language, plan, is_admin_flag, start_count = user
        plan_emoji = "💎" if plan == 'pro' else "🆓"
        admin_emoji = "👑" if is_admin_flag else ""
        button_text = f"{admin_emoji} {name[:15]} {plan_emoji}"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"user_info_{user_id}"
            )
        ])
    
    # Add navigation buttons
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="refresh_users"),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_admin")
    ])
    
    users_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    users_text = f"""👥 **FOYDALANUVCHILAR BOSHQARUVI** 👥

📊 **Jami foydalanuvchilar:** {len(all_users)}

🔍 **Foydalanuvchi tanlang:**
(So'ngi 20 ta ko'rsatilmoqda)"""
    
    await message.reply(users_text, reply_markup=users_keyboard, parse_mode="Markdown")

@admin_router.callback_query(F.data.startswith("user_info_"))
async def show_user_info(callback: CallbackQuery):
    """
    Show detailed user information
    """
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    user_id = int(callback.data.split("_")[2])
    user_info = db.select_user(id=user_id)
    
    if not user_info:
        await callback.answer("❌ Foydalanuvchi topilmadi!")
        return
    
    # Get user's income and expenses
    income_data = db.get_user_kirim(user_id)
    expenses_data = db.get_user_chiqim(user_id)
    plan, pro_token = db.get_user_plan(user_id)
    
    user_text = f"""👤 **FOYDALANUVCHI MA'LUMOTLARI** 👤

🆔 **ID:** {user_id}
👤 **Ism:** {user_info[1]}
📞 **Telefon:** {user_info[3] or 'Kiritilmagan'}
🌐 **Til:** {user_info[2] or 'uz'}
💎 **Tarif:** {'PRO' if plan == 'pro' else 'TEKIN'}
👑 **Admin:** {'Ha' if db.is_admin(user_id) else 'Yoq'}
🚀 **Start soni:** {user_info[6] if len(user_info) > 6 else 0}

📊 **Statistika:**
• Daromadlar: {len(income_data) if income_data else 0} ta
• Harajatlar: {len(expenses_data) if expenses_data else 0} ta

🔑 **Pro Token:** {pro_token[:8] + '...' + pro_token[-4:] if pro_token and len(pro_token) > 12 else pro_token or 'Yoq'}"""
    
    # Create action buttons
    action_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 PRO qilish" if plan != 'pro' else "🆓 TEKIN qilish",
                    callback_data=f"toggle_plan_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👑 Admin qilish" if not db.is_admin(user_id) else "👤 Admin o'chirish",
                    callback_data=f"toggle_admin_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_users")
            ]
        ]
    )
    
    await callback.message.edit_text(user_text, reply_markup=action_keyboard, parse_mode="Markdown")
    await callback.answer()

@admin_router.callback_query(F.data.startswith("toggle_plan_"))
async def toggle_user_plan(callback: CallbackQuery):
    """
    Toggle user plan between free and pro
    """
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    user_id = int(callback.data.split("_")[2])
    current_plan, _ = db.get_user_plan(user_id)
    new_plan = 'free' if current_plan == 'pro' else 'pro'
    
    # Update user plan
    db.update_user_plan(user_id, new_plan)
    
    plan_text = "PRO" if new_plan == 'pro' else "TEKIN"
    await callback.answer(f"✅ Foydalanuvchi {plan_text} tarifga o'tkazildi!")
    
    # Refresh user info
    await show_user_info(callback)

@admin_router.callback_query(F.data.startswith("toggle_admin_"))
async def toggle_user_admin(callback: CallbackQuery):
    """
    Toggle user admin status
    """
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    user_id = int(callback.data.split("_")[2])
    is_admin_user = db.is_admin(user_id)
    
    if is_admin_user:
        # Remove admin
        db.remove_admin(user_id)
        await callback.answer("✅ Admin huquqi olib tashlandi!")
    else:
        # Add admin
        user_info = db.select_user(id=user_id)
        username = user_info[1] if user_info else "Unknown"
        db.add_admin(user_id, added_by=callback.from_user.id, username=username)
        await callback.answer("✅ Admin huquqi berildi!")
    
    # Refresh user info
    await show_user_info(callback)

@admin_router.message(F.text == "📢 Reklama yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    """
    Start broadcast message process
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    await message.reply(
        "📢 **REKLAMA YUBORISH** 📢\n\n"
        "Reklama matnini yuboring:\n"
        "(Rasm, video, matn - hammasi qabul qilinadi)\n\n"
        "❌ **Bekor qilish:** /cancel",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
            resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    
    await state.set_state(AdminStates.waiting_for_broadcast)

@admin_router.message(AdminStates.waiting_for_broadcast, F.text.in_(["✅ Tasdiqlash", "/confirm"]))
async def confirm_broadcast(message: Message, state: FSMContext):
    """
    Confirm and start broadcasting
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        await state.clear()
        return
    
    data = await state.get_data()
    broadcast_message = data.get('broadcast_message')
    user_count = data.get('user_count', 0)
    
    if not broadcast_message:
        await message.reply("❌ Xatolik! Qayta urinib ko'ring.", reply_markup=admin_menu)
        await state.clear()
        return
    
    await message.reply(
        f"🚀 **REKLAMA YUBORILMOQDA...** 🚀\n\n"
        f"📊 Foydalanuvchilar: {user_count}\n"
        f"⏱️ Taxminiy vaqt: {user_count * 5} soniya\n\n"
        f"📱 Xabarlar 5 soniya interval bilan yuboriladi...",
        reply_markup=admin_menu,
        parse_mode="Markdown"
    )
    
    # Start broadcasting
    success_count = 0
    error_count = 0
    error_details = []
    
    for i, user in enumerate(db.get_all_users()):
        user_id = user[0]
        user_name = user[1] if len(user) > 1 else f"User {user_id}"
        
        try:
            # Copy the original message
            if broadcast_message.text:
                await bot.send_message(user_id, broadcast_message.text)
            elif broadcast_message.photo:
                await bot.send_photo(user_id, broadcast_message.photo[-1].file_id, caption=broadcast_message.caption)
            elif broadcast_message.video:
                await bot.send_video(user_id, broadcast_message.video.file_id, caption=broadcast_message.caption)
            elif broadcast_message.document:
                await bot.send_document(user_id, broadcast_message.document.file_id, caption=broadcast_message.caption)
            else:
                await bot.send_message(user_id, "📢 Reklama xabari")
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            error_msg = str(e)
            error_details.append(f"• {user_name} (ID: {user_id}): {error_msg}")
            print(f"Error sending to user {user_id}: {e}")
        
        # Wait 5 seconds between messages
        if i < user_count - 1:  # Don't wait after the last message
            await asyncio.sleep(5)
    
    # Create back to admin panel button
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Admin panelga qaytish",
                    callback_data="back_to_admin_panel"
                )
            ]
        ]
    )
    
    # Send final report
    if error_count > 0:
        # Send detailed error report to admin
        error_report = f"⚠️ **REKLAMA XATOLIKLARI** ⚠️\n\n"
        error_report += f"📊 **Xatolik hisoboti:**\n"
        error_report += f"• Muvaffaqiyatli: {success_count}\n"
        error_report += f"• Xatolik: {error_count}\n"
        error_report += f"• Jami: {user_count}\n\n"
        error_report += f"❌ **Xatolik tafsilotlari:**\n"
        
        # Add error details (limit to first 10 errors to avoid message too long)
        for error_detail in error_details[:10]:
            error_report += f"{error_detail}\n"
        
        if len(error_details) > 10:
            error_report += f"\n... va yana {len(error_details) - 10} ta xatolik"
        
        error_report += f"\n\n💡 **Maslahat:**\n"
        error_report += f"• Foydalanuvchilar botni bloklagan bo'lishi mumkin\n"
        error_report += f"• Yaroqsiz foydalanuvchi ID lari\n"
        error_report += f"• Internet aloqasi muammolari"
        
        # Send error report to admin
        await message.reply(error_report, parse_mode="Markdown")
    
    # Send main completion report
    completion_text = f"✅ **REKLAMA YUBORILDI!** ✅\n\n"
    completion_text += f"📊 **Natija:**\n"
    completion_text += f"• Muvaffaqiyatli: {success_count}\n"
    completion_text += f"• Xatolik: {error_count}\n"
    completion_text += f"• Jami: {user_count}\n\n"
    
    if error_count == 0:
        completion_text += f"🎉 Reklama muvaffaqiyatli yuborildi!"
    else:
        completion_text += f"⚠️ Reklama yuborildi, lekin {error_count} ta xatolik yuz berdi.\n"
        completion_text += f"Xatolik tafsilotlari yuqorida ko'rsatilgan."
    
    await message.reply(
        completion_text,
        reply_markup=back_keyboard,
        parse_mode="Markdown"
    )
    
    await state.clear()

@admin_router.message(AdminStates.waiting_for_broadcast, F.text.in_(["❌ Bekor qilish", "/cancel"]))
async def cancel_broadcast(message: Message, state: FSMContext):
    """
    Cancel broadcast
    """
    await state.clear()
    await message.reply("❌ Reklama yuborish bekor qilindi.", reply_markup=admin_menu)

@admin_router.message(AdminStates.waiting_for_broadcast, F.text.in_(["📊 Statistika", "👥 Foydalanuvchilar", "👑 Adminlar", "🔙 Asosiy menyu"]))
async def return_to_admin_from_broadcast(message: Message, state: FSMContext):
    """
    Return to admin panel from broadcast state
    """
    await state.clear()
    
    if message.text == "📊 Statistika":
        await show_admin_stats(message)
    elif message.text == "👥 Foydalanuvchilar":
        await show_users(message)
    elif message.text == "👑 Adminlar":
        await show_admins(message)
    elif message.text == "🔙 Asosiy menyu":
        await back_to_main_from_admin(message)

@admin_router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    """
    Process and send broadcast message
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        await state.clear()
        return
    
    # Get all users
    try:
        all_users = db.get_all_users()
        
        if not all_users:
            await message.reply("❌ Foydalanuvchilar topilmadi!", reply_markup=admin_menu)
            await state.clear()
            return
            
    except Exception as e:
        await message.reply(
            f"❌ **XATOLIK!** ❌\n\n"
            f"Foydalanuvchilar ro'yxatini olishda xatolik yuz berdi:\n"
            f"`{str(e)}`\n\n"
            f"💡 **Maslahat:**\n"
            f"• Database bilan bog'lanishni tekshiring\n"
            f"• Qayta urinib ko'ring",
            reply_markup=admin_menu,
            parse_mode="Markdown"
        )
        await state.clear()
        return
    
    # Send confirmation
    await message.reply(
        f"📢 **REKLAMA TASDIQLASH** 📢\n\n"
        f"📊 **Ma'lumot:**\n"
        f"• Foydalanuvchilar soni: {len(all_users)}\n"
        f"• Yuborish vaqti: ~{len(all_users) * 5} soniya\n\n"
        f"✅ **Tasdiqlash:** /confirm\n"
        f"❌ **Bekor qilish:** /cancel",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Tasdiqlash")],
                [KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    
    # Store message for broadcasting
    await state.update_data(broadcast_message=message, user_count=len(all_users))
    await state.set_state(AdminStates.waiting_for_broadcast)

@admin_router.callback_query(F.data == "back_to_admin_panel")
async def back_to_admin_panel_from_broadcast(callback: CallbackQuery):
    """
    Return to admin panel from broadcast completion
    """
    await callback.answer("🏠 Admin panelga qaytdingiz")
    
    # Get statistics for admin panel
    user_id = callback.from_user.id
    total_users = db.get_user_count()
    pro_users = db.get_pro_user_count()
    free_users = db.get_free_user_count()
    total_admins = len(db.get_all_admins())
    
    stats_text = f"""👑 **ADMIN PANEL** 👑

📊 **Statistika:**
• Jami foydalanuvchilar: {total_users}
• PRO foydalanuvchilar: {pro_users}
• TEKIN foydalanuvchilar: {free_users}
• Adminlar soni: {total_admins}

🔧 **Admin funksiyalari:**
• Foydalanuvchilarni boshqarish
• Reklama yuborish
• Adminlar qo'shish/o'chirish
• Statistika ko'rish

Quyidagi tugmalardan foydalaning:"""
    
    await callback.message.edit_text(stats_text, reply_markup=None, parse_mode="Markdown")
    await callback.message.reply("Admin panel", reply_markup=admin_menu)


@admin_router.message(F.text == "🔑 Admin Tokenlar")
async def show_admin_tokens(message: Message):
    """
    Show admin token management
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    try:
        # Get all admin tokens
        tokens = db.get_all_admin_tokens()
        
        if not tokens:
            tokens_text = """🔑 **ADMIN TOKENLAR** 🔑

📝 **Hozircha admin tokenlar yo'q.**

➕ **Yangi admin token yaratish:**
1. "Yangi token yaratish" tugmasini bosing
2. Token nomini kiriting
3. Token yaratiladi va foydalanishga tayyor bo'ladi

💡 **Admin token nima?**
Admin token - bu yangi adminlar qo'shish uchun maxsus kod.
Har bir token faqat bir marta ishlatiladi."""
            
            # Create inline keyboard for creating new token
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            token_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="➕ Yangi token yaratish",
                            callback_data="create_admin_token"
                        )
                    ]
                ]
            )
            print(f"🔧 Created inline keyboard for empty tokens with callback_data: create_admin_token")
            
            await message.reply(tokens_text, reply_markup=token_keyboard, parse_mode="Markdown")
            print(f"📤 Empty tokens message sent to user {message.from_user.id}")
            return
        
        # Format tokens list
        tokens_text = "🔑 **ADMIN TOKENLAR** 🔑\n\n"
        
        for i, token in enumerate(tokens, 1):
            token_name, created_by, used_by, used_at, created_at, is_active = token
            
            status = "✅ Faol" if is_active and used_by is None else "❌ Ishlatilgan" if used_by else "❌ Faol emas"
            used_info = f" (Ishlatgan: {used_by})" if used_by else ""
            
            tokens_text += f"{i}. **{token_name}**\n"
            tokens_text += f"   📅 Yaratilgan: {created_at}\n"
            tokens_text += f"   👤 Yaratgan: {created_by}\n"
            tokens_text += f"   📊 Holat: {status}{used_info}\n\n"
        
        tokens_text += "💡 **Token yaratish:** Yangi admin token yaratish uchun tugmani bosing."
        
        # Create inline keyboard
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        token_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Yangi token yaratish",
                        callback_data="create_admin_token"
                    )
                ]
            ]
        )
        print(f"🔧 Created inline keyboard with callback_data: create_admin_token")
        
        await message.reply(tokens_text, reply_markup=token_keyboard, parse_mode="Markdown")
        print(f"📤 Admin tokens message sent to user {message.from_user.id}")
        
    except Exception as e:
        print(f"Error showing admin tokens: {e}")
        error_message = f"❌ Admin tokenlarni ko'rsatishda xatolik: {str(e)}"
        await message.reply(error_message)
        
        # Send error notification to main admin
        try:
            main_admin_id = 7231910736
            await bot.send_message(
                main_admin_id,
                f"🚨 **ADMIN TOKEN KO'RSATISH XATOLIK** 🚨\n\n"
                f"👤 **Foydalanuvchi:** {message.from_user.id}\n"
                f"📝 **Xatolik:** {str(e)}\n"
                f"⏰ **Vaqt:** {asyncio.get_event_loop().time()}\n\n"
                f"🔧 **Yechim:** Admin token ko'rsatish tizimini tekshiring"
            )
            print(f"✅ Error notification sent to main admin {main_admin_id}")
        except Exception as notify_error:
            print(f"❌ Failed to send error notification: {notify_error}")


@admin_router.message(F.text == "💎 PRO Tokenlar")
async def show_pro_tokens(message: Message):
    """
    Show PRO token management
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    try:
        # Get all PRO tokens
        tokens = db.get_all_pro_tokens()
        
        if not tokens:
            tokens_text = """💎 **PRO TOKENLAR** 💎

📝 **Hozircha PRO tokenlar yo'q.**

➕ **Yangi PRO token yaratish:**
1. "Yangi PRO token yaratish" tugmasini bosing
2. Token nomini kiriting
3. Token yaratiladi va foydalanishga tayyor bo'ladi

💡 **PRO token nima?**
PRO token - bu foydalanuvchilarga PRO tarif berish uchun maxsus kod.
Har bir token faqat bir marta ishlatiladi."""
            
            # Create inline keyboard for creating new PRO token
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            token_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="➕ Yangi PRO token yaratish",
                            callback_data="create_pro_token"
                        )
                    ]
                ]
            )
            
            await message.reply(tokens_text, reply_markup=token_keyboard, parse_mode="Markdown")
            return
        
        # Format tokens list
        tokens_text = "💎 **PRO TOKENLAR** 💎\n\n"
        
        for i, token in enumerate(tokens, 1):
            token_name, created_by, used_by, used_at, created_at, is_active = token
            
            status = "✅ Faol" if is_active and used_by is None else "❌ Ishlatilgan" if used_by else "❌ Faol emas"
            used_info = f" (Ishlatgan: {used_by})" if used_by else ""
            
            tokens_text += f"{i}. **{token_name}**\n"
            tokens_text += f"   📅 Yaratilgan: {created_at}\n"
            tokens_text += f"   👤 Yaratgan: {created_by}\n"
            tokens_text += f"   📊 Holat: {status}{used_info}\n\n"
        
        tokens_text += "💡 **Token yaratish:** Yangi PRO token yaratish uchun tugmani bosing."
        
        # Create inline keyboard
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        token_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Yangi PRO token yaratish",
                        callback_data="create_pro_token"
                    )
                ]
            ]
        )
        print(f"🔧 Created PRO token inline keyboard with callback_data: create_pro_token")
        
        await message.reply(tokens_text, reply_markup=token_keyboard, parse_mode="Markdown")
        print(f"📤 PRO tokens message sent to user {message.from_user.id}")
        
    except Exception as e:
        print(f"Error showing PRO tokens: {e}")
        error_message = f"❌ PRO tokenlarni ko'rsatishda xatolik: {str(e)}"
        await message.reply(error_message)
        
        # Send error notification to main admin
        try:
            main_admin_id = 7231910736
            await bot.send_message(
                main_admin_id,
                f"🚨 **PRO TOKEN KO'RSATISH XATOLIK** 🚨\n\n"
                f"👤 **Foydalanuvchi:** {message.from_user.id}\n"
                f"📝 **Xatolik:** {str(e)}\n"
                f"⏰ **Vaqt:** {asyncio.get_event_loop().time()}\n\n"
                f"🔧 **Yechim:** PRO token ko'rsatish tizimini tekshiring"
            )
            print(f"✅ Error notification sent to main admin {main_admin_id}")
        except Exception as notify_error:
            print(f"❌ Failed to send error notification: {notify_error}")


@admin_router.callback_query(F.data == "create_pro_token")
async def create_pro_token_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle PRO token creation callback
    """
    print(f"🔍 PRO TOKEN CALLBACK TRIGGERED by user {callback.from_user.id}")
    print(f"🔍 Callback data: {callback.data}")
    
    if not is_admin(callback.from_user.id):
        print(f"❌ User {callback.from_user.id} is not admin")
        await callback.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    print(f"✅ User {callback.from_user.id} is admin, proceeding with PRO token creation")
    
    try:
        # Generate a random PRO token
        import random
        import string
        
        # Create a random token
        token_length = 12
        token = 'PRO' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=token_length))
        print(f"🔑 Generated PRO token: {token}")
        
        # Add token to database
        print(f"💾 Adding PRO token to database for user {callback.from_user.id}")
        db.add_pro_token(token, callback.from_user.id)
        print(f"✅ PRO token added to database successfully")
        
        success_text = f"""✅ **PRO TOKEN YARATILDI!** ✅

💎 **Yangi PRO token:**
`{token}`

📝 **Token haqida:**
• Bu token foydalanuvchilarga PRO tarif berish uchun ishlatiladi
• Faqat bir marta ishlatiladi
• Tokenni xavfsiz joyda saqlang

👥 **Tokenni ishlatish:**
1. Foydalanuvchi /sozlamalar → 💎 PRO olish
2. Token kiritadi: `{token}`
3. PRO tarif beriladi

⚠️ **Eslatma:** Tokenni faqat ishonchli odamlarga bering!"""
        
        print(f"📤 Sending PRO token success message to user {callback.from_user.id}")
        await callback.message.edit_text(success_text, parse_mode="Markdown")
        await callback.answer("✅ PRO token yaratildi!")
        print(f"✅ PRO token success message sent successfully")
        
    except Exception as e:
        print(f"Error creating PRO token: {e}")
        error_message = f"❌ PRO token yaratishda xatolik: {str(e)}"
        await callback.message.edit_text(error_message)
        await callback.answer("❌ Xatolik yuz berdi!")
        
        # Send error notification to main admin
        try:
            main_admin_id = 7231910736
            await bot.send_message(
                main_admin_id,
                f"🚨 **PRO TOKEN XATOLIK** 🚨\n\n"
                f"👤 **Foydalanuvchi:** {callback.from_user.id}\n"
                f"📝 **Xatolik:** {str(e)}\n"
                f"⏰ **Vaqt:** {asyncio.get_event_loop().time()}\n\n"
                f"🔧 **Yechim:** PRO token yaratish tizimini tekshiring"
            )
            print(f"✅ Error notification sent to main admin {main_admin_id}")
        except Exception as notify_error:
            print(f"❌ Failed to send error notification: {notify_error}")


@admin_router.message(F.text == "🧪 Test Callback")
async def test_callback_button(message: Message):
    """
    Test callback button handler
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    try:
        test_text = """🧪 **CALLBACK TEST** 🧪

Bu tugma callback ishlayotganini tekshirish uchun.

📝 **Test jarayoni:**
1. Quyidagi tugmani bosing
2. Agar callback ishlayotgan bo'lsa, xabar ko'rsatiladi
3. Agar ishlamayotgan bo'lsa, hech narsa bo'lmaydi

🔧 **Debug ma'lumotlari:**
• Foydalanuvchi ID: {user_id}
• Vaqt: {time}
• Callback data: test_callback"""
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        test_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🧪 Test Callback",
                        callback_data="test_callback"
                    )
                ]
            ]
        )
        
        await message.reply(test_text.format(
            user_id=message.from_user.id,
            time=asyncio.get_event_loop().time()
        ), reply_markup=test_keyboard, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error in test callback button: {e}")
        await message.reply(f"❌ Test callback tugmasida xatolik: {str(e)}")

@admin_router.message(F.text == "👑 Adminlar")
async def show_admins(message: Message):
    """
    Show all admins
    """
    if not is_admin(message.from_user.id):
        await message.reply("❌ Sizda admin huquqi yo'q!")
        return
    
    try:
        # Get all admins
        admins = db.get_all_admins()
        
        if not admins:
            await message.reply("❌ Adminlar topilmadi.")
            return
        
        admins_text = "👑 **ADMINLAR RO'YXATI** 👑\n\n"
        
        for i, admin in enumerate(admins, 1):
            user_id, name, username, created_at = admin
            admins_text += f"{i}. **{name}**\n"
            admins_text += f"   🆔 ID: `{user_id}`\n"
            admins_text += f"   👤 Username: @{username or 'Yoq'}\n"
            admins_text += f"   📅 Qo'shilgan: {created_at}\n\n"
        
        await message.reply(admins_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error showing admins: {e}")
        await message.reply(f"❌ Adminlarni ko'rsatishda xatolik: {str(e)}")


@admin_router.callback_query(F.data == "test_callback")
async def test_callback_handler(callback: CallbackQuery):
    """
    Test callback handler to check if callbacks work
    """
    print(f"🔍 TEST CALLBACK TRIGGERED by user {callback.from_user.id}")
    await callback.answer("✅ Test callback ishlaydi!")
    await callback.message.edit_text("✅ Callback ishlaydi! Endi token yaratishni sinab ko'ring.")

@admin_router.callback_query(F.data == "create_admin_token")
async def create_admin_token_callback(callback: CallbackQuery, state: FSMContext):
    """
    Handle admin token creation callback
    """
    print(f"🔍 ADMIN TOKEN CALLBACK TRIGGERED by user {callback.from_user.id}")
    print(f"🔍 Callback data: {callback.data}")
    
    if not is_admin(callback.from_user.id):
        print(f"❌ User {callback.from_user.id} is not admin")
        await callback.answer("❌ Sizda admin huquqi yo'q!")
        return
    
    print(f"✅ User {callback.from_user.id} is admin, proceeding with token creation")
    
    try:
        # Generate a random admin token
        import random
        import string
        
        # Create a random token
        token_length = 12
        token = 'ADMIN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=token_length))
        print(f"🔑 Generated token: {token}")
        
        # Add token to database
        print(f"💾 Adding token to database for user {callback.from_user.id}")
        db.add_admin_token(token, callback.from_user.id)
        print(f"✅ Token added to database successfully")
        
        success_text = f"""✅ **ADMIN TOKEN YARATILDI!** ✅

🔑 **Yangi admin token:**
`{token}`

📝 **Token haqida:**
• Bu token yangi admin qo'shish uchun ishlatiladi
• Faqat bir marta ishlatiladi
• Tokenni xavfsiz joyda saqlang

👥 **Tokenni ishlatish:**
1. Foydalanuvchi /sozlamalar → 👑 Admin olish
2. Token kiritadi: `{token}`
3. Admin huquqi beriladi

⚠️ **Eslatma:** Tokenni faqat ishonchli odamlarga bering!"""
        
        print(f"📤 Sending success message to user {callback.from_user.id}")
        await callback.message.edit_text(success_text, parse_mode="Markdown")
        await callback.answer("✅ Admin token yaratildi!")
        print(f"✅ Success message sent successfully")
        
    except Exception as e:
        print(f"Error creating admin token: {e}")
        error_message = f"❌ Admin token yaratishda xatolik: {str(e)}"
        await callback.message.edit_text(error_message)
        await callback.answer("❌ Xatolik yuz berdi!")
        
        # Send error notification to main admin
        try:
            main_admin_id = 7231910736
            await bot.send_message(
                main_admin_id,
                f"🚨 **ADMIN TOKEN XATOLIK** 🚨\n\n"
                f"👤 **Foydalanuvchi:** {callback.from_user.id}\n"
                f"📝 **Xatolik:** {str(e)}\n"
                f"⏰ **Vaqt:** {asyncio.get_event_loop().time()}\n\n"
                f"🔧 **Yechim:** Token yaratish tizimini tekshiring"
            )
            print(f"✅ Error notification sent to main admin {main_admin_id}")
        except Exception as notify_error:
            print(f"❌ Failed to send error notification: {notify_error}")
