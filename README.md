# Kassa AI Bot

A Telegram bot for managing income and expenses with AI-powered analysis and admin panel functionality.

## Features

### 🤖 AI-Powered Analysis
- Voice and text message processing using Google Gemini AI
- Automatic categorization of income and expenses
- Smart financial insights

### 👤 User Management
- Free and PRO plan system
- Token-based plan activation
- AI usage limits for free users (3 tests)
- User statistics and profiles

### 👑 Admin Panel
- Broadcast messages to all users
- User and admin management
- Token generation (PRO and Admin tokens)
- Detailed statistics and monitoring

### 📊 Financial Management
- Income and expense tracking
- Detailed reports and statistics
- Data export and backup
- Multi-language support (Uzbek, Russian, English)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Muhammaddiyor2010/Kassa_origin.git
cd Kassa_origin
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/local.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the bot:
```bash
python bot.py
```

### Production Deployment

1. Install production dependencies:
```bash
pip install -r requirements/production.txt
```

2. Set up environment variables:
```bash
export BOT_TOKEN="your_bot_token"
export WEBHOOK_URL="https://yourdomain.com"
export GEMINI_API_KEY="your_gemini_api_key"
export MAIN_ADMIN_ID="7231910736"
```

3. Run with webhook server:
```bash
python webhook_server.py
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram bot token | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `WEBHOOK_URL` | Webhook URL for production | Production only |
| `MAIN_ADMIN_ID` | Main admin user ID | Yes |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |

### Database

The bot uses SQLite by default for local development and can be configured to use PostgreSQL for production.

#### Tables:
- `Users` - User information and settings
- `Chiqim` - Expense records
- `Kirim` - Income records
- `ProTokens` - PRO plan activation tokens
- `Admins` - Admin user management
- `AdminTokens` - Admin activation tokens

## Usage

### For Users

1. Start the bot: `/start`
2. Add income/expenses by sending text or voice messages
3. View reports: "📊 Hisobot"
4. Check settings: "⚙️ Sozlamalar"
5. Upgrade to PRO: "💎 PRO olish"

### For Admins

1. Access admin panel: `/admin`
2. Send broadcasts: "📢 Reklama yuborish"
3. Manage users: "👥 Foydalanuvchilar"
4. Create tokens: "🔑 Admin Tokenlar" / "💎 PRO Tokenlar"

## API Endpoints (Production)

- `GET /health` - Health check
- `GET /stats` - Bot statistics
- `POST /webhook` - Telegram webhook

## Project Structure

```
kassa-ai/
├── bot.py                 # Main bot file
├── webhook_server.py      # Production webhook server
├── config/               # Configuration files
│   ├── base.py
│   ├── config.py
│   └── production.py
├── handlers/             # Message handlers
│   ├── start.py
│   ├── chiqim.py
│   ├── admin.py
│   └── ...
├── keyboards/            # Keyboard layouts
├── lexicon/              # Language files
├── models/               # Database models
├── tables/               # Database operations
├── utils/                # Utility functions
└── requirements/         # Dependencies
```

## Development

### Adding New Features

1. Create handler in `handlers/` directory
2. Add keyboard layouts in `keyboards/`
3. Update database schema in `tables/`
4. Add language strings in `lexicon/`

### Testing

```bash
# Run tests
python -m pytest tests/

# Test specific functionality
python test_admin.py
```

## Deployment

### Using Docker

```bash
# Build image
docker build -t kassa-ai-bot .

# Run container
docker run -d --name kassa-bot \
  -e BOT_TOKEN="your_token" \
  -e GEMINI_API_KEY="your_key" \
  kassa-ai-bot
```

### Using Systemd

1. Create service file:
```ini
[Unit]
Description=Kassa AI Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/kassa-ai
ExecStart=/path/to/venv/bin/python webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start:
```bash
sudo systemctl enable kassa-bot
sudo systemctl start kassa-bot
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: @Dier_ai on Telegram

## Changelog

### v1.0.0
- Initial release
- AI-powered income/expense analysis
- Admin panel with broadcast functionality
- PRO/Free plan system
- Multi-language support