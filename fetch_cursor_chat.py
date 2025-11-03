#!/usr/bin/env python3
"""
Script to fetch and analyze Cursor agent chat data from a URL.
This requires selenium with a headless browser to load the dynamic content.
"""

import sys
import time
import json
from urllib.parse import urlparse, parse_qs

def extract_chat_id(url):
    """Extract the chat/conversation ID from the URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('selectedBcId', [None])[0]

def fetch_with_selenium(url):
    """Fetch chat content using Selenium with headless Chrome."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        print("Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            print(f"Loading URL: {url}")
            driver.get(url)
            
            # Wait for content to load (adjust selector as needed)
            print("Waiting for page to load...")
            time.sleep(5)  # Give time for dynamic content
            
            # Try to find chat messages
            page_source = driver.page_source
            
            # Save the full page source for analysis
            with open('/workspace/cursor_chat_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("Saved page source to cursor_chat_page.html")
            
            # Try to extract text content
            body = driver.find_element(By.TAG_NAME, 'body')
            text_content = body.text
            
            with open('/workspace/cursor_chat_text.txt', 'w', encoding='utf-8') as f:
                f.write(text_content)
            print("Saved text content to cursor_chat_text.txt")
            
            # Try to find specific chat elements (you may need to adjust selectors)
            try:
                messages = driver.find_elements(By.CSS_SELECTOR, '[data-message], .message, [role="article"]')
                print(f"\nFound {len(messages)} potential message elements")
                
                chat_data = []
                for i, msg in enumerate(messages):
                    chat_data.append({
                        'index': i,
                        'text': msg.text,
                        'html': msg.get_attribute('outerHTML')[:200]  # First 200 chars
                    })
                
                with open('/workspace/cursor_chat_messages.json', 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, indent=2)
                print("Saved messages to cursor_chat_messages.json")
                
            except Exception as e:
                print(f"Could not extract specific messages: {e}")
            
            return True
            
        finally:
            driver.quit()
            
    except ImportError:
        print("Error: selenium is not installed.")
        print("Install it with: pip install selenium")
        print("Also need Chrome and chromedriver installed.")
        return False
    except Exception as e:
        print(f"Error during fetching: {e}")
        return False

def fetch_with_requests(url):
    """Try to fetch with requests library (likely won't work for dynamic content)."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print("Attempting to fetch with requests...")
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save HTML
        with open('/workspace/cursor_chat_simple.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Try to extract text
        text = soup.get_text()
        with open('/workspace/cursor_chat_simple.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        print("Saved simple fetch results (may not contain chat content)")
        print("Note: This page likely loads content dynamically via JavaScript")
        
        return True
        
    except Exception as e:
        print(f"Error with simple fetch: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_cursor_chat.py <URL>")
        print("Example: python fetch_cursor_chat.py 'https://cursor.com/agents?selectedBcId=...'")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Fetching Cursor chat from: {url}")
    
    chat_id = extract_chat_id(url)
    print(f"Chat ID: {chat_id}")
    
    # Try Selenium first (more likely to work)
    print("\n=== Attempting with Selenium (headless browser) ===")
    if not fetch_with_selenium(url):
        print("\n=== Falling back to simple requests ===")
        fetch_with_requests(url)
    
    print("\n=== Done ===")
    print("Check the generated files in /workspace/")

if __name__ == '__main__':
    main()
