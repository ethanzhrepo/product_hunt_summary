# Product Hunt Summary Automation

A Python application that automatically fetches trending Product Hunt products, analyzes them with AI, and sends summaries to Telegram channels.

## Features

- 🌅 **Daily Tasks**: Fetch today's top 20 Product Hunt products, analyze with AI, and send to Telegram
- 📅 **Weekly Tasks**: Get weekly trending products and generate weekly summary reports
- 📊 **Monthly Tasks**: Get monthly trending products and generate monthly summary reports
- 🤖 **AI Analysis**: Use DeepSeek API for product analysis and summary generation
- 📱 **Telegram Integration**: Auto-send to Telegram channels with automatic message pinning
- ⏰ **Scheduled Tasks**: Automated scheduling using APScheduler
- 🏷️ **Category Tags**: Different period identifiers (daily top, weekly top, monthly top)

## Project Structure

```
product_hunt_summary/
├── src/
│   ├── config_manager.py      # Configuration management
│   ├── product_hunt_api.py    # Product Hunt API client
│   ├── deepseek_analyzer.py   # DeepSeek AI analyzer
│   ├── telegram_bot.py        # Telegram bot
│   ├── scheduler.py           # Task scheduler
│   └── main.py               # Application entry point
├── config.yml                # Configuration file
├── requirements.txt          # Python dependencies
├── environment.yml           # Conda environment file
├── setup.sh                 # Environment setup script
├── start.sh                 # Startup script
├── .env.example             # Environment variables template
└── logs/                    # Log directory
```

## Quick Start

### 1. Environment Setup

Make sure conda is installed, then run:

```bash
# Clone or download the project locally
cd product_hunt_summary

# Run setup script
./setup.sh
```

### 2. Configure API Keys

Copy and edit the environment variables file:

```bash
cp .env.example .env
```

Fill in the following information in the `.env` file:

```bash
# Product Hunt Developer Token
PH_DEV_TOKEN=your_product_hunt_developer_token_here

# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Telegram Channel ID (e.g., @your_channel or -1001234567890)
TELEGRAM_CHANNEL_ID=@your_channel_username_or_chat_id
```

### 3. Obtain API Keys

#### Product Hunt Developer Token
1. Visit [Product Hunt API](https://api.producthunt.com/v2/oauth/applications)
2. Create a new application
3. Generate Developer Token

#### DeepSeek API Key
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Register an account and get API key
3. Free version provides 5000 characters/month quota

#### Telegram Bot Token
1. Find @BotFather in Telegram
2. Send `/newbot` to create a new bot
3. Get the bot token
4. Add the bot to your channel and set it as an administrator

### 4. Run the Application

```bash
# Test connections
./start.sh test

# Manually execute daily task
./start.sh daily

# Start scheduled service (background)
./start.sh
```

## Usage Instructions

### Startup Script Parameters

```bash
./start.sh [command]
```

Available commands:
- `(no parameters)`: Start background service, automatically execute scheduled tasks
- `test`: Test all API connections
- `daily`: Manually execute daily task
- `weekly`: Manually execute weekly task
- `monthly`: Manually execute monthly task
- `help`: Show help information

### Scheduled Task Configuration

Configure scheduled tasks in `config.yml`:

```yaml
scheduling:
  daily_time: "09:00"      # Execute at 9 AM daily
  weekly_day: "monday"     # Execute every Monday
  monthly_day: 1           # Execute on the 1st of each month
  timezone: "America/Vancouver"
```

### Language Configuration

The application supports multi-language output, with Chinese as default. Configure in `config.yml`:

```yaml
language:
  output_language: "zh"        # Output language code
  ai_system_language: "Chinese" # AI system language description
```

**Supported Languages**:
- `zh` - Chinese (default)
- `en` - English
- `ja` - Japanese
- `ko` - Korean (coming soon)
- `es` - Spanish (coming soon)
- `fr` - French (coming soon)
- `de` - German (coming soon)

**Language Configuration Description**:
- `output_language`: Affects the language of Telegram messages and AI analysis results
- `ai_system_language`: Language description used during AI analysis

**Language Switching Examples**:
```yaml
# Switch to English
language:
  output_language: "en"
  ai_system_language: "English"

# Switch to Japanese
language:
  output_language: "ja"
  ai_system_language: "Japanese"
```

### Message Format

The application sends two types of messages:

1. **Directory Messages** (pinned): Contains product list and AI summary
2. **Individual Product Messages**: Detailed analysis of each product

Messages are tagged according to their period:
- 🌅 Daily top - Daily products
- 📅 Weekly top - Weekly products  
- 📊 Monthly top - Monthly products

## Technology Stack

- **Python 3.11+**: Main programming language
- **Product Hunt API v2**: Product data source
- **DeepSeek API**: AI analysis and summary generation
- **python-telegram-bot**: Telegram integration
- **APScheduler**: Task scheduling
- **PyYAML**: Configuration management
- **Conda**: Environment management

## Troubleshooting

### Common Issues

1. **Environment Creation Failed**
   ```bash
   # Clean conda cache
   conda clean --all
   # Re-run setup.sh
   ./setup.sh
   ```

2. **API Connection Failed**
   ```bash
   # Check network connection and API keys
   ./start.sh test
   ```

3. **Telegram Sending Failed**
   - Ensure the bot is added to the channel
   - Ensure the bot has permissions to send messages and pin messages
   - Check channel ID format (@username or numeric ID)

4. **Permission Errors**
   ```bash
   # Add execute permissions to scripts
   chmod +x setup.sh start.sh
   ```

### View Logs

```bash
# View application logs
tail -f logs/app.log

# View error logs
grep ERROR logs/app.log
```

## Development Notes

### Project Architecture

- `ConfigManager`: Configuration file and environment variable management
- `ProductHuntAPI`: Product Hunt GraphQL API client
- `DeepSeekAnalyzer`: AI analysis and summary generation
- `TelegramBot`: Telegram message sending and management
- `ProductHuntScheduler`: Task scheduling and coordination

### Custom Development

1. **Modify Analysis Prompts**: Edit prompts in `src/deepseek_analyzer.py`
2. **Adjust Message Format**: Modify message templates in `src/telegram_bot.py`
3. **Add New Task Types**: Add new methods in `src/scheduler.py`

## API Limitations

- **Product Hunt API**: Does not allow commercial use by default. Contact hello@producthunt.com for commercial use
- **DeepSeek API**: Free version 5000 characters/month, paid version $49/month for 10K requests
- **Telegram Bot API**: No special restrictions, but has rate limits

## License

This project is for learning and personal use only. Please comply with the terms of use of each API service provider.

## Contributing

Issues and Pull Requests are welcome!

## Changelog

### v1.0.0
- Initial release
- Support for daily/weekly/monthly Product Hunt product analysis
- Integrated DeepSeek AI and Telegram Bot
- Complete scheduled task system