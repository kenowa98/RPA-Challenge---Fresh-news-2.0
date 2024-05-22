"""
------ Last modification ---------
Ken Owashi
22/05/2024 07:00
"""

import re
import os
import time
import zipfile
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from NewsWeb import NewsWeb

MAX_NO_VALID_NEWS = 3 # The bot stops reading news if there are 3 in a row that do not meet the search criteria
MAX_NEWS = 500 # A search limit of no more than 500 news (personal configuration)

class News(NewsWeb):
    def __init__(self, phrase, period) -> None:
        super().__init__()
        self.initialize()

        self.phrase = phrase
        self.count_rows = 1
        self.no_valid_news = 0
        self.register = pd.DataFrame(columns=['Title', 'Source', 'Date',
                                              'Description', 'Link', 'Picture filename',
                                              'Ocurrences search phrase', 'Contains any amount of money'])
        
        # A search limit of no more than 1 year is established (personal configuration)
        if period == 0 or period == 1:
            self.period = 0
        else:
            if period > 12:
                self.period = 12
            else:
                self.period = period - 1
    
    def get_all_news(self):
        """Collect all news articles based on search criteria."""
        while self.count_rows < MAX_NEWS:
            news = self.selenium.get_webelements(self.elements["all_news"])
            news_dates = self.selenium.get_webelements(self.elements["all_news_date"])
            news_links = self.selenium.get_webelements(self.elements["all_news_link"])
            news_sources = self.selenium.get_webelements(self.elements["all_news_source"])
            news_descriptions = self.selenium.get_webelements(self.elements["all_news_description"])
            
            for index, item in enumerate(news):
                date = re.search(r'(\d+\s\w+\sago)', news_dates[index].text).group(1)

                if self.validate_date(date):
                    title = news_links[index].get_attribute("title")
                    
                    if title is None or title == "":
                        title = news_links[index].text

                    if self.validate_item(title):
                        url = news_links[index].get_attribute("href")
                        source = news_sources[index].text
                        description = news_descriptions[index].text
                        
                        self.analyze_and_register_data_news(item, title, url, source, date, description)
               
            try:
                if self.no_valid_news >= MAX_NO_VALID_NEWS:
                    break
                self.no_valid_news = 0
                self.next_page()
            except:
                break

        self.store_excel_and_images()
            
    def validate_date(self, date):
        """Validate if the news article date falls within the specified period."""
        if re.search(r'days?|hours?|minutes?|seconds?', date):
            valid_date = True
        elif re.search(r'months?', date):
            months_match = re.search(r'(\d+)\smonths?\sago', date)
            months = int(months_match.group(1))
            if months <= self.period:
                valid_date = True
            else:
                valid_date = False
                self.no_valid_news += 1
        else:
            valid_date = False
            self.no_valid_news += 1

        return valid_date
    
    def validate_item(self, title):
        """Validate if the news article has been already registered."""
        if title in self.register['Title'].values:
            self.no_valid_news += 1
            return False
        return True

    def analyze_and_register_data_news(self, *args):
        date = self.format_date(args[4])
        
        occurrences  = args[1].lower().count(self.phrase.lower())
        occurrences += args[5].lower().count(self.phrase.lower())

        pattern_money  = r'\$[\d,.]+|\d+\s?(dollars|USD)\b'
        contains_money = bool(re.search(pattern_money, f'{args[1]}  {args[5]}'))

        img_file = f"screenshot-{self.count_rows}.png"
        self.selenium.screenshot(args[0], f"output/pictures/{img_file}")
        time.sleep(self.pauses["super_short"])

        new_register = pd.DataFrame({'Title': args[1], 'Source': args[3], 'Date': date,
                                    'Description': args[5], 'Link': args[2], 'Picture filename': img_file,
                                    'Ocurrences search phrase': occurrences, 'Contains any amount of money': contains_money},
                                    index=[0])
        self.register = pd.concat([new_register, self.register.loc[:]]).reset_index(drop=True)

        self.count_rows += 1
    
    def format_date(self, date):
        if re.search(r'days?', date):
            days_match = re.search(r'(\d+)\sdays?\sago', date)
            days = int(days_match.group(1))
            date = datetime.now() - timedelta(days=days)
            date = date.strftime('%d/%m/%Y')
        elif re.search(r'months?', date):
            months_match = re.search(r'(\d+)\smonths?\sago', date)
            months = int(months_match.group(1))
            date = datetime.now() - relativedelta(months=months)
            date = date.strftime('%b/%Y')
        else:
            date = datetime.now().strftime('%d/%m/%Y')
        
        return date

    def store_excel_and_images(self):
        if self.count_rows > 1:
            self.register.to_excel(f"output/{self.phrase}_{datetime.now().strftime('%d-%m-%Y %H_%M')}.xlsx", index=False)
            
            directory = 'output/pictures'
            zip_name  = 'output/pictures.zip'

            with zipfile.ZipFile(zip_name, 'w') as zipf:
                for root, _, files in os.walk(directory):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))