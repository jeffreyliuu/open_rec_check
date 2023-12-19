from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Constants
URL = "https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=b171ab36-32ab-4a8c-8327-bb8314cbc5cd&semesterId=875edabf-1182-42a8-b187-157092f2d1c9"
BUTTON_SELECTOR = 'button[data-target="#offering-collapse-1"]'
SCHEDULE_CONTAINER_ID = 'offering-collapse-1'

def parse_dates(date_str):
    """Parse date strings and return a list of dates for multi-day events."""
    """Parse date strings and return a list of dates for multi-day events."""
    if '-' in date_str:
        start_date_str, end_date_str = date_str.split(' - ')
        start_date = datetime.strptime(start_date_str, '%a, %b %d %Y')
        end_date = datetime.strptime(end_date_str, '%a, %b %d %Y')
        delta = end_date - start_date
        return [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    else:
        return [datetime.strptime(date_str, '%a, %b %d %Y')]


def generate_entries(html, num_entries=5, locations=None):
    """Generate and print the next few session entries from the provided HTML, filtered by location."""
    current_datetime = datetime.now()
    soup = BeautifulSoup(html, 'html.parser')

    # If locations is not specified or empty, default to include all locations
    if not locations:
        locations = ['PAC Gym', 'CIF Gym 3']

    # Find all rows in the table
    rows = soup.find_all('tr', class_=['regular-occurrence', 'broken-occurrence'])

    # Store sessions
    sessions = []

    # Process each session
    for row in rows:
        date_td = row.find('td', class_='noinstructor') or row.find('td')
        if date_td:
            date_str = date_td.text.strip()
            dates = parse_dates(date_str)

            if 'cancel-oc-alert' not in row.get('class', []):
                time_td = row.find('td', class_='time-column')
                location_td = row.find('td', class_='location-column')
                if time_td and location_td:
                    time = time_td.text.strip()
                    location = location_td.text.strip()

                    if location in locations:
                        for date in dates:
                            try:
                                session_time = datetime.strptime(time.split(' - ')[0], '%I:%M %p').time()
                            except ValueError:
                                session_time = datetime.strptime(time.split(' - ')[0], '%H:%M').time()

                            session_datetime = datetime.combine(date, session_time)
                            if session_datetime > current_datetime:
                                sessions.append((session_datetime, location))

    # Sort sessions by date and time
    sessions.sort(key=lambda x: x[0])

    # Display the next few upcoming sessions
    if sessions:
        for session in sessions[:num_entries]:
            print(f"Date: {session[0].strftime('%a, %b %d %Y, %I:%M %p')}, Location: {session[1]}")
    else:
        print(f"No sessions available at locations: {', '.join(locations)}.")

def fetch_schedule_content():
    """Fetch the schedule content using WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(URL)
    button = driver.find_element(By.CSS_SELECTOR, BUTTON_SELECTOR)
    button.click()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID, SCHEDULE_CONTAINER_ID)))
    content = driver.find_element(By.ID, SCHEDULE_CONTAINER_ID).get_attribute('innerHTML')

    driver.quit()
    return content

# Main execution
if __name__ == "__main__":
    content = fetch_schedule_content()
    generate_entries(content, locations=['CIF Gym 3'])  # You can pass a list of locations here
