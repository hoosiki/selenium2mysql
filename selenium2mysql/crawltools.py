import time
from pathlib import Path

import pyautogui
import pyperclip
from PIL import Image

from .__init__ import Crawler


def make_image_from_component_with_xpath(crawler: Crawler, xpath: str, image_path: str):
    try:

        tmp_tag = crawler.driver.find_element_by_xpath(xpath)
        print(tmp_tag.text)
        tmp_file = open(image_path, "wb")
        tmp_file.write(tmp_tag.screenshot_as_png)
        tmp_file.close()

    except Exception as e:
        print("cannot make image from xpath : {}".format(xpath))
        print(e)


def click_using_pyautogui_with_xpath(crawler: Crawler, xpath: str):
    try:
        crawler.driver.scroll_down_xpath(xpath)
        make_image_from_component_with_xpath(crawler, xpath, "./tmp_image4crawl.png")
        tmp_point = pyautogui.locateCenterOnScreen("./tmp_image4crawl.png")
        pyautogui.click(tmp_point)
        Path("./tmp_image4crawl.png").unlink()

    except Exception as e:
        print("cannot click xpath : {}".format(xpath))
        print(e)


def type_using_pyautogui_with_xpath(crawler: Crawler, xpath: str, input_text: str, special_key="command"):
    try:
        pyperclip.copy(input_text)
        click_using_pyautogui_with_xpath(crawler, xpath)
        pyautogui.hotkey(special_key, "v")

    except Exception as e:
        print("cannot type into xpath : {}".format(xpath))
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


def type_using_pyautogui_with_class(crawler: Crawler, class_name: str, input_text: str, special_key="command"):
    try:
        pyperclip.copy(input_text)
        click_using_pyautogui_with_xpath(crawler, class_name)
        pyautogui.hotkey(special_key, "v")
    except Exception:
        print(Exception)


def workflow(fig_dir: str, type_dict=dict()):
    tmp_path = Path(fig_dir)

    for path in list(str(x) for x in tmp_path.glob("*.jpg")):
        im1 = Image.open(path)
        im1.save(path.replace("jpg", "png"))

    file_path_list = list(str(x) for x in tmp_path.glob("*.png"))

    for i in range(2000):
        tmp_c = str(tmp_path / Path("c{}.png".format(i)))
        tmp_d = str(tmp_path / Path("d{}.png".format(i)))
        if tmp_c in file_path_list:
            tmp_position_c = pyautogui.locateCenterOnScreen(tmp_c)
            print(tmp_position_c, tmp_c)
            if tmp_position_c:
                pyautogui.click(tmp_position_c)
                time.sleep(0.5)
            else:
                print("cannot find pattern {}".format(str(tmp_c)))

        if tmp_d in file_path_list:
            tmp_position_d = pyautogui.locateCenterOnScreen(tmp_d)
            print(tmp_position_d, tmp_d)
            if tmp_position_d:
                pyautogui.click(tmp_position_d)
                pyautogui.press("enter")
                time.sleep(0.5)
            else:
                print("cannot find pattern {}".format(str(tmp_d)))

        if "t{}".format(i) in type_dict.keys():
            pyautogui.typewrite(type_dict["t{}".format(i)])
            time.sleep(0.5)
