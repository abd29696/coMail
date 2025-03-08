import os
import json
import pandas as pd
import time
from ai_client import AIClient  # Import AI client from a separate file

# Load prompt template from constants.json
with open("constants.json", "r") as config_file:
    config = json.load(config_file)
    email_prompt_template = config["email_prompt_template"]

# Initialize AI client
ai_client = AIClient()


def generate_cold_email(name, company, industry, offer):
    prompt = email_prompt_template.format(name=name, company=company, industry=industry, offer=offer)
    return ai_client.generate_text(prompt)


def process_leads(input_excel, output_excel):
    df = pd.read_excel(input_excel)

    for index, row in df.iterrows():
        try:
            email_content = generate_cold_email(row['Name'], row['Company'], row['Industry'],
                                                "We offer AI-powered sales automation tools.")
            df.at[index, 'Generated Email'] = email_content

            print(f"\nGenerated email for {row['Name']} at {row['Company']}:")
            print(email_content)
            print("-" * 50)

            time.sleep(2)  # Prevent API rate limits
        except Exception as e:
            print(f"Error processing {row['Name']}: {str(e)}")

    df.to_excel(output_excel, index=False)


if __name__ == "__main__":
    input_excel = "leads.xlsx"  # Excel file with Name, Company, Industry, Email columns
    output_excel = "generated_emails.xlsx"
    process_leads(input_excel, output_excel)
    print("Cold email generation complete!")
