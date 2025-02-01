import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def fetch_notices(download_dir):
    try:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--headless")

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        chromedriver_path = r"C:\Users\Piyush sinha\Downloads\Compressed\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}")

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        url = "https://www.imsnsit.org/imsnsit/notifications.php"
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.list-data-focus a"))
        )

        elements = driver.find_elements(By.CSS_SELECTOR, "td.list-data-focus a")
        links = [elem.get_attribute("href") for elem in elements[:10] if elem.get_attribute("href")]

        notices = [{"title": elem.text, "link": href} for elem, href in zip(elements[:10], links)]

        selenium_cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in selenium_cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        driver.quit()

        headers = {
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                          "AppleWebKit/537.36 (KHTML, like Gecko) " +
                          "Chrome/113.0.0.0 Safari/537.36"
        }

        for notice in notices:
            link = notice['link']
            try:
                response = session.get(link, headers=headers, stream=True, timeout=120)
                response.raise_for_status()

                if 'Content-Disposition' in response.headers:
                    filename = response.headers.get('Content-Disposition').split('filename=')[-1].strip('"')
                else:
                    filename = os.path.basename(link) or "downloaded_file"
                filename = sanitize_filename(filename)
                file_path = os.path.join(download_dir, filename)

                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                notice['filename'] = filename
            except Exception as e:
                notice['error'] = str(e)

        return notices

    except Exception as e:
        print(f"Error fetching notices: {e}")
        return {"error": str(e)}