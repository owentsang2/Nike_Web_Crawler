from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path
import pandas as pd
from datetime import datetime
import pytz
import urllib.parse
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the Chrome driver
svc = Service(executable_path=binary_path)
browser = webdriver.Chrome(service=svc)

# Prompt the user for the product name
product_name = input("Enter the product name to search on Nike: ")

# URL-encode the product name
product_name_encoded = urllib.parse.quote_plus(product_name)

# Construct the search URL
search_url = f"https://www.nike.com/gb/w?q={product_name_encoded}"

# Navigate to the search URL
browser.get(search_url)

# Wait for the search results to load
WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"product-grid")]')))

# Extract the product URLs from the search results
product_elements = browser.find_elements(By.XPATH, '//div[contains(@class,"product-grid")]//a[contains(@class,"product-card__link-overlay")]')
product_urls = [elem.get_attribute('href') for elem in product_elements]

# Create an empty DataFrame to store the results
df = pd.DataFrame(columns=["Product", "Name", "Price", "Time", "Category", "Subcategory", "Sub-subcategory"])

# Loop through the product URLs
for url in product_urls:
    browser.get(url)
    try:
        # Extract product name
        product_name_elem = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//h1[contains(@class,"headline")]')))
        product_name_text = product_name_elem.text.strip()
        
        # Extract price
        price_elem = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@data-test,"product-price")]')))
        price_text = price_elem.text.strip()

        # Extract category information from breadcrumbs
        category_elems = browser.find_elements(By.XPATH, '//nav[contains(@aria-label,"Breadcrumbs")]//li/a')
        categories = [elem.text.strip() for elem in category_elems]

        # Get the current time in London
        tz_London = pytz.timezone('Europe/London')
        datetime_London = datetime.now(tz_London)

        # Prepare data for DataFrame
        data = {
            "Product": url,
            "Name": product_name_text,
            "Price": price_text,
            "Time": datetime_London.strftime("%H:%M:%S"),
            "Category": categories[0] if len(categories) > 0 else '',
            "Subcategory": categories[1] if len(categories) > 1 else '',
            "Sub-subcategory": categories[2] if len(categories) > 2 else ''
        }

        # Append data to DataFrame
        df = df._append(data, ignore_index=True)

        print(f"Scraped data for product: {product_name_text}")
    except Exception as e:
        print(f"Failed to scrape product at {url}: {e}")

# Close the browser
browser.quit()

# Save the DataFrame to a CSV file
df.to_csv('PriceList.csv', index=False, encoding='utf-8-sig')

# Data Visualization with Seaborn
# Clean the 'Price' column to extract numerical values
df['Price_Clean'] = df['Price'].replace('[^0-9.]', '', regex=True).astype(float)

# Bar plot of product prices
plt.figure(figsize=(12, 6))
sns.barplot(x='Name', y='Price_Clean', data=df)
plt.xticks(rotation=90)
plt.title('Prices of Products')
plt.xlabel('Product Name')
plt.ylabel('Price (£)')
plt.tight_layout()
plt.show()

# Box plot of prices by category
plt.figure(figsize=(12, 6))
sns.boxplot(x='Category', y='Price_Clean', data=df)
plt.title('Price Distribution by Category')
plt.xlabel('Category')
plt.ylabel('Price (£)')
plt.show()

# Histogram of price distribution
plt.figure(figsize=(12, 6))
sns.histplot(df['Price_Clean'], kde=True)
plt.title('Price Distribution')
plt.xlabel('Price (£)')
plt.ylabel('Frequency')
plt.show()
