# chrome.exe --remote-debugging-port=9222

# Import necessary libraries
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# In[]
# Function to click a checkbox at specific coordinates
def click_checkbox(x_cor, y_cor, driver):
    js_script = '''
    var element = document.elementFromPoint({x}, {y});
    element.click();
    '''.format(x=x_cor, y=y_cor)
    
    driver.execute_script(js_script)

# Function to set the value of an input field
def set_field_value(input_field, expected_value, max_attempts=19, type_float=False):
    for _ in range(max_attempts):
        input_field.clear()
        input_field.send_keys(expected_value)
        driver.execute_script("arguments[0].blur();", input_field)
        if type_float:    
            current_value = float(input_field.get_attribute("value"))
        else:
            current_value = int(input_field.get_attribute("value").replace('.00', ''))
        if current_value == expected_value:
            return True
        time.sleep(0.05)
    return False

# Function to save a dataframe with scraped data
def save_dataframe(driver):
    df = pd.DataFrame(columns=['timestamp', 'top_elements'])
    top_elements = []
        
    for i in range(1, 210):
        xpath = f'/html/body/form/section/div/aside[1]/div/div[{i}]'
        try:
            element_text = driver.find_element(By.XPATH, xpath).text
            top_elements.append(element_text)
            print(element_text)
        except Exception as e:
            print(f"Error retrieving element at xpath {xpath}: {e}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame({'timestamp': [timestamp], 'top_elements': [', '.join(top_elements)]})
    df = pd.concat([df, new_row], ignore_index=True)
    current_time = time.time()
    timestamp_str = time.strftime("%Y-%m-%d_%H-%M", time.localtime(current_time))
    filename = fr"C:\Users\arjun\Desktop\jetX\data_{timestamp_str}.parquet"
    
    df.to_parquet(filename, index=False)

# Function to refresh the web driver
def refresh_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_path = r"C:\Users\arjun\OneDrive\Desktop\Jet X\chrome-win64\chrome-win64\chromedriver.exe"
    chrome_options.add_experimental_option('debuggerAddress', 'localhost:9222')
    
    driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
    url = "https://pari-match-bet.in/en/casino/instant-games/game/smartsoft-in-jetx-insta"
    driver.get(url)
    
    time.sleep(20)
    
    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        all_text = soup.get_text()
        main_page_text = soup.get_text()
        iframe_texts = []
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        z = 0
        
        def extract_info_from_iframe(driver, iframe, idx, z):
            driver.switch_to.frame(iframe)
            iframe_page_source = driver.page_source
            iframe_soup = BeautifulSoup(iframe_page_source, 'html.parser')
            iframe_text = iframe_soup.get_text()
            text_list.append(iframe_text)
            if iframe_text[:7] == "\n\tJetX\n":
                print(idx)
                print(z)
                return 'exit'
            source_list.append(iframe_page_source)
            nested_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            z = z + 1
            for nested_iframe in nested_iframes:
                extract_info_from_iframe(driver, nested_iframe, idx, z)
            driver.switch_to.parent_frame()
        
        top_level_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        text_list = []
        source_list = []
        
        for idx, top_level_iframe in enumerate(top_level_iframes, 1):
            print(f"Top Level Iframe {idx}:")
            res = extract_info_from_iframe(driver, top_level_iframe, idx, z)
            if res == 'exit':
                break
    except:
        pass
    
    return driver

# In[]

# Main loop to continuously refresh the driver and perform actions
last_save_time = time.time()
while True:
    driver = refresh_driver()  # Refresh the web driver
    for _ in range(100000):
        try:
            # Find elements on the page
            auto_bet_checkbox = driver.find_element(By.XPATH, "/html/body/form/section/div/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/label/span")
            auto_collect_checkbox = driver.find_element(By.XPATH, "/html/body/form/section/div/div/div[3]/div[2]/div[1]/div/div[1]/div[4]/div[1]/label/span")
            bet_button = driver.find_element(By.XPATH, "/html/body/form/section/div/div/div[3]/div[2]/div[1]/div/div[2]/div")
            auto_collect_multiplier_input = driver.find_element(By.XPATH, "/html/body/form/section/div/div/div[3]/div[2]/div[1]/div/div[1]/div[4]/div[3]/div/input")
            print('condition checked')
            # Set field value and break if successful
            if set_field_value(auto_collect_multiplier_input, 1.2, type_float=True):
                break
            else:
                driver = refresh_driver()
                time.sleep(1)
        except:
            driver = refresh_driver()
            time.sleep(1)

    element_location = auto_collect_checkbox.location
    click_checkbox(element_location['x'], element_location['y'], driver)

    # Function to get the top elements from the page
    def get_top_elements():
        top_elements = []
        for i in range(1, 8):
            xpath = f'/html/body/form/section/div/aside[1]/div/div[{i}]'
            top_elements.append(driver.find_element(By.XPATH, xpath).text)
        return top_elements
    
    # Define variables for the betting loop
    bet_amount_input = '/html/body/form/section/div/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[3]/div/input'
    bet_amount_input_field = driver.find_element(By.XPATH, bet_amount_input)
    previous_top_elements = []
    consecutive_count = 0
    max_consecutive = 3
    previous_amount = 1
    list_of_amount = [0, 1, 2, 3, 4]
    continuous_threshold_ctr = 0
    bet_placed_list = []
    betmultiplier_threshold = 5
    while True:
        try:
            current_top_elements = get_top_elements()  # Get current top elements from the page
            if current_top_elements == previous_top_elements:
                consecutive_count += 1
            else:
                consecutive_count = 0
            # The time when we place our bet
            if consecutive_count == max_consecutive:
                # The first element is not empty
                if not current_top_elements[0]:
                    consecutive_count_inside = 0
                    for value in current_top_elements[1:]:
                        if value and float(value) < betmultiplier_threshold :
                            consecutive_count_inside += 1
                        else:
                            break
                    if consecutive_count_inside >= 0:
                        expected_value = list_of_amount[consecutive_count_inside]
                        if set_field_value(bet_amount_input_field, expected_value):
                            bet_button.click()
                            print('bet placing, ', list_of_amount[consecutive_count_inside])
                            bet_placed_list.append(['Success', str(list_of_amount[consecutive_count_inside]), consecutive_count_inside, current_top_elements])
                        else:
                            bet_placed_list.append(['Fail', str(list_of_amount[consecutive_count_inside]), consecutive_count_inside, current_top_elements])
                    else:
                        current_time = time.time()
                        # Saving data in every 15 Minutes
                        if current_time - last_save_time >= 15 * 60:
                            print('data being saved at ', (current_time - last_save_time))
                            save_dataframe(driver)
                            last_save_time = current_time
                            break
                        if current_time - last_save_time >= 1 * 60:
                            if driver.current_url != 'https://pari-match-bet.in/en/casino/instant-games/game/smartsoft-in-jetx-insta':
                                break
            previous_top_elements = current_top_elements
            time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
