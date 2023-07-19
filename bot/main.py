#import
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from login import login
from crawler import initial_crawl, incremental_crawl
import config 
import argparse
import time

def main(crawl_type : str, is_headless : bool = True, is_demo_mode : bool = False, is_debug : bool = False):
    '''
    Main function
    :param crawl_type: the type of crawl to perform (initial or incremental)
    :param is_headless: whether to enable headless mode (no browser window)
    :return: None
    '''
    start_time = time.time()
    #Init default arguments
    options = Options()

    # Set headless mode
    if is_headless:
        # headless mode operations
        options.add_argument("--headless")

    # Init Selenium
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # Login to StudOn
    print("StudOn Login ...")
    login(driver=driver)
    print("Successfully logged in to StudOn")

    # Loop over each URL in the config file
    if crawl_type == 'initial':
        # initial_crawl function
        print("Initial Crawling...")
        _ = initial_crawl(driver=driver, url=config.START_PAGE_URL, is_demo_mode=is_demo_mode)
    elif crawl_type == 'incremental':
        # incremental_crawl function
        print("Incremental Crawling...")
        _ = incremental_crawl(driver=driver, url=config.START_PAGE_URL, is_demo_mode=is_demo_mode)

    print("--- %s seconds ---" % (time.time() - start_time))
    
if __name__ == '__main__':
    """
    Main function
    initial run: python main.py initial --debug --headless --demo
    incremental run: python crawler.py initial --debug --headless --demo

    """
    parser = argparse.ArgumentParser(description='Web Crawling Script')
    
    parser.add_argument('crawl_type', choices=['initial', 'incremental'], help='Type of crawl to perform')
    parser.add_argument('--headless', dest='is_headless', action='store_true', help='Enable headless mode')
    parser.add_argument('--demo', dest='is_demo_mode', action='store_true', help='Enable demo mode')
    parser.add_argument('--debug', dest='is_debug_mode', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    main(args.crawl_type, args.is_headless, args.is_demo_mode, args.is_debug_mode)