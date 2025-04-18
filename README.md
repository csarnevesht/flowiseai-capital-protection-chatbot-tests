# Flowise Chatbot E2E Tests

This repository contains Selenium E2E tests for the Flowise chatbot.

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- ChromeDriver (will be automatically installed via webdriver-manager)

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:
```bash
python -m unittest tests/test_chatbot.py
```

To run a specific test:
```bash
python -m unittest tests.test_chatbot.ChatbotTests.test_chatbot_initial_load
```

## Test Structure

The tests follow the Selenium E2E testing guidelines and include:

1. `test_chatbot_initial_load`: Verifies the chatbot interface loads correctly
2. `test_send_message`: Tests sending a message to the chatbot
3. `test_chatbot_response`: Verifies the chatbot responds to messages

## Notes

- Tests are configured to wait up to 10 seconds for elements to appear
- Screenshots are automatically captured on test failure
- The tests use semantic locators where possible, following ARIA roles 