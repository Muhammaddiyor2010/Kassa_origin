from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from loader import db
from keyboards.keyboards import main_menu
from datetime import datetime, timedelta

hisobot_router: Router = Router()


@hisobot_router.message(Command("hisobot"))
@hisobot_router.message(F.text == "📊 Hisobot")
async def show_report(message: Message):
    """
    Show comprehensive financial report for user
    """
    try:
        user_id = message.from_user.id
        
        # Get user's income and expenses
        income_data = db.get_user_kirim(user_id)
        expenses_data = db.get_user_chiqim(user_id)
        
        # Calculate totals
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
        
        # Calculate balance
        balance = total_income - total_expenses
        
        # Get user info
        user_info = db.select_user(id=user_id)
        user_name = user_info[1] if user_info else "Foydalanuvchi"
        
        # Calculate ratio
        ratio = (total_income/total_expenses*100) if total_expenses > 0 else float('inf')
        ratio_text = f"{ratio:.1f}%" if ratio != float('inf') else "∞%"
        
        # Create report
        report_text = f"""📊 **FINANCIAL REPORT** 📊

👤 **Foydalanuvchi:** {user_name}
📅 **Sana:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

💰 **DAROMADLAR:**
• Jami daromad: {total_income:,} so'm
• Daromadlar soni: {len(income_data) if income_data else 0} ta

💸 **HARAJATLAR:**
• Jami harajat: {total_expenses:,} so'm  
• Harajatlar soni: {len(expenses_data) if expenses_data else 0} ta

📈 **BALANS:**
• Qolgan mablag': {balance:,} so'm
• Daromad/Harajat nisbati: {ratio_text}

📊 **STATISTIKA:**
• O'rtacha daromad: {total_income//len(income_data) if income_data else 0:,} so'm
• O'rtacha harajat: {total_expenses//len(expenses_data) if expenses_data else 0:,} so'm

🎯 **TAVSIYA:**
"""
        
        # Add recommendations based on balance
        if balance > 0:
            report_text += "✅ Yaxshi! Sizning daromadingiz harajatlaringizdan ko'p. Bu yaxshi moliyaviy holat!"
        elif balance == 0:
            report_text += "⚖️ Daromad va harajatlaringiz teng. Harajatlarni kamaytirish yoki daromadni oshirish kerak."
        else:
            report_text += "⚠️ Diqqat! Harajatlaringiz daromadingizdan ko'p. Moliyaviy rejani ko'rib chiqing."
        
        # Add recent transactions summary
        if income_data or expenses_data:
            report_text += "\n\n📋 **SO'NGI TRANSAKSIYALAR:**\n"
            
            # Show last 3 income entries
            if income_data:
                report_text += "\n💰 **So'ngi daromadlar:**\n"
                for i, inc in enumerate(income_data[:3], 1):
                    report_text += f"{i}. {inc[1]} so'm - {inc[2] or 'Izoh yoq'}\n"
            
            # Show last 3 expense entries  
            if expenses_data:
                report_text += "\n💸 **So'ngi harajatlar:**\n"
                for i, exp in enumerate(expenses_data[:3], 1):
                    report_text += f"{i}. {exp[1]} so'm - {exp[2] or 'Izoh yoq'}\n"
        
        # If no data exists
        if not income_data and not expenses_data:
            report_text = """📊 **FINANCIAL REPORT** 📊

👤 **Foydalanuvchi:** {user_name}
📅 **Sana:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

❌ **Ma'lumot yo'q**

Hali hech qanday daromad yoki harajat kiritilmagan.

💰 **Daromad qo'shish uchun:**
• "Ish haqim 2000000 so'm oldim"
• Ovozli xabar yuboring

💸 **Harajat qo'shish uchun:**
• "Ovqat uchun 50000 so'm sarf qildim"  
• Ovozli xabar yuboring

📊 Hisobotni ko'rish uchun ma'lumotlar kiritilgandan keyin qayta urinib ko'ring.""".format(
                user_name=user_name,
                datetime=datetime
            )
        
        # Send the report
        await message.reply(report_text, reply_markup=main_menu, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        await message.reply(
            f"❌ Hisobot yaratishda xatolik yuz berdi: {str(e)}\n\n"
            "Iltimos, qayta urinib ko'ring yoki admin bilan bog'laning.",
            reply_markup=main_menu
        )
