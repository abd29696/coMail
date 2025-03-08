import gradio as gr
import pandas as pd
import time
from ai_client import AIClient
import json

# Load prompt template from constants.json
with open("constants.json", "r") as config_file:
    config = json.load(config_file)
    email_prompt_template = config["email_prompt_template"]

# Initialize AI Client
aiclient = AIClient()

# Global variable to store uploaded leads
global_leads = None


def generate_cold_email(name, company, industry, offer):
    prompt = email_prompt_template.format(name=name, company=company, industry=industry, offer=offer)
    return aiclient.generate_text(prompt)


def process_leads(file):
    global global_leads
    df = pd.read_excel(file.name)
    if df.empty:
        return "No leads found in the file."
    first_lead = df.iloc[0]
    global_leads = df  # Store the DataFrame globally
    sample_email = generate_cold_email(first_lead['Name'], first_lead['Company'], first_lead['Industry'],
                                       "We offer AI-powered sales automation tools.")
    return sample_email


def send_emails():
    global global_leads
    if global_leads is None:
        return "No leads file uploaded. Please upload an Excel file first."

    emails = []
    for index, row in global_leads.iterrows():
        try:
            email_content = generate_cold_email(row['Name'], row['Company'], row['Industry'],
                                                "We offer AI-powered sales automation tools.")
            emails.append(f"To: {row['Email']}\nSubject: AI Solutions for {row['Company']}\n\n{email_content}")
            time.sleep(2)  # Prevent API rate limits
        except Exception as e:
            emails.append(f"Error processing {row['Name']}: {str(e)}")
    return "Emails sent successfully! (Simulated)\n\n" + "\n\n".join(emails)


# Default prompt
default_prompt = email_prompt_template

# Create Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## AI-Powered Cold Email Generator")
    file_upload = gr.File(label="Upload Excel File (.xlsx)")
    prompt_box = gr.Textbox(label="Prompt", value=default_prompt, lines=2)
    sample_output_box = gr.Textbox(label="Generated Sample Email", lines=10)
    process_btn = gr.Button("Generate Sample Email")

    with gr.Row():
        regenerate_btn = gr.Button("Re-generate")
        paraphrase_btn = gr.Button("Paraphrase")

    process_btn.click(fn=process_leads, inputs=[file_upload], outputs=[sample_output_box])
    regenerate_btn.click(fn=lambda prompt: generate_cold_email("", "", "", prompt), inputs=[prompt_box],
                         outputs=[sample_output_box])
    paraphrase_btn.click(fn=lambda text: aiclient.generate_text(f"Paraphrase this: {text}"), inputs=[sample_output_box],
                         outputs=[sample_output_box])

    send_btn = gr.Button("Send Emails")
    send_btn.click(fn=send_emails, inputs=[], outputs=[sample_output_box])

# Launch UI
demo.launch()
