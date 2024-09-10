from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from datetime import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt

# Initialize browser
def init_browser():
    svc = Service(executable_path=binary_path)
    browser = webdriver.Chrome(service=svc)
    return browser

# Scrape product data from a Nike product page
def scrape_product_data(browser, url):
    browser.get(url)
    try:
        # Extract product name and price
        product_name = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//h1[contains(@class, "headline-5")]'))).get_attribute('innerHTML')
        price = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-test="product-price"]'))).get_attribute('innerHTML')

        # Get the current time in London
        tz_London = pytz.timezone('Europe/London')
        datetime_London = datetime.now(tz_London)

        return {
            "Product URL": url,
            "Product Name": product_name,
            "Price": price,
            "Time": datetime_London.strftime("%H:%M:%S")
        }

    except Exception as e:
        print(f"Error fetching data for {url}: {e}")
        return None

# Ask user to input the product name
def get_product_urls():
    products = []
    while True:
        product_name = input("Enter a Nike product URL (or 'done' to finish): ").strip()
        if product_name.lower() == 'done':
            break
        products.append(product_name)
    return products

# Add product categories manually (optional)
def assign_product_category():
    print("Choose the category for this product:")
    category = input("Category (Men, Women, Kids, Sale): ").strip()
    subcategory = input("Subcategory (Shoes, Clothing, Accessories, Equipment): ").strip()
    sub_subcategory = input("Sub-Subcategory (e.g., Running, Football, etc.): ").strip()
    return category, subcategory, sub_subcategory

# Store and export data to CSV
def store_data(dataframe, file_name='PriceList.csv'):
    dataframe.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"Data saved to {file_name}")

# Visualize the data using Seaborn
def visualize_data(df):
    sns.set(style='whitegrid')

    # Plot price distribution per category
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='Price', hue='Category', kde=True, bins=20)
    plt.title('Price Distribution by Category')
    plt.show()

    # Plot the price trends
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Time', y='Price', hue='Category', marker='o')
    plt.title('Price Trend Over Time')
    plt.show()

# Main function to run the scraper
def main():
    # Initialize browser
    browser = init_browser()

    # Get product URLs from user
    product_urls = get_product_urls()

    # Create an empty DataFrame to store the results
    df = pd.DataFrame(columns=["Product URL", "Product Name", "Price", "Time", "Category", "Subcategory", "Sub-Subcategory"])

    # Scrape product data
    for url in product_urls:
        data = scrape_product_data(browser, url)
        if data:
            category, subcategory, sub_subcategory = assign_product_category()
            data["Category"] = category
            data["Subcategory"] = subcategory
            data["Sub-Subcategory"] = sub_subcategory
            df = df.append(data, ignore_index=True)

    # Close the browser
    browser.quit()

    # Store the data
    store_data(df)

    # Visualize the data
    visualize_data(df)

if __name__ == "__main__":
    main()
