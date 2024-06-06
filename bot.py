import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import chromedriver_autoinstaller

# Load environment variables
load_dotenv(r"YOUR.env PATH")

# Twitter credentials
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# Telegram keys
token = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')

# Install ChromeDriver
chromedriver_autoinstaller.install()

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# URL for sending messages in Telegram
SEND_URL = f'https://api.telegram.org/bot{token}/sendMessage'

# Twitter profile URL
twitter_profile_url = "https://twitter.com/YOUR_USERNAME"
# Variable to identify the latest tweet
last_tweet_id = None

def twitter_login(driver, username, password):
    try:
        driver.get("https://twitter.com/i/flow/login")
        time.sleep(2)
        print("Verifying Username...")
        username_field = driver.find_element(By.CLASS_NAME, "r-30o5oe")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        print("Verified!")
        time.sleep(2)

        print("Veryfying Password...")
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        print("Verified!")
        time.sleep(5)

    except Exception as e:
        print(f"Error during login: {e}")
        driver.save_screenshot("login_error_screenshot.png")

while True:
    try:
        # Log in to Twitter
        twitter_login(driver, username, password)

        # Navigate to Twitter page
        driver.get(twitter_profile_url)
        print("Waiting for Twitter page to load...")

        # Wait for the page to load with WebDriverWait
        wait = WebDriverWait(driver, 30)
        tweets = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]')))
        print(f"Found {len(tweets)} tweets on the page.")

        if tweets:
            tweet_link_element = tweets[0].find_element(By.XPATH, './/a[@href and contains(@href, "/status/")]')
            tweet_url = tweet_link_element.get_attribute('href')
            tweet_id = tweet_url.split('/')[-1]

            print(f"Processing tweet: {tweet_url}")

            # Check if the tweet is new
            if tweet_id != last_tweet_id:
                last_tweet_id = tweet_id
                response = requests.post(SEND_URL, json={'chat_id': chat_id, 'parse_mode': 'HTML', 'text': tweet_url})
                print(f"Response from Telegram server: {response.status_code}")

    except Exception as e:
        print(f"Error while checking tweets: {e}")
        driver.save_screenshot("tweet_check_error_screenshot.png")
        with open("error_page.html", "w") as file:
            file.write(driver.page_source)

    finally:
        time.sleep(300)
