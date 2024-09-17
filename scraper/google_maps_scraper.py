from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from io import StringIO

class GoogleMapsScraper:
    def __init__(self):
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
        options.add_argument('--headless')  # Remove or comment out this line for debugging
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service("./chromedriver.exe"), options=options)
        return driver

    def scrape(self, query, max_results=100, max_pages=5):
        self.driver.get(f"https://www.google.com/maps/search/{query}")

        wait = WebDriverWait(self.driver, 10)
        time.sleep(5)  # Wait for the page to load

        results = []
        for i in range(max_pages):  # Loop through a fixed number of pages
            if len(results) >= max_results:
                break

            print(f"Scraping page {i+1}...")
            try:
                businesses = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.hfpxzc')))
                print(f"Found {len(businesses)} businesses on this page.")
            except TimeoutException:
                print("Timeout: No businesses found.")
                break

            for business in businesses:
                try:
                    business_name = business.get_attribute('aria-label')

                    # Skip sponsored businesses
                    try:
                        sponsored = business.find_element(By.XPATH, ".//span[contains(text(), 'Sponsored')]")
                        if sponsored:
                            print("Skipping sponsored business...")
                            continue
                    except NoSuchElementException:
                        pass  # No "Sponsored" label found, proceed normally

                    # Skip businesses with "· Visited link" in the name
                    if "· Visited link" in business_name:
                        print(f"Skipping business: {business_name}")
                        continue

                    print(f"Clicking on {business_name}")
                    business.click()
                    time.sleep(5)  # Wait for the pane to load

                    # Scrape phone number
                    address = self._get_element_text("//div[contains(@class, 'AeaXub')]//div[contains(@class, 'Io6YTe')]")

                    # Scrape website
                    website = self._get_element_attribute("//a[@aria-label and contains(@aria-label, 'Website')]", 'href')

                    results.append({'Name': business_name, 'Address': address, 'Website': website})
                    print(f"Scraped: {business_name}, {address}, {website}")

                    # Go back to the list
                    self.driver.execute_script("window.history.go(-1)")
                    time.sleep(5)  # Wait for the page to reload

                    # Re-locate businesses after coming back
                    businesses = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.hfpxzc')))

                except StaleElementReferenceException:
                    print(f"Stale element reference error encountered. Retrying...")
                    continue  # Continue to the next business

                except Exception as e:
                    print(f"Error: {e}")
                    continue

            # Scroll down to load more results
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Wait for more results to load

        self.driver.quit()
        return self._create_csv_string(results)

    def _get_element_text(self, xpath):
        try:
            return self.driver.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            return 'N/A'

    def _get_element_attribute(self, xpath, attribute):
        try:
            return self.driver.find_element(By.XPATH, xpath).get_attribute(attribute)
        except NoSuchElementException:
            return 'N/A'

    def _create_csv_string(self, results):
        df = pd.DataFrame(results)
        output = StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()