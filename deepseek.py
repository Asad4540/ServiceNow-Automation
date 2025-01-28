import os
import pandas as pd
from bs4 import BeautifulSoup
from slugify import slugify
import requests

# Read the Excel input
df = pd.read_excel('input_data.xlsx')

for index, row in df.iterrows():
    # Variables from the Excel file
    example_link = row['example link']
    example_et = row['example et']
    asset_name = row['asset_name']
    asset_abstract = row['asset_abstract']
    country_list = row['country'].split(';')
    asset_pdf_page = row['asset_pdf_page']
    solution_category = row['solution_category']
    
    # Create folders
    solution_folder = slugify(solution_category)
    et_folder = os.path.join(solution_folder, 'et')
    os.makedirs(et_folder, exist_ok=True)

    # Modified HTML processing function to preserve styling
    def process_html(html_content, is_et=False):
        # Use 'html5lib' parser for better HTML preservation
        soup = BeautifulSoup(html_content, 'html5lib')

        # Preserve existing styling while updating content
        # Update title-heading text without removing existing spans/styles
        for title in soup.select('.title-heading'):
            if title.find(True):  # Check if there are child elements
                title.find(string=lambda t: True).replace_with(asset_name)
            else:
                title.string = asset_name

        # Update abstract text while preserving wrapper elements
        for abstract in soup.select('.lp-abstract'):
            if abstract.find(True):  # Preserve child elements if they exist
                abstract.find(string=lambda t: True).replace_with(asset_abstract)
            else:
                abstract.string = asset_abstract

        # Update country dropdown
        select_tag = soup.find('select', id='Country')
        if select_tag:
            select_tag.clear()
            default_option = soup.new_tag('option', value="")
            default_option.string = "Country/Region *"
            select_tag.append(default_option)
            for country in country_list:
                option = soup.new_tag('option', value=country.strip())
                option.string = country.strip()
                select_tag.append(option)

        # Update PDF value
        hidden_input = soup.find('input', {'name': 'pdfValue', 'type': 'hidden'})
        if hidden_input:
            hidden_input['value'] = asset_pdf_page

        # Email template specific changes
        if is_et:
            a_tag = soup.find('a', {'id': 'et-redirection'})
            if a_tag:
                file_name = slugify(asset_name) + ".html"
                a_tag['href'] = f'./{file_name}'

        # Preserve original formatting when outputting
        return str(soup)

    # Process landing page
    landing_response = requests.get(example_link)
    landing_content = process_html(landing_response.text)

    # Save landing page
    landing_file = slugify(f"{asset_name} {solution_category} english") + ".html"
    landing_path = os.path.join(solution_folder, landing_file)
    with open(landing_path, 'w', encoding='utf-8') as f:
        f.write(landing_content)

    # Process email template
    et_response = requests.get(example_et)
    et_content = process_html(et_response.text, is_et=True)

    # Save email template
    et_file = slugify(asset_name) + ".html"
    et_path = os.path.join(et_folder, et_file)
    with open(et_path, 'w', encoding='utf-8') as f:
        f.write(et_content)

print("All files processed successfully with preserved styling!")