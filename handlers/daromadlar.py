from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from loader import db
from keyboards.keyboards import main_menu

daromadlar_router: Router = Router()


@daromadlar_router.message(Command("daromadlarim"))
@daromadlar_router.message(F.text == "💰 Daromadlari")
async def show_income(message: Message):
    """
    Show user's income
    """
    try:
        user_id = message.from_user.id
        
        # Get user's income from database
        income = db.get_user_kirim(user_id)
        
        if not income:
            await message.reply(
                "📝 Sizda hali daromadlar yo'q.\n\n"
                "Daromad qo'shish uchun:\n"
                "• Matnli xabar yuboring: 'Ish haqim 2000000 so'm oldim'\n"
                "• Ovozli xabar yuboring\n"
                "• Tugmalardan foydalaning",
                reply_markup=main_menu
            )
            return
        
        # Format income for display
        total_income = 0
        income_text = "💰 Sizning daromadlaringiz:\n\n"
        
        for i, inc in enumerate(income, 1):
            income_id, summa, izoh, kategoriya, user_id_db = inc
            
            # Parse summa (it might be string)
            try:
                amount = int(summa.replace(' ', '').replace(',', ''))
                total_income += amount
            except (ValueError, AttributeError):
                amount = 0
            
            # Format the income entry
            income_text += f"📌 #{i}\n"
            income_text += f"💵 Summa: {summa} so'm\n"
            income_text += f"📂 Kategoriya: {kategoriya}\n"
            income_text += f"📝 Izoh: {izoh or 'Izoh yoq'}\n"
            income_text += f"🆔 ID: {income_id}\n"
            income_text += "─" * 30 + "\n\n"
        
        # Add total at the end
        income_text += f"💰 Jami daromad: {total_income:,} so'm"
        
        # Split message if too long (Telegram limit is 4096 characters)
        if len(income_text) > 4000:
            # Send in chunks
            chunks = []
            current_chunk = "💰 Sizning daromadlaringiz:\n\n"
            
            for i, inc in enumerate(income, 1):
                income_id, summa, izoh, kategoriya, user_id_db = inc
                
                income_entry = f"📌 #{i}\n"
                income_entry += f"💵 Summa: {summa} so'm\n"
                income_entry += f"📂 Kategoriya: {kategoriya}\n"
                income_entry += f"📝 Izoh: {izoh or 'Izoh yoq'}\n"
                income_entry += "─" * 20 + "\n\n"
                
                if len(current_chunk + income_entry) > 3800:
                    chunks.append(current_chunk)
                    current_chunk = f"💰 Daromadlaringiz (davomi) - #{i}-{len(income)}:\n\n"
                
                current_chunk += income_entry
            
            # Add total to last chunk
            current_chunk += f"💰 Jami daromad: {total_income:,} so'm"
            chunks.append(current_chunk)
            
            # Send all chunks
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await message.reply(chunk, reply_markup=main_menu)
                else:
                    await message.reply(chunk)
        else:
            await message.reply(income_text, reply_markup=main_menu)
            
    except Exception as e:
        print(f"Error showing income: {e}")
        await message.reply(
            f"❌ Xatolik yuz berdi: {str(e)}\n\n"
            "Iltimos, qayta urinib ko'ring yoki admin bilan bog'laning.",
            reply_markup=main_menu
        )
