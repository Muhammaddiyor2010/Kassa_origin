from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Telefon raqamni yuborish",request_contact=True )
        ]
    ]
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💸 Harajatlari"),
            KeyboardButton(text="💰 Daromadlari")
        ],
        [
            KeyboardButton(text="📊 Hisobot"),
            KeyboardButton(text="⚙️ Sozlamalar")
        ]
    ],
    resize_keyboard=True,
    persistent=True
)