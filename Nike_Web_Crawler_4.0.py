from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path
import pandas as pd
import time
from datetime import datetime
import pytz
import seaborn as sns
import matplotlib.pyplot as plt

# Function to generate Nike URL based on the product name
def generate_nike_url(product_name):
    base_url = 'https://www.nike.com/'
    search_url = base_url + 'gb/search?q=' + product_name.replace(' ', '%20')
    return search_url

# Initialize Selenium WebDriver
svc = Service(executable_path=binary_path)
browser = webdriver.Chrome(service=svc)

# Create an empty DataFrame to store the results
df = pd.DataFrame(columns=["Product", "Name", "Price", "Type", "Subcategory", "Time"])

# User Input for Product Details
product_name = input("Enter the Nike product name you want to scrape: ")
product_type = input("Enter the product type (Men, Women, Kids, Sale): ")
subcategory = input("Enter the subcategory (Shoes, Clothing, Accessories, etc.): ")

# Generate the URL for the product
url = generate_nike_url(product_name)

# Open the URL with the browser
browser.get(url)

try:
    # Attempt to find the price and product name
    price = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@data-test="product-price"]')))
    product_title = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@data-test="product-title"]')))

    # Get the timezone object for London
    tz_London = pytz.timezone('Europe/London')
    datetime_London = datetime.now(tz_London)

    # Append the data to the DataFrame
    df = df._append({
        "Product": url, 
        "Name": product_title.get_attribute('innerHTML'),
        "Price": price.get_attribute('innerHTML'),
        "Type": product_type,
        "Subcategory": subcategory,
        "Time": datetime_London.strftime("%H:%M:%S")
    }, ignore_index=True)
    
    print(f"Product: {product_title.get_attribute('innerHTML')} | Price: {price.get_attribute('innerHTML')} | Time: {datetime_London.strftime('%H:%M:%S')}")
    
except Exception as e:
    print(f"Error: {str(e)}")

# Close the browser
browser.quit()

# Save data into an Excel CSV file
df.to_csv(r'NikePriceList.csv', index=False, encoding='utf-8-sig')

# Data Visualization with Seaborn
sns.set(style="whitegrid")

# Plot Price Distribution per Category
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x="Price", hue="Type", kde=True, bins=20)
plt.title('Price Distribution by Product Type')
plt.xlabel('Price')
plt.ylabel('Frequency')
plt.show()

# Plot Price by Subcategory
plt.figure(figsize=(12, 6))
sns.boxplot(x="Subcategory", y="Price", data=df)
plt.title('Price Distribution per Subcategory')
plt.xticks(rotation=45)
plt.show()
