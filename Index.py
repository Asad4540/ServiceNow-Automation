import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from slugify import slugify

# Step 1: Read the input Excel file
file_path = "input_data.xlsx"  # Replace with your Excel file path
df = pd.read_excel(file_path)

# Step 2: Loop through each row in the Excel file
for index, row in df.iterrows():
    example_link = row['example link']
    asset_name = row['asset_name']
    asset_abstract = row['asset_abstract']
    country_list = row['country'].split(',')  # Assuming countries are comma-separated
    asset_pdf_page = row['asset_pdf_page']
    solution_category = row['solution_category']  # Using solution_category instead of cluster
    language = row['language']
    
    # Step 3: Fetch the webpage
    response = requests.get(example_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Step 4: Replace the "#title-heading" content
    title_heading = soup.find(id="title-heading")
    if title_heading:
        title_heading.string = asset_name

    # Step 5: Replace the "#lp-abstract" content
    abstract = soup.find(id="lp-abstract")
    if abstract:
        abstract.string = asset_abstract

    # Step 6: Replace the "#Country" <select> options
    country_select = soup.find(id="Country")  # Updated to target "Country" instead of "lp-country"
    if country_select:
        country_select.clear()  # Clear current options
        for country in country_list:
            option = soup.new_tag('option')
            option.string = country
            option['value'] = country
            country_select.append(option)

    # Step 7: Set the value for the hidden "pdfValue" input field
    pdf_input = soup.find('input', {'name': 'pdfValue', 'type': 'hidden'})
    if pdf_input:
        pdf_input['value'] = asset_pdf_page

    # Step 8: Create a shortened folder with the first 20 characters of the "solution_category" name
    solution_category_folder = slugify(solution_category)  # Limit to 20 characters for folder name
    
    # Ensure the folder exists, including parent directories
    os.makedirs(solution_category_folder, exist_ok=True)

    # Step 9: Generate a shortened slugified file name from "assetname", "solution_category", and "language"
    file_name = slugify(f"{asset_name[:20]} {solution_category[:20]} {language[:10]}") + ".html"  # Limit components to reduce length
    file_path = os.path.join(solution_category_folder, file_name)

    # Step 10: Save the modified HTML file inside the solution_category folder
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print(f"Processed {example_link} -> {file_path}")
