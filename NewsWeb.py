"""
------ Last modification ---------
Ken Owashi
22/05/2024 07:00
"""

from robocorp import storage

from RPA.Browser.Selenium import Selenium

import time
import logging

class NewsWeb:
    def __init__(self) -> None:
        self.urls = storage.get_json("URLs")
        self.pauses  = storage.get_json("Pauses")
        self.retries = storage.get_json("Retries")
        self.elements = storage.get_json("Elements")

        self.selenium = Selenium()
    
    def initialize(self):
        """Initialize the NewsWeb instance by opening the news website."""
        try:
            self.open_news_web()
        except Exception as err:
            if str(err) == "Website unavailable":
                logging.error(f"Website unavailable error: {err}")
                raise Exception(
                    "Bot could not Initialize due to website unavailability"
                    )
            else:
                logging.error(f"An unexpected error occurred: {err}")

    def open_news_web(self):
        """Open the news website in a Chrome browser."""
        try:
            self.selenium.open_chrome_browser(
                url=self.urls["newsWebsite"],
                maximized=True
                )
            logging.info("Browser opened successfully.")
        except Exception as err:
            self.save_error_evidence()
            logging.error(f"An unexpected error occurred while opening browser: {err}")
            raise Exception(err)

    def generate_search_with_phrase(self, phrase):
        try:
            self.selenium.click_button(self.elements["button_accept_all"])
            time.sleep(self.pauses["short"])
        except:
            logging.info("Do not appear pop up.")
        
        try:
            self.selenium.wait_until_element_is_visible(self.elements["search_bar"])
            self.selenium.input_text(self.elements["search_bar"], phrase)
            self.selenium.click_button(self.elements["search_button"])
            wait_until_keyword_succeeds(
                self.retries['normalTask'], self.pauses["short"],
                self.navigate_news_section
                )
        except Exception as err:
            self.save_error_evidence()
            logging.error(f"An unexpected error occurred while searching the phrase: {err}")
            raise Exception(err)

    def navigate_news_section(self):
        try:
            windows = self.selenium.get_window_handles()
            self.selenium.switch_window(windows[1])      
            self.selenium.click_element(self.elements["tab_news"])
            time.sleep(self.pauses["short"])
        except Exception as err:
            self.save_error_evidence()
            logging.error(f"An unexpected error occurred while navigating to news section: {err}")
            raise Exception(err)

    def next_page(self): 
        try:
            self.selenium.click_element(self.elements["button_next"])
            time.sleep(self.pauses["short"])
        except Exception as err:
            self.save_error_evidence()
            logging.error(f"An unexpected error occurred while navigating to next page: {err}")
            raise Exception(err)
    
    def close_browser(self):
        self.selenium.close_all_browsers()
    
    def save_error_evidence(self):
        self.selenium.screenshot("output/error_screenshot.png")
        

def wait_until_keyword_succeeds(retries: int, interval: int, function, *args):
    """Retry executing a function until it succeeds or reaches the maximum retries."""
    error = ""

    for _ in range(retries):
        try:
            function(*args)
            return
        except Exception as e:
            error = e
            time.sleep(interval)
    raise Exception(
        f"Keyword '{function.__name__}' did not succeed after {retries} attempts with these args:[{args}] - Error: {error}"
        )

logging.basicConfig(level=logging.INFO)