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
    
    # Create solution category folder and et subfolder
    solution_folder = slugify(solution_category)
    et_folder = os.path.join(solution_folder, 'et')
    os.makedirs(et_folder, exist_ok=True)
    
    # Function to process the HTML content
    def process_html(html_content, is_et=False):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Replace the text content of title-heading and lp-abstract
        for title in soup.select('.title-heading'):
            title.string = asset_name
        for abstract in soup.select('.lp-abstract'):
            abstract.string = asset_abstract

        # Replace country list in <select> with id lp-country
        select_tag = soup.find('select', id='lp-country')
        if select_tag:
            select_tag.clear()
            default_option = soup.new_tag('option', value="")
            default_option.string = "Country/Region *"
            select_tag.append(default_option)
            for country in country_list:
                option = soup.new_tag('option', value=country.strip())
                option.string = country.strip()
                select_tag.append(option)

        # Replace hidden input with asset_pdf_page
        hidden_input = soup.find('input', {'name': 'pdfValue', 'type': 'hidden'})
        if hidden_input:
            hidden_input['value'] = asset_pdf_page
        
        # Replace et-redirection href with corresponding link for email templates
        if is_et:
            a_tag = soup.find('a', {'id': 'et-redirection'})
            if a_tag:
                file_name = slugify(asset_name) + ".html"
                a_tag['href'] = f'./{file_name}'
        
        return str(soup)
    
    # Scrape and process landing page (example link)
    landing_response = requests.get(example_link)
    landing_content = process_html(landing_response.text)

    # Create slugified filename for landing page
    file_name = slugify(f"{asset_name} {solution_category} english") + ".html"
    file_path = os.path.join(solution_folder, file_name)
    
    # Save the landing page content
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(landing_content)

    print(f"Processed {example_link} -> {file_path}")
    
    # Scrape and process email template (example et)
    et_response = requests.get(example_et)
    et_content = process_html(et_response.text, is_et=True)

    # Create slugified filename for email template
    et_file_name = slugify(f"{asset_name} {solution_category} english") + ".html"
    et_file_path = os.path.join(et_folder, et_file_name)

    # Save the email template content
    with open(et_file_path, 'w', encoding='utf-8') as file:
        file.write(et_content)

    print(f"Processed {example_et} -> {et_file_path}")
