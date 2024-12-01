import sqlite3
import json
import pytesseract
from PIL import Image
import re
import pandas as pd
import pdfplumber
from datetime import datetime

# Step 1: Connect to SQLite database
conn = sqlite3.connect('invoice_data.db')
c = conn.cursor()

# Step 2: Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS invoices
             (name TEXT, invoice_number TEXT, due_date TEXT, description TEXT)''')

# Step 3: Extract text from image
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

# Step 4: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

# Step 5: Extract data from structured input (e.g., Excel)
def extract_data_from_excel(excel_path):
    try:
        df = pd.read_excel(excel_path)
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error extracting data from Excel: {e}")
        return []

# Step 6: Extract invoice details
def extract_invoice_details(text):
    try:
        # Initialize fields with default values
        name = "Unknown"
        invoice_number = "Unknown"
        due_date = "Invalid Date"
        description = "No description provided."

        # Use regex to capture details
        name_match = re.search(r"(?i)(name|customer\s+name)[\s:]*([\w\s]+)", text)
        if name_match:
            name = name_match.group(2).strip()

        invoice_match = re.search(r"(?i)(invoice\s*number|invoice\s*no|invoice#)[\s:]*([\w\d\-]+)", text)
        if invoice_match:
            invoice_number = invoice_match.group(2).strip()

        due_date_match = re.search(r"(?i)(due\s*date|due)[\s:]*([\d\-\/]+)", text)
        if due_date_match:
            due_date_raw = due_date_match.group(2).strip()
            try:
                due_date = datetime.strptime(due_date_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                try:
                    due_date = datetime.strptime(due_date_raw, "%Y-%m-%d").strftime("%Y-%m-%d")
                except ValueError:
                    due_date = "Invalid Date"

        description_match = re.search(r"(?i)(description|items)[\s:]*([\w\s,]+)", text)
        if description_match:
            description = description_match.group(2).strip()

        # Format extracted data as JSON
        invoice_data = {
            "name": name,
            "invoice_number": invoice_number,
            "due_date": due_date,
            "description": description
        }

        return invoice_data
    except Exception as e:
        print(f"Error extracting invoice details: {e}")
        return None

# Step 7: Save to database
def save_to_database(invoice_data):
    try:
        c.execute("INSERT INTO invoices VALUES (?, ?, ?, ?)", (
            invoice_data['name'],
            invoice_data['invoice_number'],
            invoice_data['due_date'],
            invoice_data['description']
        ))
        conn.commit()
        print("Data saved to database successfully.")
    except Exception as e:
        print(f"Error saving to database: {e}")

# Step 8: Main function to process inputs
def process_file(file_path):
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(file_path)
    elif file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(('.xls', '.xlsx')):
        data = extract_data_from_excel(file_path)
        if data:
            for record in data:
                save_to_database(record)
            return
    else:
        print("Unsupported file format.")
        return

    # Extract invoice details from text
    if text:
        invoice_data = extract_invoice_details(text)
        if invoice_data:
            print("Extracted Invoice Data:", json.dumps(invoice_data, indent=4))
            save_to_database(invoice_data)

# Step 9: Example Usage
file_path = 's.png'  # Replace with your file path
process_file(file_path)

conn.close()












# import sqlite3
# import json
# from PIL import Image
# import pytesseract
# import re
# from datetime import datetime

# # Step 1: Connect to SQLite database
# conn = sqlite3.connect('invoice_data.db')
# c = conn.cursor()

# # Step 2: Create table if it doesn't exist
# c.execute('''CREATE TABLE IF NOT EXISTS invoices
#              (name TEXT, invoice_number TEXT, due_date TEXT, description TEXT)''')
# # Step 3: Extract invoice details from image
# def extract_invoice_details(image_path):
#     try:
#         # Load image
#         image = Image.open(image_path)

#         # Use Tesseract OCR to extract text from image
#         text = pytesseract.image_to_string(image)

#         # Debug log: Extracted text
#         print("Extracted Text:\n", text)

#         # Initialize fields with default values
#         name = "Unknown"
#         invoice_number = "Unknown"
#         due_date = "Invalid Date"
#         description = "No description provided."

#         # Use more flexible regex patterns to capture details
#         name_match = re.search(r"(?i)(name|customer\s+name)[\s:]*([\w\s]+)", text)
#         if name_match:
#             name = name_match.group(2).strip()

#         invoice_match = re.search(r"(?i)(invoice\s*number|invoice\s*no|invoice#)[\s:]*([\w\d\-]+)", text)
#         if invoice_match:
#             invoice_number = invoice_match.group(2).strip()

#         due_date_match = re.search(r"(?i)(due\s*date|due)[\s:]*([\d\-\/]+)", text)
#         if due_date_match:
#             due_date_raw = due_date_match.group(2).strip()
#             try:
#                 # Try different date formats
#                 due_date = datetime.strptime(due_date_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
#             except ValueError:
#                 try:
#                     due_date = datetime.strptime(due_date_raw, "%Y-%m-%d").strftime("%Y-%m-%d")
#                 except ValueError:
#                     due_date = "Invalid Date"

#         description_match = re.search(r"(?i)(description|items)[\s:]*([\w\s,]+)", text)
#         if description_match:
#             description = description_match.group(2).strip()

#         # Format extracted data as JSON
#         invoice_data = {
#             "name": name,
#             "invoice_number": invoice_number,
#             "due_date": due_date,
#             "description": description
#         }

#         return invoice_data
#     except Exception as e:
#         print(f"Error during extraction: {e}")
#         return None



# # Step 4: Save invoice data to SQLite database
# def save_to_database(invoice_data):
#     try:
#         c.execute("INSERT INTO invoices VALUES (?, ?, ?, ?)", (
#             invoice_data['name'],
#             invoice_data['invoice_number'],
#             invoice_data['due_date'],
#             invoice_data['description']
#         ))
#         conn.commit()
#         print("Data saved to database successfully.")
#         return invoice_data
#     except Exception as e:
#         print(f"Error saving to database: {e}")
#         return None

# # Step 5: Process the uploaded file
# file_path = 'in.jpg'  # Your uploaded file path
# invoice_data = extract_invoice_details(file_path)

# if invoice_data:
#     print("Extracted Invoice Data:", json.dumps(invoice_data, indent=4))
#     save_to_database(invoice_data)

# conn.close()



