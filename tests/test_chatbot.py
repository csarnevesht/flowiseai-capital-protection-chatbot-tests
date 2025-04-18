import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .pages.chatbot_page import ChatbotPage

class ChatbotTests(unittest.TestCase):
    def setUp(self):
        # Create Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--incognito")  # Enable incognito mode
        chrome_options.add_argument("--start-maximized")  # Start with maximized window
        
        # Initialize the driver with options
        self.driver = webdriver.Chrome(options=chrome_options)
        self.chatbot_page = ChatbotPage(self.driver)
        self.chatbot_page.load("https://flowiseai-her8.onrender.com/chatbot/769b8e19-17f3-4e89-80d7-73553211c085")
        
        # Fill in user information
        self.chatbot_page.fill_user_info(
            name="Test User",
            email="test@example.com",
            phone="1234567890"
        )

    def tearDown(self):
        self.driver.quit()

    def test_chatbot_initial_load(self):
        """Test that the chatbot interface loads correctly"""
        self.assertTrue(
            self.chatbot_page.is_chat_input_visible(),
            "Chat input should be visible"
        )

    def test_send_message(self):
        """Test sending a message to the chatbot"""
        test_message = "Hello, how are you?"
        self.chatbot_page.send_message(test_message)
        
        self.assertTrue(
            self.chatbot_page.is_message_visible(test_message),
            "Sent message should be visible"
        )

    def test_chatbot_response(self):
        """Test that the chatbot responds to messages"""
        self.chatbot_page.send_message("What can you help me with?")
        
        self.assertTrue(
            self.chatbot_page.is_chatbot_response_visible(),
            "Chatbot response should be visible"
        )

if __name__ == "__main__":
    unittest.main() 