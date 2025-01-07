from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime, timedelta
import schedule
import pytz
import json

def get_page_height(driver):
    """Get total scrollable height of page"""
    return driver.execute_script("return Math.max( document.documentElement.scrollHeight, document.documentElement.clientHeight);")

def calculate_scroll_positions(total_height, window_height, pages_to_capture):
    """
    Calculate scroll positions for capturing screenshots based on desired number of pages.
    Returns a list of scroll positions that divide the page into roughly equal sections.
    """
    if pages_to_capture == 1:
        return [0]  # Just the top of the page
    
    # For two pages, we want:
    # 1. Top of page (0)
    # 2. About 80% of first viewport height
    viewport_overlap = 0.2  # 20% overlap between viewports
    second_position = int(window_height * (1 - viewport_overlap))
    
    return [0, second_position]

def take_screenshots(url_config, output_folder="screenshots"):
    """
    Take screenshots of specified pages of the website with improved scrolling logic
    
    Args:
        url_config: Either a string (URL) for backward compatibility or a dict with 'url' and 'pages' keys
        output_folder: Base folder for screenshots
    """
    # Handle both string and dict inputs for backward compatibility
    if isinstance(url_config, str):
        url = url_config
        pages_to_capture = 2
    else:
        url = url_config['url']
        pages_to_capture = url_config['pages']
    
    # Get current date in EST
    est = pytz.timezone('US/Eastern')
    current_date = datetime.now(est)
    
    # Create folders
    date_folder = current_date.strftime("%m-%d")
    daily_folder = os.path.join(output_folder, date_folder)
    domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
    website_folder = os.path.join(daily_folder, domain)
    
    if not os.path.exists(website_folder):
        os.makedirs(website_folder)
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[{current_date.strftime('%Y-%m-%d %H:%M:%S %Z')}] Loading {url}...")
        
        driver.set_page_load_timeout(30)
        
        # Load page with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get(url)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(5)
        
        print("Waiting for page to fully load...")
        time.sleep(10)  # Initial wait for page load
        
        # Get page dimensions
        total_height = get_page_height(driver)
        window_height = driver.get_window_size()['height']
        
        # Calculate scroll positions
        scroll_positions = calculate_scroll_positions(total_height, window_height, pages_to_capture)
        
        timestamp = current_date.strftime("%H%M%S")
        
        # Take screenshots at calculated positions
        for i, scroll_pos in enumerate(scroll_positions, 1):
            # Smooth scroll to position
            driver.execute_script(f"""
                window.scrollTo({{
                    top: {scroll_pos},
                    behavior: 'smooth'
                }});
            """)
            
            # Wait for scroll animation and any lazy-loaded content
            time.sleep(3)
            
            # Ensure we're at the right position (sometimes smooth scroll doesn't finish)
            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
            time.sleep(1)
            
            filename = f"{website_folder}/page{i}_{timestamp}.png"
            driver.save_screenshot(filename)
            print(f"Screenshot {i} saved as {filename}")
        
    except Exception as e:
        print(f"Error capturing {url}: {str(e)}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

def load_websites():
    """Load websites from config file"""
    try:
        with open('websites.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_websites(websites):
    """Save websites to config file"""
    with open('websites.json', 'w') as f:
        json.dump(websites, f, indent=2)

# def schedule_daily_screenshots():
#    """Schedule screenshots at 6 AM EST for all websites"""
#    websites = load_websites()
    
#    def job():
#        for url in websites:
#            take_screenshots(url)
    
    # Schedule the job for 6 AM EST
#    schedule.every().day.at("06:00").do(job)
    
#    print(f"\nScheduled daily screenshots for {len(websites)} websites at 6:00 AM EST:")
#    for url in websites:
 #       print(f"- {url}")
  #  print("\nPress Ctrl+C to stop the program")
   # 
    #while True:
     #   schedule.run_pending()
      #  time.sleep(1)
def schedule_daily_screenshots():
    """Schedule screenshots at 11:50 AM EST for all websites"""
    websites = load_websites()
    
    def job():
        for url in websites:
            take_screenshots(url)
    
    # Schedule the job for 11:50 AM EST
    schedule.every().day.at("12:29").do(job)
    
    print(f"\nScheduled daily screenshots for {len(websites)} websites at 11:50 AM EST:")
    for url in websites:
        print(f"- {url}")
    print("\nPress Ctrl+C to stop the program")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
def manage_websites():
    """Manage the list of websites to screenshot and their page settings"""
    websites = load_websites()
    
    # Convert simple list to dict if needed
    if websites and isinstance(websites[0], str):
        websites = [{
            'url': url,
            'pages': 2  # Default to 2 pages for backward compatibility
        } for url in websites]
    
    def save_current_websites():
        """Helper function to save the current website configuration"""
        save_websites(websites)
    
    while True:
        print("\nManage Websites")
        print("1. View current websites")
        print("2. Add website (screenshot first page only)")
        print("3. Add website (screenshot first and second pages)")
        print("4. Remove website")
        print("5. Modify existing website settings")
        print("6. Return to main menu")
        
        choice = input("\nSelect an option (1-6): ")
        
        if choice == '1':
            if websites:
                print("\nCurrent websites:")
                for i, site in enumerate(websites, 1):
                    pages_text = "first page only" if site['pages'] == 1 else "first and second pages"
                    print(f"{i}. {site['url']} ({pages_text})")
            else:
                print("\nNo websites configured")
                
        elif choice in ('2', '3'):
            url = input("Enter website URL: ")
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Check if URL already exists
            if any(site['url'] == url for site in websites):
                print("Website already exists in the list")
                continue
                
            # Add new website with specified number of pages
            new_site = {
                'url': url,
                'pages': 1 if choice == '2' else 2
            }
            websites.append(new_site)
            save_current_websites()
            pages_text = "first page only" if choice == '2' else "first and second pages"
            print(f"Added {url} ({pages_text})")
                
        elif choice == '4':
            if websites:
                print("\nSelect website to remove:")
                for i, site in enumerate(websites, 1):
                    print(f"{i}. {site['url']}")
                try:
                    idx = int(input("Enter number to remove (0 to cancel): "))
                    if 0 < idx <= len(websites):
                        removed = websites.pop(idx - 1)
                        save_current_websites()
                        print(f"Removed {removed['url']}")
                except ValueError:
                    print("Invalid input")
            else:
                print("\nNo websites to remove")
                
        elif choice == '5':
            if websites:
                print("\nSelect website to modify:")
                for i, site in enumerate(websites, 1):
                    pages_text = "first page only" if site['pages'] == 1 else "first and second pages"
                    print(f"{i}. {site['url']} ({pages_text})")
                try:
                    idx = int(input("Enter number to modify (0 to cancel): "))
                    if 0 < idx <= len(websites):
                        print("\nSelect new setting:")
                        print("1. Screenshot first page only")
                        print("2. Screenshot first and second pages")
                        setting = input("Enter choice (1-2): ")
                        if setting in ('1', '2'):
                            websites[idx - 1]['pages'] = 1 if setting == '1' else 2
                            save_current_websites()
                            print(f"Updated settings for {websites[idx - 1]['url']}")
                        else:
                            print("Invalid choice")
                except ValueError:
                    print("Invalid input")
            else:
                print("\nNo websites to modify")
                
        elif choice == '6':
            break

def main():
    while True:
        print("\nWebsite Screenshot Tool")
        print("1. Take screenshots now")
        print("2. Schedule daily screenshots at 6 AM EST")
        print("3. Manage websites")
        print("4. Quit")
        
        choice = input("\nSelect an option (1-4): ")
        
        if choice == '1':
            websites = load_websites()
            if websites:
                print("\nTaking screenshots for all configured websites...")
                for url in websites:
                    take_screenshots(url)
            else:
                print("\nNo websites configured. Please add websites first.")
            
        elif choice == '2':
            websites = load_websites()
            if websites:
                try:
                    schedule_daily_screenshots()
                except KeyboardInterrupt:
                    print("\nStopping scheduled screenshots...")
            else:
                print("\nNo websites configured. Please add websites first.")
                
        elif choice == '3':
            manage_websites()
                
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()