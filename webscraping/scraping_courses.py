from interface import Course
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import ast
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# In the HTML, tickboxes in breadth/gened/level/honors/course_attr have format mat-mdc-checkbox-n, where n is some number corresponding to the nth checkbox
check_boxes = {
    "Biological Sciences": 1,
    "Humanities": 2,
    "Literature": 3,
    "Natural Sciences": 4,
    "Physical Sciences": 5,
    "Social Sciences": 6,
    "Communication A": 7,
    "Communication B": 8,
    "Quantitative Reasoning A": 9,
    "Quantitative Reason B": 10,
    "Ethnic Studies": 11,
    "Elementary": 12,
    "Intermediate": 13,
    "Advanced": 14,
    "Honors": 15,
    "Accelerated Honors": 16,
    "Honors Optional": 17,
    "50% Graduate Coursework Requirement": 18,
    "Workplace Experience": 19,
    "Community Based Learning": 20,
    "Repeatable for Credit": 21,
}

# Similar to check_boxes, but for choose one only. For our purposes, pretty much identical because we are only ever gonna select one.
# mat-radio-n-input
select_boxes = {
    "In-Person": 3,
    "Hybrid": 4,
    "Online Only (Async)": 5,
    "Online Only (Sync)": 6,
    "Online Only (All)": 7,
    "Language 1st Semester": 10,
    "Language 2nd Semester": 11,
    "Language 3rd Semester": 12,
    "Language 4th Semester": 13,
    "Language 5th Semester": 14,
}


chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-extensions")

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 4)


def open_dropdown(is_checkbox, number, driver=driver):
    """
    Opens the dropdown for the given checkbox or select box. If is_checkbox is True, then it's a checkbox, otherwise it's a select box.
    """
    filter_name = None
    if is_checkbox:
        if number <= 6:
            filter_name = "Breadth filter"
        elif number <= 11:
            filter_name = "General Education filter"
        elif number <= 14:
            filter_name = "Level filter"
        elif number <= 17:
            filter_name = "Honors filter"
        else:
            filter_name = "Course Attributes filter"
    else:
        if number <= 7:
            filter_name = "Mode of Instruction filter"
        else:
            filter_name = "Language filter"

    dropdown = driver.find_element(
        By.CSS_SELECTOR, f"summary[aria-label='{filter_name}']"
    )
    dropdown.click()
    time.sleep(1)


def click_box(is_checkbox, number, driver=driver):
    """
    Clicks the checkbox or select box with the given number. If is_checkbox is True, then it's a checkbox, otherwise it's a select box.
    """
    if is_checkbox:
        checkbox = driver.find_element(By.ID, f"mat-mdc-checkbox-{number}-input")
    else:
        checkbox = driver.find_element(By.ID, f"mat-radio-{number}-input")
    checkbox.click()
    time.sleep(1)


courses = {}  # course code: course object
for input_type in [check_boxes, select_boxes]:
    time.sleep(1)
    for name, number in input_type.items():
        time.sleep(1)
        print(name, number)
        url = "https://public.enroll.wisc.edu/search?closed=true"
        driver.get(url)

        if input_type == check_boxes:
            open_dropdown(True, number, driver)  # Opens the dropdown for checkboxes
            click_box(True, number, driver)  # Clicks the checkbox
        else:
            open_dropdown(False, number, driver)  # Opens the dropdown for select boxes
            click_box(False, number, driver)  # Clicks the select box

        with open("response.html", "w") as file:
            file.write(driver.page_source)
        quit()
        while True:
            search_results = driver.find_element(By.TAG_NAME, "cse-search-results")

            course_codes = search_results.find_elements(
                By.CSS_SELECTOR, ".left.grow.catalog"
            )
            course_codes = [
                element.get_attribute("innerText") for element in course_codes
            ]
            for course_code in course_codes:
                if course_code not in courses:
                    courses[course_code] = Course()

                if input_type == check_boxes:
                    if number <= 6:
                        courses[course_code].breadth = name
                    elif number <= 11:
                        courses[course_code].general_education = name
                    elif number <= 14:
                        courses[course_code].level = name
                    else:
                        courses[course_code].course_attributes = name
                else:
                    if number <= 7:
                        courses[course_code].mode_of_instruction = name
                    else:
                        courses[course_code].language = name

            pages = (
                driver.find_element(
                    By.XPATH, "//span[starts-with(normalize-space(.), 'Page')]"
                )
                .get_attribute("innerText")
                .split(" ")
            )
            print(pages[1], pages[3])
            if pages[1] == pages[3]:
                break

            next_page_button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//mat-icon[contains(text(), 'keyboard_arrow_right')]/ancestor::button",
                    )
                )
            )

            with open("next_page_button.html", "w") as file:
                file.write(next_page_button.get_attribute("outerHTML"))
            next_page_button.click()
