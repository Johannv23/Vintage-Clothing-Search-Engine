from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.keys import Keys
import time
import random

def process_grailed_item(result):
    """Extracts data from a single Grailed product listing."""
    try:
        title = result.find_element(By.CSS_SELECTOR, "p.ListingMetadata-module__title___Rsj55").text
    except Exception:
        title = "Not found"

    try:
        size = result.find_element(By.CSS_SELECTOR, "p.ListingMetadata-module__size___e9naE").text
    except Exception:
        size = "Not found"

    try:
        price = result.find_element(By.CSS_SELECTOR, "span.Price-module__onSale___1pIHp").text
    except Exception:
        price = "Not found"

    try:
        image_url = result.find_element(By.CSS_SELECTOR, "img.Image-module__crop___nWp1j").get_attribute("src")
    except Exception:
        image_url = "Not found"

    try:
        product_link = result.find_element(By.CSS_SELECTOR, "a.listing-item-link").get_attribute("href")
    except Exception:
        product_link = "Not found"

    return {
        "title": title,
        "size": size,
        "price": price,
        "image_url": image_url,
        "product_link": product_link,
    }


def scrape_grailed(search_query):
    """Scrapes the first 10 listings from Grailed for a given search query using multi-threading."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Program Files/ChromeDriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navigate to Grailed homepage
        url = "https://www.grailed.com/"
        print(f"Navigating to URL: {url}")
        driver.get(url)

        time.sleep(3)

        # Click the search bar to trigger the sign-in pop-up
        search_input = driver.find_element(By.ID, "header_search-input")
        search_input.click()
        print("Clicked on the search bar to trigger the sign-in pop-up.")

        # Dismiss the sign-in pop-up using JavaScript
        try:
            driver.execute_script(
                "document.querySelector('.ReactModal__Overlay').style.display='none';"
            )
            print("Sign-in pop-up removed using JavaScript.")
        except Exception:
            print("Failed to remove pop-up.")

        # Retry clicking the search bar
        search_input.click()
        print("Clicked on the search bar again after dismissing the pop-up.")

        # Enter the search query
        search_input.send_keys(search_query)
        print(f"Entered search query: {search_query}")

        # Submit the search
        search_button = driver.find_element(By.CSS_SELECTOR, "button[title='Submit']")
        search_button.click()
        print("Search button clicked.")

        time.sleep(5)

        # Verify if search results loaded
        results = driver.find_elements(By.CLASS_NAME, "feed-item")
        print(f"Found {len(results)} search results.")

        scraped_results = []
        # Use ThreadPoolExecutor for concurrent scraping of product listings
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust threads if necessary
            futures = [executor.submit(process_grailed_item, result) for result in results[:10]]

            for future in as_completed(futures):
                scraped_results.append(future.result())

    except Exception as e:
        print(f"Error extracting products: {e}")
        scraped_results = []
    finally:
        driver.quit()

    return scraped_results


def process_depop_item(product):
    """Extracts data from a single Depop product."""
    try:
        title = product.find_element(By.CSS_SELECTOR, "p.styles__StyledBrandNameText-sc-ec533c9e-21").text
    except Exception:
        title = "Not found"

    try:
        price = product.find_element(By.CSS_SELECTOR, "p[aria-label='Price'].Price-styles__FullPrice-sc-1c510ed0-0").text
    except Exception:
        price = "Not found"

    try:
        size = product.find_element(By.CSS_SELECTOR, "p[aria-label='Size'].styles__StyledSizeText-sc-ec533c9e-12").text
    except Exception:
        size = "Not found"

    try:
        image_url = product.find_element(By.CSS_SELECTOR, "img.sc-hjbplR").get_attribute("src")
    except Exception:
        image_url = "Not found"

    try:
        link = product.find_element(By.CSS_SELECTOR, "a.styles__ProductCard-sc-ec533c9e-4").get_attribute("href")
    except Exception:
        link = "Not found"

    return {
        "title": title,
        "price": price,
        "size": size,
        "image_url": image_url,
        "link": link,
    }


def scrape_depop(search_query):
    """Scrapes the first 10 listings from Depop for a given search query using multi-threading."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Program Files/ChromeDriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://www.depop.com/search/?q={search_query.replace(' ', '+')}"
    print(f"Navigating to URL: {url}")
    driver.get(url)

    # Handle the "Accept" button
    try:
        accept_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='cookieBanner__acceptAllButton']")
        accept_button.click()
        print("Accepted cookies/modal.")
        time.sleep(2)
    except Exception:
        print("No 'Accept' button found or already handled.")

    # Scroll the page to ensure all elements are visible
    def scroll_page():
        print("Scrolling the page...")
        for _ in range(1):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)

    scroll_page()

    # Extract product data
    results = []
    try:
        product_containers = driver.find_elements(By.CSS_SELECTOR, "li.styles__ProductCardContainer-sc-ec533c9e-7")
        print(f"Found {len(product_containers)} product containers.")

        # Use ThreadPoolExecutor for concurrent scraping of product listings
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust threads if necessary
            futures = [executor.submit(process_depop_item, product) for product in product_containers[:10]]

            for future in as_completed(futures):
                results.append(future.result())

    except Exception as e:
        print(f"Error extracting products: {e}")
    finally:
        driver.quit()

    return results

