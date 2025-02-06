import os
import pandas as pd
from bs4 import BeautifulSoup
from slugify import slugify
import requests

# Direct URLs for landing pages and email templates
example_link = "https://ittech-news.com/landing_pages/servicenow/sn-lp-english.html"
example_et = "https://ittech-news.com/landing_pages/servicenow/sn-et-example.html"
link_path = "https://ittech-news.com/landing_pages"
campaign_code = "Servicenow30012025"

# Read the Excel input for all sheets
df_sheets = pd.read_excel('input_data.xlsx', sheet_name=None)

# Initialize a counter to track filenames and avoid duplicates
filename_counter = {}

# Iterate over each sheet and process the data
for sheet_name, df in df_sheets.items():
    print(f"Processing data from sheet: {sheet_name}")
    
    # Initialize lists to store generated links for each row
    et_links = []
    lp_links = []
     
    for index, row in df.iterrows():
        # Variables from the Excel file
        asset_name = row['asset_name']
        asset_abstract = row['asset_abstract']
        country_list = row['country'].split(';')
        asset_pdf_page = row['asset_pdf_page']
        solution_category = row['solution_category']
        language =  row['language']
        cluster = row['cluster']
        
        # Create folders
        solution_folder = slugify(solution_category)
        et_folder = os.path.join(solution_folder, 'et')
        os.makedirs(et_folder, exist_ok=True)
        
        # Generate base filename and key for tracking duplicates
        base_filename = slugify(f"{asset_name} {cluster} {language}")
        key = (solution_folder, base_filename)
        
        # Get current count for the filename, default to 0
        count = filename_counter.get(key, 0)
        
        # Create the filename with incremental count if needed
        if count == 0:
            common_file_name = f"{base_filename}.html"
        else:
            common_file_name = f"{base_filename}-{count}.html"
        
        # Update the counter for the next occurrence
        filename_counter[key] = count + 1
        
        et_link = f"{link_path}/{campaign_code}/et/{common_file_name}"
        lp_link = f"{link_path}/{campaign_code}/{common_file_name}"
        et_links.append(et_link)
        lp_links.append(lp_link)

        # Modified HTML processing function to preserve styling
        def process_html(html_content, is_et=False):
            # Use 'html5lib' parser for better HTML preservation
            soup = BeautifulSoup(html_content, 'html5lib')

            # Preserve existing styling while updating content
            for title in soup.select('.title-heading'):
                if title.find(True):  # Check if there are child elements
                    title.find(string=lambda t: True).replace_with(asset_name)
                else:
                    title.string = asset_name

            for abstract in soup.select('.lp-abstract'):
                if abstract.find(True):
                    abstract.find(string=lambda t: True).replace_with(asset_abstract)
                else:
                    abstract.string = asset_abstract

            # Update country dropdown
            select_tag = soup.find('select', id='country')
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
                tbody_tag = soup.find('tbody', {'id': 'et-redirection'})
                if tbody_tag:
                    a_tag = tbody_tag.find('a')
                    if a_tag:
                        # Replace <a href> link with the landing page file in the root folder
                        file_name = slugify(f"{asset_name} {cluster} {language}") + ".html"
                        a_tag['href'] = f'../{file_name}'

            # Preserve original formatting when outputting
            return str(soup)

        # Process landing page
        try:
            landing_response = requests.get(example_link)
            landing_response.raise_for_status()
            landing_content = process_html(landing_response.text)
            # Save landing page
            landing_path = os.path.join(solution_folder, common_file_name)
            with open(landing_path, 'w', encoding='utf-8') as f:
                f.write(landing_content)
            print(f"Landing page : {common_file_name} generated successfully.")
        except Exception as e:
            print(f"Failed to generate landing page {common_file_name}. Error: {e}")

        # Process email template
        try:
            et_response = requests.get(example_et)
            et_response.raise_for_status()
            et_content = process_html(et_response.text, is_et=True)
            # Save email template in the 'et' folder with the same file name
            et_path = os.path.join(et_folder, common_file_name)
            with open(et_path, 'w', encoding='utf-8') as f:
                f.write(et_content)             
            print(f"Email template : {common_file_name} generated successfully.")
        except Exception as e:
            print(f"Failed to generate email template {common_file_name}. Error: {e}")

    # Add new columns to the DataFrame
    df['ET Links'] = et_links
    df['LP Links'] = lp_links
    # Update the sheet in the dictionary
    df_sheets[sheet_name] = df
    
    # === NEW: Save the modified DataFrames to a new Excel file ===
    output_path = f'{campaign_code}.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        for sheet_name, df in df_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"\nAll data processed and links added to {output_path}!")  
print("All files processed successfully with progress updates!")

