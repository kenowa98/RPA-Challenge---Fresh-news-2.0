"""
------ Last modification ---------
Ken Owashi
22/05/2024 07:00
"""

from robocorp.tasks import task
from robocorp import workitems
from robocorp.workitems import Input

import re
import logging

from News import News

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task
def load_and_process_all_searches():
    """Load and process all search items."""
    try:
        for item in workitems.inputs:
            load_and_process_search(item)
    except Exception as err:
        print(err)
        workitems.inputs.current.fail(
            exception_type='APPLICATION',
            code='UNCAUGHT_ERROR',
            message=str(err)
            )

def load_and_process_search(work_item: Input):
    """Load and process a single search item."""
    search_phrase = work_item.payload['search_phrase']
    # category = work_item.payload['category'] # No usa categorías el buscador!!
    number_months = work_item.payload['number_months']

    logger.info(f"Processing search with phrase: {search_phrase}")
    
    try:
        news = News(search_phrase, number_months)
        news.generate_search_with_phrase(search_phrase)
        news.get_all_news()
        news.close_browser()
        work_item.done()
        logger.info("Search completed successfully.")
    except Exception as err:
        handle_exceptions(err, work_item)

def handle_exceptions(err, work_item: Input):
    error_message = str(err)
    logger.error(f"Exception occurred: {error_message}")
    
    if (re.search(r'\w+ with locator', error_message)
            and "not found" in error_message):
        work_item.fail(
            exception_type='APPLICATION',
            code='MISSING_ELEMENT',
            message=error_message
            )
    elif "web view not found" in error_message:
        work_item.fail(
            exception_type='APPLICATION',
            code='WINDOW_NOT_FOUND',
            message=error_message
            )
    else:
        work_item.fail(
            exception_type='APPLICATION',
            code='UNCAUGHT_ERROR',
            message=error_message
            )