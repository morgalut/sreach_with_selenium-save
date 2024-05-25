"# sreach_with_selenium-save" 
# Website Content Scraper

This Python script allows you to scrape content from websites and save it to a database or CSV file. It utilizes Selenium for web scraping and BeautifulSoup for parsing HTML content.

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup
- Chrome WebDriver (or any other WebDriver for the browser of your choice)

## Installation

1. Clone or download the repository to your local machine.

2. Install the required Python packages using pip:

    ```
    pip install selenium beautifulsoup4
    ```

3. Download and install the WebDriver for your preferred browser:
   
   - For Edge: [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
   - For other browsers: [WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads), [WebDriver for Firefox](https://github.com/mozilla/geckodriver/releases), etc.

## Usage

1. Set up the Edge WebDriver path and other configurations in the script (`scraper.py`).

2. Customize the list of keywords, skip list, or any other parameters as needed.

3. Run the script:

    ```
    python scraper.py
    ```

## Functionality

- The script fetches browsing history from Microsoft Edge (you can modify it for other browsers).
- It extracts content from visited URLs and filters it based on keywords and custom rules.
- Extracted content is saved to a SQLite database and a CSV file.
- Error logs are stored in `error_log.log`.

## Customization

You can customize the following aspects of the script:

- Keywords: Define specific keywords to filter content.
- Skip list: Skip certain websites or URLs from processing.
- Content extraction rules: Modify the `extract_main_content` function to adjust content filtering based on HTML structure or other criteria.

