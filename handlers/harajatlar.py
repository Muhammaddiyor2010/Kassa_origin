from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from loader import db
from keyboards.keyboards import main_menu

harajatlar_router: Router = Router()


@harajatlar_router.message(Command("harajatlarim"))
@harajatlar_router.message(F.text == "💸 Harajatlari")
async def show_expenses(message: Message):
    """
    Show user's expenses
    """
    try:
        user_id = message.from_user.id
        
        # Get user's expenses from database
        expenses = db.get_user_chiqim(user_id)
        
        if not expenses:
            await message.reply(
                "📝 Sizda hali harajatlar yo'q.\n\n"
                "Harajat qo'shish uchun:\n"
                "• Matnli xabar yuboring: 'Ovqat uchun 50000 so'm sarf qildim'\n"
                "• Ovozli xabar yuboring\n"
                "• Tugmalardan foydalaning",
                reply_markup=main_menu
            )
            return
        
        # Format expenses for display
        total_expenses = 0
        expenses_text = "💸 Sizning harajatlaringiz:\n\n"
        
        for i, expense in enumerate(expenses, 1):
            expense_id, summa, izoh, kategoriya, user_id_db = expense
            
            # Parse summa (it might be string)
            try:
                amount = int(summa.replace(' ', '').replace(',', ''))
                total_expenses += amount
            except (ValueError, AttributeError):
                amount = 0
            
            # Format the expense entry
            expenses_text += f"📌 #{i}\n"
            expenses_text += f"💵 Summa: {summa} so'm\n"
            expenses_text += f"📂 Kategoriya: {kategoriya}\n"
            expenses_text += f"📝 Izoh: {izoh or 'Izoh yoq'}\n"
            expenses_text += f"🆔 ID: {expense_id}\n"
            expenses_text += "─" * 30 + "\n\n"
        
        # Add total at the end
        expenses_text += f"💰 Jami harajat: {total_expenses:,} so'm"
        
        # Split message if too long (Telegram limit is 4096 characters)
        if len(expenses_text) > 4000:
            # Send in chunks
            chunks = []
            current_chunk = "💸 Sizning harajatlaringiz:\n\n"
            
            for i, expense in enumerate(expenses, 1):
                expense_id, summa, izoh, kategoriya, user_id_db = expense
                
                expense_entry = f"📌 #{i}\n"
                expense_entry += f"💵 Summa: {summa} so'm\n"
                expense_entry += f"📂 Kategoriya: {kategoriya}\n"
                expense_entry += f"📝 Izoh: {izoh or 'Izoh yoq'}\n"
                expense_entry += "─" * 20 + "\n\n"
                
                if len(current_chunk + expense_entry) > 3800:
                    chunks.append(current_chunk)
                    current_chunk = f"💸 Harajatlaringiz (davomi) - #{i}-{len(expenses)}:\n\n"
                
                current_chunk += expense_entry
            
            # Add total to last chunk
            current_chunk += f"💰 Jami harajat: {total_expenses:,} so'm"
            chunks.append(current_chunk)
            
            # Send all chunks
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await message.reply(chunk, reply_markup=main_menu)
                else:
                    await message.reply(chunk)
        else:
            await message.reply(expenses_text, reply_markup=main_menu)
            
    except Exception as e:
        print(f"Error showing expenses: {e}")
        await message.reply(
            f"❌ Xatolik yuz berdi: {str(e)}\n\n"
            "Iltimos, qayta urinib ko'ring yoki admin bilan bog'laning.",
            reply_markup=main_menu
        )

