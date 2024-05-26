import logging
import sqlite3
import os
import shutil
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import re
import urllib.request
import json
import csv
from bs4 import BeautifulSoup
from docx import Document

# Path to msedgedriver.exe
edge_driver_path = "C:\\webDravier\\msedgedriver.exe"

# Setting up logging configuration
logging.basicConfig(filename='error_log.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Setting up the Edge WebDriver with logging enabled
service = Service(edge_driver_path)
options = webdriver.EdgeOptions()
options.add_argument('--enable-logging')
options.add_argument('--v=1')
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

driver = webdriver.Edge(service=service, options=options)

# Function to create or connect to the SQLite database for saving content
def create_content_db():
    conn = sqlite3.connect('website_content.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

# Function to save website content to the database
def save_website_content(conn, url, content):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO content (url, content) VALUES (?, ?)', (url, content))
    conn.commit()

# Function to log JSON errors
def log_json_errors(logs):
    for entry in logs:
        log = json.loads(entry['message'])['message']
        if 'params' in log and 'response' in log['params']:
            if log['params']['response'].get('status', 0) >= 400:
                logging.error(f"JSON Error: {log}")

# Function to save content to a CSV file
def save_content_to_csv(url, content):
    with open('website_content.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([url, content])

# Function to fetch and save readable content from a URL
def fetch_and_save_content(driver, url):
    try:
        driver.get(url)
        page_source = driver.page_source  # Get page source content

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(page_source, 'lxml')

        # Extract readable content
        content = extract_main_content(soup)

        # Save content to the database
        save_website_content(conn, url, content)

        # Save content to CSV file
        save_content_to_csv(url, content)

        # Check for JSON errors
        logs = driver.get_log('performance')
        log_json_errors(logs)
    except Exception as e:
        logging.error(f"Error fetching content from {url}: {e}")

# Keywords for filtering content
keywords = [
    'Python', 'Selenium', 'Web scraping', 'Data analysis', 'Java', 'JavaScript', 'C', 'C++', 'C#', 'Ruby', 
    'Swift', 'Kotlin', 'Go', 'PHP', 'Perl', 'Rust', 'TypeScript', 'SQL', 'HTML', 'CSS', 'R', 'MATLAB', 'Lua', 
    'Shell scripting', 'Dart', 'Scala', 'Groovy', 'VBScript', 'PowerShell', 'Objective-C', 'Assembly', 
    'Visual Basic', 'Cobol'
]

# Function to extract the main content from a BeautifulSoup object
def extract_main_content(soup):
    content = ''
    code_snippets = ''

    # Extract code snippets from <pre> and <code> tags
    pre_tags = soup.find_all('pre')
    code_tags = soup.find_all('code')

    for tag in pre_tags:
        code_text = tag.get_text(strip=True)
        if len(code_text.split()) > 5:
            code_snippets += code_text + '\n'

    for tag in code_tags:
        code_text = tag.get_text(strip=True)
        if len(code_text.split()) > 5:
            code_snippets += code_text + '\n'

    # Combine code snippets with other main content if available
    main_content_tags = soup.find_all(['article', 'section'])
    if not main_content_tags:
        main_content_tags = soup.find_all('div', class_=['main-content', 'content', 'post', 'entry'])

    for tag in main_content_tags:
        for sub_tag in tag.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = sub_tag.get_text(strip=True)
            if len(text.split()) > 5:
                content += text + '\n'

    # Fallback to extract content from all paragraphs and headings if no specific tags found
    if not content:
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = tag.get_text(strip=True)
            if len(text.split()) > 5:
                content += text + '\n'

    # Prioritize returning code snippets if available
    if code_snippets:
        return code_snippets

    # Filter content by keywords
    for keyword in keywords:
        if keyword.lower() in content.lower():
            return content

    return content if content else code_snippets

    # If none of the keywords are found, return an empty string
    return ''

# Function to read and extract content from a DOC file
def extract_content_from_doc(file_path):
    doc = Document(file_path)
    content = ''
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if len(text.split()) > 5:  # Rule: Keep only content with more than 5 words
            content += text + '\n'
    return content

# Function to get Edge browsing history
def get_edge_history():
    history_db_path = os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History')
    temp_db_path = os.path.expanduser('~\\AppData\\Local\\Temp\\EdgeHistory')

    # Copy the history file to a temporary location to avoid locking issues
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    shutil.copy2(history_db_path, temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC")

    urls = cursor.fetchall()
    conn.close()
    return urls

# Function to download and save DOC files from URLs
def download_doc_file(driver, url):
    try:
        driver.get(url)
        iframe = driver.find_element(By.ID, "office_iframe")
        src = iframe.get_attribute("src")
        m = re.search(r'.*?url=(.+?)/vector-output', src)
        if m:
            doc_url = m.group(1)
            local_filename = os.path.join('downloaded_docs', os.path.basename(doc_url))
            urllib.request.urlretrieve(doc_url, local_filename)
            return local_filename
    except Exception as e:
        logging.error(f"Error downloading DOC file from {url}: {e}")
    return None

# List of websites to skip
skip_list = [
    "https://translate.google.com",
    "https://www.google.co.uk/",
    "https://www.bing.com"
]

# Function to check if a URL should be skipped
def should_skip(url):
    for skip_url in skip_list:
        if url.startswith(skip_url):
            return True
    return False

# Main script execution
if __name__ == "__main__":
    conn = create_content_db()
    try:
        # Create a directory for downloaded DOC files if it doesn't exist
        if not os.path.exists('downloaded_docs'):
            os.makedirs('downloaded_docs')

        # Fetch browsing history from Edge
        history = get_edge_history()

        # Limit the number of URLs to process for demo purposes
        history_limit = 100
        processed_count = 0  # Counter for processed URLs

        for url_data in history:
            if processed_count >= history_limit:
                break

            url = url_data[0]
            if should_skip(url):
                print(f"Skipping {url}")
                continue

            if "OfficePreview" in url and url.endswith(".docx"):
                print(f"Downloading DOC file from {url}")
                doc_file_path = download_doc_file(driver, url)
                if doc_file_path:
                    print(f"Fetching content from DOC file: {doc_file_path}")
                    doc_content = extract_content_from_doc(doc_file_path)
                    if doc_content:
                        # Save DOC content to the database and CSV file
                        save_website_content(conn, doc_file_path, doc_content)
                        save_content_to_csv(doc_file_path, doc_content)
            else:
                print(f"Fetching content from {url}")
                fetch_and_save_content(driver, url)
            processed_count += 1  # Increment the counter only if the URL is processed

    finally:
        driver.quit()
        conn.close()
