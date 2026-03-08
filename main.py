import logging
import pathlib
import platform
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchWindowException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

def get_browser_choice():
    browsers = {"1": "chrome", "2": "firefox", "3": "edge"}
    print("Select browser:")
    print("  1) Chrome (default)")
    print("  2) Firefox")
    print("  3) Edge")
    while True:
        choice = input("Enter choice [1/2/3] (default: 1): ").strip()
        if not choice or choice == "x":
            return "chrome"
        if choice in browsers:
            return browsers[choice]
        print("Invalid choice. Enter 1, 2, or 3.")

def create_driver(browser, profile_path):
    if browser == "chrome":
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        opts = ChromeOptions()
        opts.add_argument(f"user-data-dir={profile_path}")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    elif browser == "firefox":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager
        opts = FirefoxOptions()
        opts.add_argument(f"-profile")
        opts.add_argument(str(profile_path))
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=opts)
    elif browser == "edge":
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumManager
        opts = EdgeOptions()
        opts.add_argument(f"user-data-dir={profile_path}")
        return webdriver.Edge(service=EdgeService(EdgeChromiumManager().install()), options=opts)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

def get_int_input(prompt, default):
    while True:
        try:
            inp = input(f"{prompt} (default: {default}) [x]: ")
            if not inp or inp.lower() == "x":
                return default
            value = int(inp)
            if value <= 0:
                print("Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_float_input(prompt, default):
    while True:
        try:
            inp = input(f"{prompt} (default: {default}) [x]: ")
            if not inp or inp.lower() == "x":
                return default
            value = float(inp)
            if value <= 0:
                print("Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

logging.basicConfig(format="[%(levelname)s] Instagram Cleaner: %(message)s", level=logging.INFO)

print("---- Instagram Bulk Comment Cleaner ----")
BROWSER = get_browser_choice()
SELECTIONS_AT_ONCE = get_int_input("How many comments to select (per batch)?", 5)
DELAY_BETWEEN_SELECTS = get_float_input("Delay (seconds) between each selection?", 2.0)
DELAY_AFTER_BATCH_DELETE = get_float_input("Delay (seconds) after each batch deletion?", 10.0)
CHECK_EVERY = get_float_input("If rate limit hit, wait how many hours before retry? ", 1.0) * 3600
MODE = 1  # 1 = comments, 2 = likes
print("----------------------------------------")

LIKES_URL = "https://www.instagram.com/your_activity/interactions/likes"
COMMENTS_URL = "https://www.instagram.com/your_activity/interactions/comments"

logging.info("Starting script...")

driver = None
try:
    wd = pathlib.Path().absolute()
    if platform.system() == "Windows":
        profile_path = str(wd / f"{BROWSER}-profile")
    else:
        profile_path = f"{BROWSER}-profile"
    driver = create_driver(BROWSER, profile_path)
    logging.info(f"{BROWSER.capitalize()} browser launched")
    URL = COMMENTS_URL if MODE == 1 else LIKES_URL
    driver.get(URL)
    logging.info(f"Opening page: {URL}")
    # Wait for user to log in manually
    while True:
        if driver.current_url.startswith(URL):
            logging.info("Login detected")
            break
        try:
            logging.info("Waiting for login (log in from the browser and don't click anything else)...")
            wait = WebDriverWait(driver, 60)
            def is_not_now_button_present(driver):
                try:
                    div = driver.find_element(By.CSS_SELECTOR, "div[role='button']")
                    return div.text in ["Not now", "Plus tard"]
                except:
                    return False
            wait.until(is_not_now_button_present)
            driver.find_element(By.CSS_SELECTOR, "div[role='button']").send_keys(Keys.ENTER)
            logging.info("Clicked 'Not now'")
            break
        except TimeoutException:
            pass
    # Main loop
    total_deleted = 0
    batch_number = 1
    while True:
        is_clicked_select = False
        wait_attempts = 0
        max_wait_attempts = 10
        while not is_clicked_select:
            logging.info("Waiting for elements to load...")
            time.sleep(2)
            # Check for 'Something went wrong' error (English and French)
            error_elements_en = driver.find_elements(By.XPATH, "//*[contains(text(), \"Something went wrong\")]")
            error_elements_fr = driver.find_elements(By.XPATH, "//*[contains(text(), \"Une erreur s'est produite\")]")
            if error_elements_en or error_elements_fr:
                logging.warning("'Something went wrong' detected. Refreshing page and retrying...")
                driver.refresh()
                time.sleep(5)
                wait_attempts = 0
                continue
            elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-bloks-name="bk.components.Text"]')
            for el in elements:
                if el.text in ["Select", "Sélectionner"]:
                    if any(txt.text in ["No results", "Aucun résultat"] for txt in elements):
                        logging.info("No items found. Finished.")
                        driver.quit()
                        sys.exit(0)
                    driver.execute_script("arguments[0].click();", el)
                    logging.info("Clicked 'Select'")
                    is_clicked_select = True
                    break
            wait_attempts += 1
            if wait_attempts >= max_wait_attempts:
                logging.warning("Elements not found after several attempts. Refreshing page and retrying...")
                driver.refresh()
                time.sleep(5)
                wait_attempts = 0
                continue
        selected_count = 0
        attempts = 0
        refreshed = False
        while selected_count < SELECTIONS_AT_ONCE:
            if refreshed:
                break
            time.sleep(DELAY_BETWEEN_SELECTS)
            for checkbox in driver.find_elements(By.CSS_SELECTOR, '[aria-label="Toggle checkbox"]'):
                try:
                    if not checkbox.is_selected():
                        driver.execute_script("arguments[0].click();", checkbox)
                        selected_count += 1
                        logging.info(f"Selected item (Total: {selected_count})")
                        if selected_count >= SELECTIONS_AT_ONCE:
                            break
                except StaleElementReferenceException:
                    continue
            attempts += 1
            if attempts > 10:
                logging.warning("Possible UI issue or limit. Could not select items. Skipping batch...")
                time.sleep(2)
                break
        # Click Delete/Unlike
        deleted_this_batch = False
        for span in driver.find_elements(By.CSS_SELECTOR, 'span[data-bloks-name="bk.components.TextSpan"]'):
            if span.text in (["Delete", "Supprimer"] if MODE == 1 else ["Unlike", "Je n’aime plus"]):
                time.sleep(1)
                driver.execute_script("arguments[0].click();", span)
                logging.info(f"Clicked '{span.text}' to confirm deletion (Batch #{batch_number})")
                deleted_this_batch = True
                break
        # Confirm the deletion
        confirmed = False
        while not confirmed and deleted_this_batch:
            time.sleep(1)
            for btn in driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"] button'):
                try:
                    confirmation_text = btn.find_element(By.CSS_SELECTOR, "div").text
                    if confirmation_text in ["Delete", "Unlike", "Supprimer", "Je n’aime plus"]:
                        driver.execute_script("arguments[0].click();", btn)
                        logging.info(f"Confirmed '{confirmation_text}'")
                        total_deleted += selected_count
                        logging.info(f"Deleted {selected_count} comments in batch #{batch_number}. Total deleted: {total_deleted}")
                        batch_number += 1
                        confirmed = True
                        break
                except StaleElementReferenceException:
                    continue
            if not confirmed:
                time.sleep(1)
        logging.info(f"Waiting {DELAY_AFTER_BATCH_DELETE} seconds before next batch...")
        time.sleep(DELAY_AFTER_BATCH_DELETE)  # Extra delay for safety
except KeyboardInterrupt:
    logging.info("Script manually interrupted.")
    if driver:
        driver.quit()
    sys.exit(0)
except NoSuchWindowException:
    logging.exception("Browser window was closed.")
    sys.exit(1)
except Exception as e:
    logging.exception("Unexpected error:")
    try:
        driver.quit()
    except:
        pass
    sys.exit(1)