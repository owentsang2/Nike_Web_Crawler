import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import urllib.parse
import matplotlib.pyplot as plt
import seaborn as sns

# Prompt the user for the product name
product_name = input("Enter the product name to search on Nike: ")

# URL-encode the product name
product_name_encoded = urllib.parse.quote_plus(product_name)

# Construct the search URL
search_url = f"https://www.nike.com/gb/w?q={product_name_encoded}"

# Make a request to the search URL
response = requests.get(search_url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the product URLs from the search results
product_elements = soup.select('div.product-grid a.product-card__link-overlay')
product_urls = [elem['href'] for elem in product_elements]

# Create an empty DataFrame to store the results
df = pd.DataFrame(columns=["Product", "Name", "Price", "Time", "Category", "Subcategory", "Sub-subcategory"])

# Loop through the product URLs
for url in product_urls:
    full_url = "https://www.nike.com" + url  # Prepend domain to relative URLs
    product_response = requests.get(full_url)
    product_response.raise_for_status()

    product_soup = BeautifulSoup(product_response.text, 'html.parser')

    try:
        # Extract product name
        product_name_elem = product_soup.select_one('h1.headline')
        product_name_text = product_name_elem.text.strip() if product_name_elem else 'N/A'

        # Extract price
        price_elem = product_soup.select_one('div[data-test="product-price"]')
        price_text = price_elem.text.strip() if price_elem else 'N/A'

        # Extract category information from breadcrumbs
        category_elems = product_soup.select('nav[aria-label="Breadcrumbs"] li a')
        categories = [elem.text.strip() for elem in category_elems]

        # Get the current time in London
        tz_London = pytz.timezone('Europe/London')
        datetime_London = datetime.now(tz_London)

        # Prepare data for DataFrame
        data = {
            "Product": full_url,
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
        print(f"Failed to scrape product at {full_url}: {e}")

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
