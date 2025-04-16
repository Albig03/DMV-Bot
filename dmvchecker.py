import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# ====== CONFIG ======
DESIRED_DATE = "04/22/2025"  # Format must match site format exactly
CHECK_INTERVAL =  600 # in seconds

GMAIL_USER = 'iiquantumbreak@gmail.com'
GMAIL_APP_PASSWORD = 'elik nsfw chat okfe'
TO_EMAIL = 'veerp360@gmail.com'  # Or phone's email-to-text address

def send_email(subject, body):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    
    # Attach the body with the email
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            text = msg.as_string()
            server.sendmail(GMAIL_USER, TO_EMAIL, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# URL to check
URL = "https://telegov.njportal.com/njmvc/AppointmentWizard/11"

# Path to your ChromeDriver
service = Service(ChromeDriverManager().install())  # Automatically installs the correct driver
driver = webdriver.Chrome(service=service)

def get_availability():
    try:
        driver.get(URL)

        # Wait for any heightCheck div to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "heightCheck"))
        )

        # Find all divs with id="heightCheck"
        height_check_divs = driver.find_elements(By.ID, "heightCheck")

        matching_locations = []

        for div in height_check_divs:
            # Find the dateText and cardHeader within the same heightCheck div
            try:
                date_div = div.find_element(By.XPATH, ".//div[starts-with(@id, 'dateText')]")
                location_header = div.find_element(By.ID, "cardHeader")
                
                # Get the text from the date div (to check if it matches)
                raw_text = date_div.text.strip()

                # Try to find a date in MM/DD/YYYY format
                found_date = re.search(r"\b\d{2}/\d{2}/\d{4}\b", raw_text)

                if found_date:
                    available_date = found_date.group(0)
                    print(f"🔍 Found available date: {available_date}")

                    if available_date == DESIRED_DATE:
                        print(f"MATCH: {available_date}")

                        # Extract the location name
                        location_name = location_header.text.strip()
                        print(f"Location: {location_name}")

                        # Add the location to the list
                        matching_locations.append(location_name)
            
            except Exception as e:
                print(f"⚠Error extracting location or date info: {e}")

        # If we found any matching locations, send the email
        if matching_locations:
            subject = f"DMV Appointments Available on {DESIRED_DATE}"
            body = "\n".join([f"DMV appointment available at {loc} on {DESIRED_DATE}!" for loc in matching_locations])
            send_email(subject, body)
            return True
        else:
            print("No matching dates found.")

    except Exception as e:
        print(f"Error checking availability: {e}")
        
    return False


def main():
    while True:
        print(f"[{datetime.now()}] Checking availability...")
        found = get_availability()
        if found:
            print("Match found, waiting for next interval...")
        else:
            print("No match found. Checking again soon.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
