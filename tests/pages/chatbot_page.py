from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common.exceptions import TimeoutException

class ChatbotPage:
    # Locators
    SHADOW_HOST = "flowise-fullchatbot"
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def load(self, url):
        """Load the chatbot page"""
        self.driver.get(url)
        time.sleep(5)  # Wait for page to load
        return self
    
    def get_shadow_root(self):
        """Get the shadow root element with debugging"""
        try:
            print("Attempting to find shadow host...")
            # First, let's see what elements are on the page
            all_elements = self.driver.execute_script("""
                return Array.from(document.querySelectorAll('*')).map(el => ({
                    tagName: el.tagName,
                    id: el.id,
                    className: el.className,
                    attributes: Array.from(el.attributes).map(attr => `${attr.name}=${attr.value}`)
                }));
            """)
            print("All elements on page:", all_elements)
            
            # Try to find the shadow host
            shadow_host = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, self.SHADOW_HOST))
            )
            print(f"Found shadow host: {shadow_host.get_attribute('outerHTML')}")
            
            # Try to get the shadow root
            shadow_root = self.driver.execute_script("""
                const host = arguments[0];
                console.log('Host element:', host);
                const root = host.shadowRoot;
                console.log('Shadow root:', root);
                if (!root) {
                    console.log('No shadow root found');
                    return null;
                }
                // Log shadow root content
                console.log('Shadow root HTML:', root.innerHTML);
                return root;
            """, shadow_host)
            
            if not shadow_root:
                print("No shadow root found!")
                self.driver.save_screenshot("no_shadow_root.png")
                raise Exception("Could not access shadow root")
            
            print("Successfully accessed shadow root")
            return shadow_root
            
        except Exception as e:
            print(f"Error in get_shadow_root: {str(e)}")
            print("Page source:", self.driver.page_source)
            self.driver.save_screenshot("shadow_root_error.png")
            raise
    
    def fill_user_info(self, name, email, phone):
        """Fill in the user information form"""
        try:
            print("\n=== Starting form fill process ===")
            
            # Get shadow root using JavaScript
            print("Getting shadow root...")
            script = """
                const chatbot = document.querySelector('flowise-fullchatbot');
                if (!chatbot) return null;
                return chatbot.shadowRoot;
            """
            shadow_root = self.driver.execute_script(script)
            if not shadow_root:
                raise Exception("Could not find shadow root")
            
            # Find and fill form fields using JavaScript
            fill_script = """
                const name = arguments[0];
                const email = arguments[1];
                const phone = arguments[2];
                
                const chatbot = document.querySelector('flowise-fullchatbot');
                if (!chatbot || !chatbot.shadowRoot) return { error: 'No chatbot or shadow root found' };
                
                const shadowRoot = chatbot.shadowRoot;
                console.log('Shadow root found:', shadowRoot);
                
                // Debug: Log all input elements
                const allInputs = shadowRoot.querySelectorAll('input');
                console.log('All inputs:', Array.from(allInputs).map(i => ({
                    type: i.type,
                    placeholder: i.placeholder,
                    value: i.value
                })));
                
                // Find input fields
                const nameInput = shadowRoot.querySelector('input[placeholder*="name" i]');
                const emailInput = shadowRoot.querySelector('input[placeholder*="email" i]');
                const phoneInput = shadowRoot.querySelector('input[placeholder*="phone" i]');
                
                console.log('Found inputs:', {
                    name: nameInput?.placeholder,
                    email: emailInput?.placeholder,
                    phone: phoneInput?.placeholder
                });
                
                if (nameInput) {
                    nameInput.value = name;
                    nameInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                if (emailInput) {
                    emailInput.value = email;
                    emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                if (phoneInput) {
                    phoneInput.value = phone;
                    phoneInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
                // Find and click submit button
                const submitButton = shadowRoot.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
                
                return {
                    nameFilled: nameInput ? nameInput.value === name : false,
                    emailFilled: emailInput ? emailInput.value === email : false,
                    phoneFilled: phoneInput ? phoneInput.value === phone : false,
                    submitFound: !!submitButton
                };
            """
            
            print("\nFilling form fields...")
            result = self.driver.execute_script(fill_script, name, email, phone)
            print(f"Form fill results: {result}")
            
            if isinstance(result, dict) and 'error' in result:
                print(f"Error from JavaScript: {result['error']}")
                self.driver.save_screenshot("shadow_root_error.png")
                return False
            
            if not all([result.get('nameFilled'), result.get('emailFilled'), result.get('phoneFilled')]):
                print("Warning: Not all fields were filled successfully")
                self.driver.save_screenshot("form_fill_warning.png")
                return False
            
            if not result.get('submitFound'):
                print("Warning: Submit button not found")
                self.driver.save_screenshot("submit_button_not_found.png")
                return False
            
            print("Form submitted successfully")
            return True
            
        except Exception as e:
            print(f"Error in fill_user_info: {str(e)}")
            print("Page source:", self.driver.page_source)
            self.driver.save_screenshot("form_fill_error.png")
            raise
    
    def wait_for_chat_input(self):
        """Wait for and return the chat input element"""
        try:
            # Wait a moment for the form submission to complete and chat interface to load
            time.sleep(2)
            
            # Find elements directly using JavaScript
            script = """
                const chatbot = document.querySelector('flowise-fullchatbot');
                if (!chatbot || !chatbot.shadowRoot) {
                    console.log('No chatbot or shadow root found');
                    return { error: 'No chatbot or shadow root found' };
                }
                
                const shadowRoot = chatbot.shadowRoot;
                console.log('Shadow root found');
                
                // Debug: Log all elements in shadow root
                const allElements = Array.from(shadowRoot.querySelectorAll('*'));
                console.log('All elements:', allElements.map(el => ({
                    tagName: el.tagName,
                    role: el.getAttribute('role'),
                    className: el.className,
                    id: el.id,
                    placeholder: el.placeholder,
                    contentEditable: el.contentEditable,
                    html: el.outerHTML
                })));
                
                // Try different selectors
                const selectors = [
                    "[role='textbox']",
                    "div[contenteditable='true']",
                    "textarea",
                    "input[type='text']",
                    ".chat-input",
                    "#chat-input",
                    // Add more specific selectors based on the actual structure
                    "div.message-input",
                    "div.chat-textarea",
                    "[aria-label*='chat' i]",
                    "[aria-label*='message' i]",
                    "[placeholder*='message' i]",
                    "[placeholder*='type' i]"
                ];
                
                for (const selector of selectors) {
                    console.log('Trying selector:', selector);
                    const element = shadowRoot.querySelector(selector);
                    if (element) {
                        console.log('Found element:', element.outerHTML);
                        return {
                            found: true,
                            element: element,
                            selector: selector
                        };
                    }
                }
                
                // If no element found with specific selectors, try finding any input-like element
                const potentialInputs = allElements.filter(el => {
                    const tag = el.tagName.toLowerCase();
                    const isEditable = el.contentEditable === 'true';
                    const isTextInput = tag === 'input' && el.type === 'text';
                    const isTextarea = tag === 'textarea';
                    const hasTextboxRole = el.getAttribute('role') === 'textbox';
                    return isEditable || isTextInput || isTextarea || hasTextboxRole;
                });
                
                if (potentialInputs.length > 0) {
                    console.log('Found potential input:', potentialInputs[0].outerHTML);
                    return {
                        found: true,
                        element: potentialInputs[0],
                        selector: 'custom'
                    };
                }
                
                return { error: 'No chat input found' };
            """
            
            result = self.driver.execute_script(script)
            
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"Error from JavaScript: {result['error']}")
                    raise Exception(result['error'])
                elif result.get('found'):
                    print(f"Found chat input with selector: {result['selector']}")
                    return result['element']
            
            raise Exception("Could not find chat input with any known selector")
            
        except Exception as e:
            print(f"Error finding chat input: {str(e)}")
            self.driver.save_screenshot("chat_input_error.png")
            raise
    
    def analyze_chat_interface(self):
        """Analyze the structure of the chat interface for debugging."""
        print("\n=== Analyzing Chat Interface Structure ===")
        try:
            shadow_root = self.get_shadow_root()
            if not shadow_root:
                print("No shadow root found")
                return
            
            # Get all elements in the shadow root
            elements = shadow_root.find_elements(By.CSS_SELECTOR, "*")
            print(f"\nFound {len(elements)} elements in shadow root:")
            
            for element in elements:
                try:
                    tag_name = element.tag_name
                    text = element.text
                    classes = element.get_attribute("class")
                    id_attr = element.get_attribute("id")
                    role = element.get_attribute("role")
                    
                    print(f"\nElement: {tag_name}")
                    if id_attr:
                        print(f"ID: {id_attr}")
                    if classes:
                        print(f"Classes: {classes}")
                    if role:
                        print(f"Role: {role}")
                    if text:
                        print(f"Text: {text}")
                except:
                    continue
                    
        except Exception as e:
            print(f"Error analyzing chat interface: {str(e)}")
    
    def _wait_for_chat_interface(self):
        """Wait for the chat interface to be ready."""
        print("\nWaiting for chat interface to load...")
        try:
            shadow_root = self.get_shadow_root()
            WebDriverWait(self.driver, 10).until(
                lambda x: shadow_root and shadow_root.find_elements(By.CSS_SELECTOR, ".chat-container")
            )
            print("Chat interface loaded successfully")
        except TimeoutException:
            print("Warning: Timeout waiting for chat interface")
        except Exception as e:
            print(f"Error waiting for chat interface: {str(e)}")

    def send_message(self, message):
        """Send a message in the chat interface."""
        print(f"\n=== Starting message send process ===")
        print(f"Attempting to send message: {message}")
        
        try:
            # Wait longer for initial chat interface load
            time.sleep(3)
            
            shadow_root = self.get_shadow_root()
            if not shadow_root:
                raise Exception("Shadow root not found")

            # Find and fill the message input with retry logic
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Try different selectors for the input field
                    selectors = [
                        "textarea.text-input",  # More specific for Flowise
                        "textarea[class*='text-input']",
                        "textarea",
                        "input[type='text']",
                        "[contenteditable='true']",
                        "[role='textbox']"
                    ]
                    
                    message_input = None
                    for selector in selectors:
                        try:
                            elements = shadow_root.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed():
                                    message_input = element
                                    print(f"Found input field with selector: {selector}")
                                    break
                            if message_input:
                                break
                        except:
                            continue
                    
                    if not message_input:
                        raise Exception("Message input not found")
                    
                    # Clear and fill the input
                    message_input.clear()
                    message_input.send_keys(message)
                    time.sleep(0.5)  # Wait for input to register
                    
                    # Verify the message was entered correctly
                    input_value = self.driver.execute_script("""
                        const el = arguments[0];
                        return el.value || el.textContent;
                    """, message_input)
                    
                    if message not in input_value:
                        raise Exception("Message not entered correctly")
                    
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(1)
            
            # Find and click the send button using JavaScript
            print("Looking for send button...")
            send_button = self.driver.execute_script("""
                const shadowHost = document.querySelector('flowise-fullchatbot');
                if (!shadowHost || !shadowHost.shadowRoot) {
                    console.log('No shadow host or root found');
                    return null;
                }
                
                const root = shadowHost.shadowRoot;
                
                // Find the button with the send icon
                const buttons = Array.from(root.querySelectorAll('button'));
                const sendButton = buttons.find(btn => {
                    // Check if button contains an SVG with send-icon class
                    const svg = btn.querySelector('svg.send-icon');
                    if (!svg) return false;
                    
                    // Check if button is visible and enabled
                    const style = window.getComputedStyle(btn);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        return false;
                    }
                    if (btn.disabled) return false;
                    
                    return true;
                });
                
                if (sendButton) {
                    console.log('Found send button with SVG');
                    return sendButton;
                }
                
                // If not found, try finding any visible button
                const visibleButton = buttons.find(btn => {
                    const style = window.getComputedStyle(btn);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           style.opacity !== '0' &&
                           !btn.disabled;
                });
                
                if (visibleButton) {
                    console.log('Found visible button as fallback');
                    return visibleButton;
                }
                
                console.log('No suitable button found');
                return null;
            """)
            
            if not send_button:
                print("\nAnalyzing shadow root structure for debugging:")
                self.analyze_chat_interface()
                raise Exception("Send button not found with any selector")
            
            # Click the button using JavaScript for better reliability
            print("Clicking send button...")
            self.driver.execute_script("""
                const button = arguments[0];
                // First try standard click
                button.click();
                // Then try dispatching click event
                button.dispatchEvent(new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                }));
            """, send_button)
            time.sleep(1)  # Wait after click
            
            # Verify message was sent
            print("Message sent, waiting for it to appear...")
            time.sleep(2)  # Initial wait for message processing
            
            # Verify message was sent
            if not self.get_sent_message(message):
                print("Message not immediately visible, performing extended check...")
                time.sleep(2)  # Additional wait
                if not self.get_sent_message(message):
                    print("Warning: Message may not have been sent successfully")
                    return False
            
            print("Message sent and verified successfully")
            return True
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            self.driver.save_screenshot("send_message_error.png")
            return False
    
    def get_sent_message(self, message_text):
        """Get the sent message element with retry logic"""
        print(f"\nLooking for sent message: {message_text}")
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # First try exact message match
                if self.is_message_visible(message_text):
                    print(f"Found message on attempt {attempt + 1}")
                    return True
                
                # If exact match fails, try analyzing the interface
                if attempt % 2 == 0:  # Analyze every other attempt
                    self.analyze_chat_interface()
                
                # Wait before next attempt
                if attempt < max_attempts - 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_attempts - 1:
                    print("All attempts to find message failed")
                    self.driver.save_screenshot("find_message_error.png")
                    return False
                time.sleep(1)
        
        print("Message not found after all attempts")
        return False
    
    def get_chatbot_response(self):
        """Get the chatbot's response element"""
        try:
            shadow_root = self.get_shadow_root()
            return shadow_root.find_element(By.CSS_SELECTOR, ".message")
        except Exception as e:
            print(f"Error finding chatbot response: {str(e)}")
            self.driver.save_screenshot("response_error.png")
            raise
    
    def is_chat_input_visible(self):
        """Check if chat input is visible"""
        try:
            return self.wait_for_chat_input().is_displayed()
        except:
            return False
    
    def is_message_visible(self, message_text):
        """
        Check if a specific message is visible in the chat interface.
        
        Args:
            message_text (str): The text of the message to look for
            
        Returns:
            bool: True if the message is found, False otherwise
        """
        print(f"\nChecking if message is visible: {message_text}")
        max_attempts = 5
        attempt = 1
        
        while attempt <= max_attempts:
            try:
                # Get the shadow root
                shadow_host = self.driver.find_element(By.TAG_NAME, "flowise-fullchatbot")
                shadow_root = shadow_host.shadow_root
                
                # Find the chat view container
                chat_view = shadow_root.find_element(By.CLASS_NAME, "chatbot-chat-view")
                
                # Look for user messages with various possible class combinations
                user_message_selectors = [
                    "div.flex.flex-row.justify-end",  # User message container
                    "div[class*='flex'][class*='justify-end']",
                    "div[class*='user-message']",
                    "div[class*='user-bubble']",
                    "span[class*='user-bubble']",
                    "span[class*='chatbot-user-bubble']",
                    "div[class*='flex'][class*='justify-end'] span"  # Text within user message
                ]
                
                # Try each selector
                for selector in user_message_selectors:
                    try:
                        elements = chat_view.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if message_text in element.text:
                                print(f"Found message with selector: {selector}")
                                return True
                    except:
                        continue
                
                # If not found with specific selectors, search all elements
                print("\nSearching all elements in chat view...")
                all_elements = chat_view.find_elements(By.XPATH, ".//*")
                for element in all_elements:
                    try:
                        if message_text in element.text:
                            print(f"\nFound message in element:")
                            print(f"Tag: {element.tag_name}")
                            print(f"Classes: {element.get_attribute('class')}")
                            print(f"Text: {element.text}")
                            return True
                    except:
                        continue
                
                if attempt < max_attempts:
                    print(f"Message not found, waiting and retrying... (Attempt {attempt + 1}/{max_attempts})")
                    time.sleep(2)
                attempt += 1
                
            except Exception as e:
                print(f"Error checking message visibility: {str(e)}")
                if attempt < max_attempts:
                    time.sleep(2)
                attempt += 1
        
        print("Message not found after all attempts")
        return False
    
    def is_chatbot_response_visible(self):
        """Check if chatbot response is visible"""
        try:
            return self.get_chatbot_response().is_displayed()
        except:
            return False 