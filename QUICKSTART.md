# ⚡ Quick Start Guide

Get the Cuba Jobs Telegram Bot running in 5 minutes!

## 🚀 Fastest Way (Using Quick Start Script)

```bash
# 1. Navigate to project
cd Jobs-Market-Cuba

# 2. Run quick start script
./quickstart.sh
```

The script will:
- Create `.env` file if needed
- Set up virtual environment
- Install dependencies
- Start the bot

**Important:** Edit `.env` and add your `TELEGRAM_BOT_TOKEN` when prompted!

## 🐳 Docker Way (Even Easier!)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and add your token
nano .env  # or use your favorite editor

# 3. Run with Docker
docker-compose up -d

# 4. Check logs
docker-compose logs -f
```

## 🐍 Manual Way

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
nano .env  # Add your TELEGRAM_BOT_TOKEN

# 4. Run
python run.py
```

## 🎯 Get Your Telegram Bot Token

1. Open Telegram
2. Search for `@BotFather`
3. Send: `/newbot`
4. Follow instructions
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
6. Paste it in your `.env` file

## ✅ Verify Setup

```bash
# Check if everything is configured correctly
python3 verify_setup.py
```

## 🧪 Test Without Telegram

```bash
# Test scraping functionality standalone
python test_scraping.py
```

This will scrape job offers and save results to `test_output.html`.

## 💬 Use the Bot

1. Open Telegram
2. Search for your bot (the username you chose)
3. Send: `/start`
4. Send: `Ofertas`
5. Wait 5-15 seconds for results

## 📊 Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message |
| `/help` | Show help information |
| `Ofertas` | Search for job offers |

## 🔧 Common Issues

### "TELEGRAM_BOT_TOKEN is required"
**Solution:** Create `.env` file and add your token:
```bash
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
```

### "Module not found"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Bot doesn't respond
**Solution:** 
1. Make sure the script is running (check terminal)
2. Verify your token is correct
3. Try `/start` command first

### Slow responses
**Solution:** Normal! Scraping 3 platforms takes time. Wait 5-15 seconds.

## 📚 Need More Help?

- **Detailed Setup:** See [SETUP.md](SETUP.md)
- **Deployment:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **FAQ:** See [FAQ.md](FAQ.md)
- **Full Docs:** See [README.md](README.md)

## 🎉 That's It!

Your bot is now running and ready to find job offers in Cuba! 🇨🇺

---

**Quick Reference Card:**

```
Setup:    ./quickstart.sh
Docker:   docker-compose up -d
Manual:   python run.py
Test:     python test_scraping.py
Verify:   python verify_setup.py
Stop:     Ctrl+C (or docker-compose down)
```
