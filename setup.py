from setuptools import setup, find_packages

setup(
    name="chatbot-tests",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "selenium==4.18.1",
        "webdriver-manager==4.0.1",
    ],
) 