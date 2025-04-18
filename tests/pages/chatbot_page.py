from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

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
    
    def send_message(self, message):
        """Send a message to the chatbot"""
        try:
            chat_input = self.wait_for_chat_input()
            
            # Try to send message using JavaScript
            script = """
                const input = arguments[0];
                const message = arguments[1];
                
                // Function to try setting value and dispatching events
                const trySetValue = (method, value) => {
                    try {
                        input[method] = value;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    } catch (e) {
                        console.log(`Failed to set value using ${method}:`, e);
                        return false;
                    }
                };
                
                // Try different methods of setting the value
                const methods = ['value', 'textContent', 'innerHTML'];
                let success = false;
                
                for (const method of methods) {
                    if (trySetValue(method, message)) {
                        success = true;
                        break;
                    }
                }
                
                if (!success) {
                    // If all methods failed, try using execCommand
                    try {
                        input.focus();
                        document.execCommand('insertText', false, message);
                        success = true;
                    } catch (e) {
                        console.log('Failed to set value using execCommand:', e);
                    }
                }
                
                // Simulate Enter key press
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                });
                input.dispatchEvent(enterEvent);
                
                return success;
            """
            
            success = self.driver.execute_script(script, chat_input, message)
            
            if not success:
                raise Exception("Failed to send message using JavaScript")
            
            return self
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            self.driver.save_screenshot("send_message_error.png")
            raise
    
    def get_sent_message(self, message_text):
        """Get the sent message element"""
        try:
            shadow_root = self.get_shadow_root()
            return shadow_root.find_element(By.XPATH, f".//*[contains(text(), '{message_text}')]")
        except Exception as e:
            print(f"Error finding sent message: {str(e)}")
            self.driver.save_screenshot("sent_message_error.png")
            raise
    
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