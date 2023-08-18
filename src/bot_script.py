from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import time

cameraPage = "https://www.bestbuy.com/site/fujifilm-x-series-x100v-26-1mp-digital-camera-silver/6400570.p?skuId=6400570"

with open("config.json") as json_file:
    config = json.load(json_file)

password = config["password"]
cvv = config["cvv"]


def initializeDriver():
    # Use Chrome driver and options
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-data-dir=/Users/gk/Library/Application Support/Google/Chrome/Default"
    )
    driver = uc.Chrome(options=options)
    return driver


def main():
    driver = initializeDriver()
    driver.maximize_window()
    driver.get("https://www.bestbuy.com/")
    stockAlert(driver)


def stockAlert(driver):
    count = 0
    inStock = False
    while not inStock:
        count += 1
        try:
            driver.get(cameraPage)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            item = soup.find(
                "button",
                {
                    "class": "c-button c-button-primary c-button-lg c-button-block c-button-icon c-button-icon-leading add-to-cart-button",
                    "data-button-state": "ADD_TO_CART",
                },
            )
            if not item:
                state = "SOLD_OUT"
            else:
                state = item.get("data-button-state")
            if state != "SOLD_OUT":
                inStock = True
                print("Item is in stock")
                checkout(driver)
            else:
                print("Item is not in stock", count)
            # time.sleep(1) # I thnk I should
        except TimeoutException:
            print("Timeout occurred. Retrying...")
            driver.refresh()
        except Exception as e:
            print("An error occurred while loading:", e)
            driver.refresh()


def checkout(driver):
    wait = WebDriverWait(driver, 30)
    short_wait = WebDriverWait(driver, 3)

    add_to_cart_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "add-to-cart-button"))
    )
    add_to_cart_button.click()
    print("added to cart!")

    go_to_cart_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "go-to-cart-button"))
    )
    go_to_cart_button.click()
    print("going to cart!")

    select_shipping_option_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//input[contains(@id, 'fulfillment-shipping-') and @type='radio']",
            )
        )
    )
    select_shipping_option_button.click()
    print("selected shipping option!")

    time.sleep(1)

    checkout_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
    )
    checkout_button.click()
    print("going to checkout!")

    continue_to_payment_button_present = EC.presence_of_element_located(
        (By.CLASS_NAME, "btn-secondary")
    )
    continue_to_payment_button = None

    try:
        continue_to_payment_button = short_wait.until(
            continue_to_payment_button_present
        )
    except:
        pass

    if continue_to_payment_button is not None:
        continue_to_payment_button.click()
    else:
        print("Continue to payment button is not present")

    password_field_present = EC.presence_of_element_located((By.ID, "fld-p1"))
    password_field = None

    try:
        password_field = short_wait.until(password_field_present)
    except:
        pass

    if password_field is not None:
        password_field.send_keys(password)
        print("entered password!")
        sign_in_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cia-form__controls__submit"))
        )
        sign_in_button.click()
    else:
        print("Password field is not present, skipping login.")

    cvv_field = wait.until(EC.presence_of_element_located((By.ID, "cvv")))
    cvv_field.send_keys(cvv)
    print("entered cvv!")

    place_order_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
    )
    place_order_button.click()
    print("checkout complete!")


if __name__ == "__main__":
    main()
