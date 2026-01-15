#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
import re
from bot.config import Config
import requests
from bot.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)
logger.setLevel('DEBUG')

def debug_cucoders():
    print("=== DEBUGGING CUCODERS SCRAPER ===")
    
    # Test 1: Direct request
    print("\n1. Testing direct HTTP request...")
    url = Config.CUCODERS_URL
    print(f"URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        
        # Test 2: Parse with BeautifulSoup
        print("\n2. Testing BeautifulSoup parsing...")
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Parsed successfully")
        
        # Test 3: Find job links with regex
        print("\n3. Testing regex pattern...")
        job_links = soup.find_all('a', href=lambda x: x and '/empleos/' in x and re.search(r'\d{4}-\d{2}-\d{2}', x))
        print(f"Job links found: {len(job_links)}")
        
        # Test 4: Extract job information
        print("\n4. Testing job extraction...")
        offers = []
        seen_containers = set()
        
        for i, link in enumerate(job_links[:5]):  # Test first 5
            print(f"\nProcessing link {i+1}: {link.get('href', '')}")
            
            try:
                # Get container
                container = link.find_parent('div', class_='inline-grid')
                if not container:
                    container = link.find_parent('div', class_=lambda x: x and 'inline-grid' in x if x else False)
                
                if container:
                    container_id = str(container)
                    print(f"Container ID: {container_id[:50]}...")
                    
                    if container_id in seen_containers:
                        print("Container already processed, skipping...")
                        continue
                    
                    seen_containers.add(container_id)
                    
                    # Extract info
                    title_elem = link
                    title = title_elem.get_text(strip=True)
                    link_url = title_elem.get('href', '')
                    
                    if link_url and not link_url.startswith('http'):
                        link_url = f"https://cucoders.dev{link_url}"
                    
                    print(f"Title: {title[:50]}...")
                    print(f"Link: {link_url}")
                    
                    # Create offer
                    offer = {
                        'title': title,
                        'company': 'Test Company',
                        'description': 'Test description',
                        'link': link_url,
                        'source': 'CuCoders'
                    }
                    
                    offers.append(offer)
                    print("Offer created successfully")
                
            except Exception as e:
                print(f"Error processing link: {str(e)}")
        
        print(f"\n5. Final results:")
        print(f"Total offers extracted: {len(offers)}")
        
        for i, offer in enumerate(offers):
            print(f"\nOffer {i+1}:")
            print(f"  Title: {offer['title']}")
            print(f"  Link: {offer['link']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_cucoders()