from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class ChatbotPage:
    # Locators
    NAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='Name']")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[placeholder='Email Address']")
    PHONE_INPUT = (By.CSS_SELECTOR, "input[placeholder='Phone Number']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button:contains('Submit')")
    CHAT_INPUT = (By.CSS_SELECTOR, "[role='textbox']")
    MESSAGE = (By.CSS_SELECTOR, ".message")
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def load(self, url):
        """Load the chatbot page"""
        self.driver.get(url)
        return self
    
    def fill_user_info(self, name, email, phone):
        """Fill in the user information form"""
        # Wait for shadow root to be available
        shadow_host = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "flowise-chatbot"))
        )
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        
        # Find elements within shadow DOM
        name_input = shadow_root.find_element(*self.NAME_INPUT)
        email_input = shadow_root.find_element(*self.EMAIL_INPUT)
        phone_input = shadow_root.find_element(*self.PHONE_INPUT)
        submit_button = shadow_root.find_element(*self.SUBMIT_BUTTON)
        
        # Fill the form
        name_input.send_keys(name)
        email_input.send_keys(email)
        phone_input.send_keys(phone)
        submit_button.click()
        return self
    
    def wait_for_chat_input(self):
        """Wait for and return the chat input element"""
        shadow_host = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "flowise-chatbot"))
        )
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        return shadow_root.find_element(*self.CHAT_INPUT)
    
    def send_message(self, message):
        """Send a message to the chatbot"""
        chat_input = self.wait_for_chat_input()
        chat_input.send_keys(message)
        chat_input.send_keys(Keys.ENTER)
        return self
    
    def get_sent_message(self, message_text):
        """Get the sent message element"""
        shadow_host = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "flowise-chatbot"))
        )
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        return shadow_root.find_element(By.XPATH, f".//*[contains(text(), '{message_text}')]")
    
    def get_chatbot_response(self):
        """Get the chatbot's response element"""
        shadow_host = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "flowise-chatbot"))
        )
        shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        return shadow_root.find_element(*self.MESSAGE)
    
    def is_chat_input_visible(self):
        """Check if chat input is visible"""
        try:
            return self.wait_for_chat_input().is_displayed()
        except:
            return False
    
    def is_message_visible(self, message_text):
        """Check if a specific message is visible"""
        try:
            return self.get_sent_message(message_text).is_displayed()
        except:
            return False
    
    def is_chatbot_response_visible(self):
        """Check if chatbot response is visible"""
        try:
            return self.get_chatbot_response().is_displayed()
        except:
            return False 