def process_poshmark_item(container):
    """Extracts data from a single Poshmark product listing."""
    try:
        title = container.find_element(By.CSS_SELECTOR, "a.tile__title").text.strip()
    except Exception:
        title = "Not found"

    try:
        price = container.find_element(By.CSS_SELECTOR, "span.p--t--1.fw--bold").text.strip()
    except Exception:
        price = "Not found"

    try:
        size = container.find_element(By.CSS_SELECTOR, "a.tile__details__pipe__size").text.strip().replace("Size: ", "")
    except Exception:
        size = "Not found"

    try:
        raw_link = container.find_element(By.CSS_SELECTOR, "a.tile__title").get_attribute("href")
        link = f"https://poshmark.com{raw_link}" if raw_link.startswith("/") else raw_link
    except Exception:
        link = "Not found"

    try:
        image_url = container.find_element(By.CSS_SELECTOR, "img.ovf--h.d--b").get_attribute("src")
    except Exception:
        image_url = "Not found"

    return {
        "title": title,
        "price": price,
        "size": size,
        "link": link,
        "image_url": image_url,
    }


def scrape_poshmark(search_query):
    """Scrapes the first 10 listings from Poshmark for a given search query using multi-threading."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Program Files/ChromeDriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navigate to Poshmark search page
        url = f"https://poshmark.com/search?query={search_query.replace(' ', '%20')}&type=listings&src=dir"
        print(f"Navigating to URL: {url}")
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card"))
        )

        product_containers = driver.find_elements(By.CSS_SELECTOR, "div.card")
        print(f"Found {len(product_containers)} product containers.")

        scraped_results = []
        # Use ThreadPoolExecutor for concurrent scraping of product listings
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust threads if necessary
            futures = [executor.submit(process_poshmark_item, container) for container in product_containers[:10]]

            for future in as_completed(futures):
                scraped_results.append(future.result())

    except Exception as e:
        print(f"Error extracting products: {e}")
        scraped_results = []
    finally:
        driver.quit()

    return scraped_results


def process_ebay_item(wrapper):
    """Extracts data from a single eBay product listing."""
    try:
        title = wrapper.find_element(By.CSS_SELECTOR, ".s-item__title").text.strip()
        if not title or "Shop on eBay" in title:
            return None  # Skip invalid listings

        try:
            price = wrapper.find_element(By.CSS_SELECTOR, "span.s-item__price").text.strip()
        except Exception:
            price = "Not found"

        try:
            image_url = wrapper.find_element(By.CSS_SELECTOR, "div.s-item__image-wrapper img").get_attribute("src")
        except Exception:
            image_url = "Not found"

        try:
            item_url = wrapper.find_element(By.CSS_SELECTOR, "a.s-item__link").get_attribute("href")
        except Exception:
            item_url = "Not found"

        return {
            "title": title,
            "price": price,
            "image_url": image_url,
            "item_url": item_url,
        }
    except Exception as e:
        print(f"Error processing eBay item: {e}")
        return None


def scrape_ebay(search_query):
    """Scrapes the first 10 listings from eBay using multi-threading."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("C:/Program Files/ChromeDriver/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    results = []
    
    try:
        # Navigate to eBay search page
        url = f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}&_sop=12"
        print(f"Navigating to URL: {url}")
        driver.get(url)

        # Wait for product containers to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-item__wrapper"))
        )

        product_wrappers = driver.find_elements(By.CSS_SELECTOR, "div.s-item__wrapper")
        print(f"Found {len(product_wrappers)} potential product wrappers.")

        scraped_results = []
        # Use ThreadPoolExecutor for concurrent scraping of product listings
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust thread count as needed
            futures = [executor.submit(process_ebay_item, wrapper) for wrapper in product_wrappers[:10]]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    scraped_results.append(result)

    except Exception as e:
        print(f"Error extracting products: {e}")
        scraped_results = []
    finally:
        driver.quit()

    return scraped_results


def scrape_all_platforms(search_query):
    """
    Runs scrapers for all platforms concurrently using ThreadPoolExecutor.
    """

    platforms = {
        "Grailed": scrape_grailed,
        "Depop": scrape_depop,
        "Poshmark": scrape_poshmark,
        "eBay": scrape_ebay,
    }

    results = []

    # **Track total execution time**
    start_time = time.time()
    print("\n🚀 Starting parallel scraping...")

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_platform = {
            executor.submit(scraper, search_query): name for name, scraper in platforms.items()
        }

        for future in as_completed(future_to_platform):
            platform_name = future_to_platform[future]
            end_time = time.time()  # Capture when the scraper finishes
            
            try:
                platform_results = future.result()
                duration = round(end_time - start_time, 2)  # Calculate time taken
                print(f"✅ {platform_name} finished in {duration} seconds with {len(platform_results)} results.")
                
                # Add platform identifier
                for result in platform_results:
                    result["platform"] = platform_name  

                results.extend(platform_results)

            except Exception as e:
                print(f"❌ Error scraping {platform_name}: {e}")

    # Shuffle results for mixed output
    random.shuffle(results)
    
    total_duration = round(time.time() - start_time, 2)
    print(f"\n⏳ Total execution time: {total_duration} seconds")

    return results
