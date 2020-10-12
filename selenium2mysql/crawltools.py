import pyperclip
import pyautogui
from .__init__ import Crawler
from pathlib import Path


def make_image_from_component_with_xpath(crawler: Crawler, xpath: str, image_path: str):
    try:

        tmp_tag = crawler.driver.find_element_by_xpath(xpath)
        print(tmp_tag.text)
        tmp_file = open(image_path, "wb")
        tmp_file.write(tmp_tag.screenshot_as_png)
        tmp_file.close()

    except Exception as e:
        print("cannot make image from xpath : {}".foramt(xpath))
        print(e)


def click_using_pyautogui_with_xpath(crawler: Crawler, xpath: str):
    try:
        crawler.driver.scroll_down_xpath(xpath)
        make_image_from_component_with_xpath(crawler, xpath, "./tmp_image4crawl.png")
        tmp_point = pyautogui.locateCenterOnScreen("./tmp_image4crawl.png")
        pyautogui.click(tmp_point)
        Path("./tmp_image4crawl.png").unlink()

    except Exception as e:
        print("cannot click xpath : {}".foramt(xpath))
        print(e)


def type_using_pyautogui_with_xpath(crawler: Crawler, xpath: str, input_text: str):
    try:
        pyperclip.copy(input_text)
        click_using_pyautogui_with_xpath(crawler, xpath)
        pyautogui.hotkey("command", "v")

    except Exception as e:
        print("cannot type into xpath : {}".foramt(xpath))
        print(e)


def make_image_from_component_with_class(crawler: Crawler, class_name: str, image_path: str):
    try:

        tmp_tag = crawler.driver.find_element_by_class_name(class_name)
        print(tmp_tag.text)
        tmp_file = open(image_path, "wb")
        tmp_file.write(tmp_tag.screenshot_as_png)
        tmp_file.close()

    except Exception:
        print(Exception)


def click_using_pyautogui_with_class(crawler: Crawler, class_name: str):
    try:
        crawler.driver.scroll_down_class(class_name)
        make_image_from_component_with_class(crawler, class_name, "./tmp_image4crawl.png")
        tmp_point = pyautogui.locateCenterOnScreen("./tmp_image4crawl.png")
        pyautogui.click(tmp_point)
        Path("./tmp_image4crawl.png").unlink()
    except Exception:
        print(Exception)


def type_using_pyautogui_with_class(crawler: Crawler, class_name: str, input_text: str):
    try:
        pyperclip.copy(input_text)
        click_using_pyautogui_with_xpath(crawler, class_name)
        pyautogui.hotkey("command", "v")
    except Exception:
        print(Exception)
