from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from argparse import ArgumentParser


parser = ArgumentParser(description="Removes Students from Canvas course automatically.")
parser.add_argument("--url", type=str, help="Link to the people's tab of the Canvas course, Eg. https://canvas.asu.edu/courses/<code>/users")
parser.add_argument("--username", type=str, help="ASU login username")
parser.add_argument("--password", type=str, help="ASU login password")
parser.add_argument("--limit", type=int, help="Limit student removal", default=25)
parser.add_argument("--exclude", type=str, help="Path to exclude file", required=False)
parser.add_argument("--detach", type=bool, help="Prevent auto-closing of browser", default=True)
parser.add_argument("--timeout", type=int, help="Timeout in seconds", default=60)
args = parser.parse_args()


def handle_duo_login() -> None:
    duo_iframe = driver.find_element(By.CSS_SELECTOR, "#login > iframe")
    driver.switch_to.frame(duo_iframe)

    wait(driver, args.timeout).until(EC.presence_of_element_located((By.ID, "auth_methods")))
    push_option = driver.find_element(By.CLASS_NAME, "push-label")
    push_option.find_element(By.TAG_NAME, "button").click()

    driver.switch_to.parent_frame()


def handle_asu_login() -> None:
    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys(args.username)

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(args.password)

    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()


def wait_for_loading_students() -> None:
    def is_loading() -> bool:
        input = driver.find_element(By.CSS_SELECTOR, "#tab-0 > input[type=hidden]")
        return input.get_attribute("class") == "loading"
    wait(driver, args.timeout).until(lambda _: not is_loading())


def apply_filter(contains: str) -> None:
    wait(driver, args.timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-0 > select")))
    select = driver.find_element(By.CSS_SELECTOR, "#tab-0 > select")
    for option in select.find_elements(By.TAG_NAME, "option"):
        if contains in option.get_attribute("innerHTML"):
            value = option.get_attribute("value")
            Select(select).select_by_value(value)
            break
    wait_for_loading_students()


def remove_students() -> None:
    exclude_names = set()
    if args.exclude != None:
        with open(args.exclude) as file:
            for exclude_name in file.read().splitlines():
                exclude_names.add(exclude_name.strip())
        print(f"Excluding: {exclude_names}")

    removed, retry = 0, 3
    while removed < args.limit:
        apply_filter("Student")

        students = driver.find_elements(By.XPATH, "//tr[contains(@class, 'rosterUser')]")
        student = None
        for possible_student in students:
            student_name = possible_student.find_element(By.CSS_SELECTOR, "td > a").get_attribute("innerHTML")
            student_name = student_name.split("<i>")[0].strip()
            if student_name not in exclude_names:
                print(f"{removed+1} - REMOVING: {student_name}")
                student = possible_student
                break
        if not student:
            print(f"No student found! Removed {removed} students.")
            retry -= 1
            if retry == 0:
                break
            print("Retrying...")
            apply_filter("TA")
            continue

        wait(driver, args.timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td.right > div.admin-links > a")))
        student.find_element(By.CSS_SELECTOR, "td.right > div.admin-links > a").click()

        wait(driver, args.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//td[contains(@class, 'right')][.//a[text()[contains(., 'Remove From Course')]]]")
        ))
        admin_links = student.find_elements(By.CSS_SELECTOR, "td.right > div.admin-links > ul > li > a")
        for admin_link in admin_links:
            if "Remove From Course" in admin_link.get_attribute("innerHTML"):
                admin_link.click()
                break

        wait(driver, args.timeout).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        driver.switch_to.parent_frame()
        removed += 1

        apply_filter("TA")

    print(f"Removed: {removed}. Limit: {args.limit}")


options = Options()
options.add_experimental_option("detach", args.detach)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

if __name__ == "__main__":
    driver.get(args.url)
    driver.maximize_window()

    handle_asu_login()
    handle_duo_login()
    remove_students()