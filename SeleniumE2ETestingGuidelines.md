
# Selenium E2E Testing Guidelines

## Test Structure and Organization

- Store all tests under a `tests/` directory  
- Name test files based on the system module or functionality being tested (not the component or page name)  
- Group related tests into classes or `pytest` modules with descriptive names  
- Use descriptive test method names to reflect the purpose of each test  
- For authenticated tests, use a login helper or setup method to establish session state  
- Use Page Object Model Design Pattern.
- Use separate folders for screenshots, environments, test data, etc.

## Locator Strategy

1. Prefer semantic locators using ARIA roles via  
   ```python
   find_element(By.XPATH, "//*[@role='textbox']")
   ```
2. Use visible text (`By.LINK_TEXT`, `By.XPATH` with `text()`) or label/placeholder matching  
3. Use `data-testid` or other unique attributes only when semantic selectors are unreliable  

## Writing Tests

- Test from a user’s perspective, focusing on visible behaviors rather than internal implementation  
- Ensure each test is isolated and can run independently  
- Use `setUp` / `setup_method` for common setup  
- Avoid shared state between test cases or classes  
- Minimize use of `execute_script()` unless necessary for triggering JS-heavy behavior  

## Assertions

- Use explicit `WebDriverWait` and `expected_conditions` for waiting on elements  
- Prefer assertions that confirm the visible state (e.g., element is displayed, text matches)  
- Use soft assertions or warnings for non-blocking verifications when appropriate  

## Handling Asynchronous Operations

- Always use `WebDriverWait` for elements that load dynamically  
- Avoid `time.sleep()`; rely on Selenium's expected conditions  
- For complex UI states, use custom `wait_until` helper functions  

## Test Data Management

- Use utility functions or factories to generate test data dynamically  
- Avoid hardcoding data directly in test methods  
- Use fixtures or setup scripts for complex test data preconditions  

## Performance and Stability

- Keep each test short and focused  
- Don’t over-assert or interact with irrelevant parts of the page  
- Mark inherently slow tests (e.g., file uploads) for optional/slow runs  
- Add retry decorators for tests prone to intermittent failure (with caution)  

## Cross-browser Testing

- Use Selenium Grid or cloud providers (e.g., BrowserStack, Sauce Labs) to test across browsers  
- Parametrize tests to run against different browser configurations  
- Parallelize test execution using tools like `pytest-xdist` or test runners that support threading  

## Debugging and Maintenance

- Use `@unittest.skip`, `@pytest.mark.skip`, or selective test runs for focusing during dev  
- Capture screenshots or logs on failure using  
  ```python
  driver.get_screenshot_as_file("failure.png")
  ```  
- Document complex test logic with inline comments or docstrings  

---

## Example Test Structure (Selenium with `unittest` in Python)

```python
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TodoListTests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://demo.playwright.dev/todomvc")

    def tearDown(self):
        self.driver.quit()

    def test_add_new_todo_item(self):
        driver = self.driver
        input_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='What needs to be done?']"))
        )
        input_box.send_keys("New todo item" + Keys.ENTER)

        items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.todo-list li"))
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].text, "New todo item")

    def test_mark_todo_as_completed(self):
        driver = self.driver
        input_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='What needs to be done?']"))
        )
        input_box.send_keys("Task to complete" + Keys.ENTER)

        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.toggle"))
        )
        checkbox.click()

        completed_item = driver.find_element(By.CSS_SELECTOR, "ul.todo-list li")
        self.assertIn("completed", completed_item.get_attribute("class"))

if __name__ == "__main__":
    unittest.main()
```