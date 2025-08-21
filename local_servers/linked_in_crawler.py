from typing import Literal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os
import random
import time

load_dotenv()

class Linked_crawler:
    def __init__(self):
        self.username = os.getenv("linkedin_username")
        self.password = os.getenv("linkedin_password")
        self.driver = self.launch_chrome()

    def default_function(self):
        dstime = random.randint(2,6)
        print(f"sleeping for {dstime} sec")
        time.sleep(dstime)
        print(">>> Done sleeping!")

    def __getattribute__(self, name):
        # Get the actual attribute
        attr = object.__getattribute__(self, name)

        # Only wrap callable methods (not default_function itself or __getattribute__)
        if callable(attr) and name not in ("default_function", "__getattribute__"):
            def wrapper(*args, **kwargs):
                self.default_function()  # Run default function first
                return attr(*args, **kwargs)
            return wrapper

        return attr
    
    def launch_chrome(headless=False, window_size="1920,1080"):
        """
        Launch Chrome browser using Selenium
        
        Args:
            headless (bool): Run browser in headless mode (no GUI)
            window_size (str): Browser window size in "width,height" format
        
        Returns:
            webdriver.Chrome: Chrome WebDriver instance
        """
        # Configure Chrome options
        chrome_options = Options()
        
        # Disable AI/ML features that cause tensor errors
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-features=BlinkGenPropertyTrees')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-field-trial-config')
        chrome_options.add_argument('--disable-back-forward-cache')
        
        # Disable GPU acceleration to fix GPU state errors
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-gpu-sandbox')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # Additional stability options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        
        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
            print("Chrome browser launched successfully!")
            return driver
            
        except Exception as e:
            print(f"Failed to launch Chrome: {e}")
            return None

    def login(self):
        login_url = "https://www.linkedin.com/login"
        if self.driver:
            self.driver.get(login_url)
              
        username_field = self.driver.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys(self.username)

        password_field = self.driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(self.password)

        wait = WebDriverWait(self.driver, 10)
        signin_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-litms-control-urn="login-submit"]'))
        )
        
        signin_button.click()
        print("Successfully clicked Sign in button")
          
        return True

    def open_url(self,url : str):
        if self.driver:
            self.driver.get(url)
        return None

    def scrape_text_by_id(self , element_id):
        """Scrape text from element by ID"""
        try:
            element = self.driver.find_element(By.ID, element_id)
            return element.text
        except Exception as e:
            print(f"Error finding element by ID '{element_id}': {e}")
            return None

    def scrape_text_by_class(self , class_name):
        """Scrape text from element by class name"""
        try:
            element = self.driver.find_element(By.CLASS_NAME, class_name)
            return element.text
        except Exception as e:
            print(f"Error finding element by class '{class_name}': {e}")
            return None

    def scrape_text_by_xpath(self , xpath):
        """Scrape text from element by XPath"""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text
        except Exception as e:
            print(f"Error finding element by XPath '{xpath}': {e}")
            return None

    def scrape_text_by_css(self , css_selector):
        """Scrape text from element by CSS selector"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
            return element.text
        except Exception as e:
            print(f"Error finding element by CSS '{css_selector}': {e}")
            return None

    def get_element_data(self,type):

        profile_elements = [
            {"type":"xpath",
             "name":"about",
             "info":'//*[@id="profile-content"]/div/div[2]/div/div/main/section[3]/div[3]/div'},
             {"type":"xpath",
             "name":"experience",
             "info":'//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]'}
        ]

        job_elements = []

        return profile_elements if type == "profile" else job_elements

from fastmcp import FastMCP
mcp = FastMCP(name="Linkedin_Crawler")
@mcp.tool()
def main(url : str, url_type : Literal["job","profile"] = 'job'):
    '''

    LinkedIN profile Crawler

    Crawlers LinkedIn to get the info from a user profile

    
    Args:
        url = The LinkedIN URL
        url_type = The type of URL eg("job" or "profile")

    Returns:
        A formatted dict with data.

    Example:
        main("htttps://www.linkedin.com/in/username","profile") 

    '''
    crawler = Linked_crawler()
    crawler.login()
    crawler.open_url(url)
    element_data = crawler.get_element_data(url_type)
    found_data_check = {}

    found_data = {}
    for data in element_data:
        if data['type'] == "xpath":
            if not found_data_check[data['name']]:
                text = crawler.scrape_text_by_xpath(data["info"])
                if text is not None:
                    found_data_check[data['name']] = True
                    found_data[data['name']] = text
        elif data['type'] == "id":
            if not found_data_check[data['name']]:
                text = crawler.scrape_text_by_id(data["info"])
                if text is not None:
                    found_data_check[data['name']] = True
                    found_data[data['name']] = text

        elif data['type'] == "class":
            if not found_data_check[data['name']]:
                text = crawler.scrape_text_by_class(data["info"])
                if text is not None:
                    found_data_check[data['name']] = True
                    found_data[data['name']] = text

        elif data['type'] == "css":
            if not found_data_check[data['name']]:
                text = crawler.scrape_text_by_css(data["info"])
                if text is not None:
                    found_data_check[data['name']] = True
                    found_data[data['name']] = text

    return found_data
            


# main(url="https://www.linkedin.com/in/syed-saleem-/") 

if __name__ == "__main__":
    # mcp.run(transport="streamable-http")
    mcp.run(transport="stdio")