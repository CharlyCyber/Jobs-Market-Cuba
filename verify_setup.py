#!/usr/bin/env python3

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def check_python_syntax(filepath):
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("Cuba Jobs Bot - Setup Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    print("📁 Checking Core Files...")
    core_files = [
        ('run.py', 'Main entry point'),
        ('.env.example', 'Environment example'),
        ('requirements.txt', 'Dependencies'),
        ('.gitignore', 'Git ignore file'),
        ('README.md', 'Main documentation'),
    ]
    
    for filepath, desc in core_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    print()
    print("🤖 Checking Bot Files...")
    bot_files = [
        'bot/__init__.py',
        'bot/main.py',
        'bot/handlers.py',
        'bot/config.py',
        'bot/utils/__init__.py',
        'bot/utils/logger.py',
        'bot/utils/formatter.py',
    ]
    
    for filepath in bot_files:
        if not check_file_exists(filepath, os.path.basename(filepath)):
            all_good = False
    
    print()
    print("🕷️ Checking Scraper Files...")
    scraper_files = [
        'scrapers/__init__.py',
        'scrapers/base_scraper.py',
        'scrapers/revolico_scraper.py',
        'scrapers/cubisima_scraper.py',
        'scrapers/cucoders_scraper.py',
        'scrapers/scraper_manager.py',
    ]
    
    for filepath in scraper_files:
        if not check_file_exists(filepath, os.path.basename(filepath)):
            all_good = False
    
    print()
    print("🔍 Checking Filter Files...")
    filter_files = [
        'filters/__init__.py',
        'filters/job_filter.py',
    ]
    
    for filepath in filter_files:
        if not check_file_exists(filepath, os.path.basename(filepath)):
            all_good = False
    
    print()
    print("🧪 Checking Test Files...")
    test_files = [
        'tests/__init__.py',
        'tests/test_filters.py',
        'tests/test_scrapers.py',
        'pytest.ini',
    ]
    
    for filepath in test_files:
        if not check_file_exists(filepath, os.path.basename(filepath)):
            all_good = False
    
    print()
    print("📚 Checking Documentation...")
    doc_files = [
        'README.md',
        'SETUP.md',
        'DEPLOYMENT.md',
        'CONTRIBUTING.md',
        'FAQ.md',
        'CHANGELOG.md',
        'LICENSE',
    ]
    
    for filepath in doc_files:
        if not check_file_exists(filepath, os.path.basename(filepath)):
            all_good = False
    
    print()
    print("🐳 Checking Docker Files...")
    docker_files = [
        'Dockerfile',
        'docker-compose.yml',
        '.dockerignore',
    ]
    
    for filepath in docker_files:
        if not check_file_exists(filepath, os.path.basename(filepath)):
            all_good = False
    
    print()
    print("🔧 Checking Python Syntax...")
    python_files = [
        'run.py',
        'bot/main.py',
        'bot/handlers.py',
        'bot/config.py',
        'scrapers/base_scraper.py',
        'filters/job_filter.py',
    ]
    
    syntax_ok = True
    for filepath in python_files:
        if Path(filepath).exists():
            if check_python_syntax(filepath):
                print(f"✅ {filepath} - Syntax OK")
            else:
                syntax_ok = False
                all_good = False
    
    print()
    print("=" * 60)
    
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your TELEGRAM_BOT_TOKEN")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Run the bot: python run.py")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please review the errors above.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
