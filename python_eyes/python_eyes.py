from datetime import datetime
from time import time
from os import path, mkdir
from loguru import logger

import cv2
import numpy

white_color = (255, 255, 255)
red_color = (0, 0, 255)
blue_color = (205, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX


class PythonEyes:

    def __init__(self, driver,
                 expected_images_dir: str,
                 path_to_result_images: str,
                 logs_enable: bool = False,
                 is_appium: bool = False):
        """
        Init for  PythonEyes class

        :param driver: Selenium or Appium webrdiver
        :param expected_images_dir: str folder for all Images for expected result
        :param path_to_result_images: str folder for all Images with difference
        :param logs_enable: bool ON/OFF logs
        :param is_appium: bool Driver is appium
        """
        self.driver = driver
        self.expected_dir = expected_images_dir
        self.path_to_result_images = path_to_result_images
        self.logs_enable = logs_enable
        self.is_appium = is_appium
        self.expected_image_name = None
        self.path_to_image_with_difference = None
        self.image_with_difference = None
        self.image_id = None
        self._set_up()

    def _set_up(self) -> None:
        """
        Functionality to create all needed directories

        :return: None
        """
        if not path.exists(self.expected_dir) or \
                not path.isdir(self.expected_dir):
            mkdir(self.expected_dir)
            self._info("Expected images directory is created")
        if not path.exists(self.path_to_result_images) or \
                not path.isdir(self.path_to_result_images):
            mkdir(self.path_to_result_images)
            self._info("Directory for result images is created")
        if not path.exists("tmp") or \
                not path.isdir("tmp"):
            mkdir("tmp")
            self._info("Temp directory is created")

    def _info(self, msg: str) -> None:
        """
        Functionality turn on and off logs

        :param msg: str text to display in logs
        :return: None
        """
        if self.logs_enable:
            logger.info(msg)

    def _image_resize(self, img: numpy.ndarray) -> numpy.ndarray:
        if self.is_appium:
            all_system_bars = self.driver.get_system_bars()
            status_bar = all_system_bars.get("statusBar")
            nav_bar = all_system_bars.get("navigationBar")
            if status_bar and status_bar.get("visible"):
                img = img[status_bar.get("height"):, :]
            if nav_bar and nav_bar.get("visible"):
                y_value = nav_bar.get("y") - status_bar.get("height")
                img = img[:y_value, :]
        return img

    def _expected_image_path(self, screen_name: str, img_h: int, img_w: int) -> str:
        """
        Functionality to generate expected result path based on
        image name, size and platform

        :param screen_name: str image name
        :param img_h: int image height
        :param img_w: int image width
        :return: str path for expected image
        """
        if self.is_appium:
            platform_name = self.driver.desired_capabilities.get("platformName").lower()
            return f"{self.expected_dir}/" \
                   f"{screen_name.split('.')[0]}_" \
                   f"{platform_name}_{img_h}_{img_w}.png"
        return f"{self.expected_dir}/" \
               f"{screen_name.split('.')[0]}_{img_h}_{img_w}.png"

    def _find_difference(self, screen_state: str) -> bool:
        """
        This function is created to find a difference between two images

        :param screen_state: str path to template image
        :return: bool images different or not
        """

        # saving screen state name
        self.expected_image_name: str = screen_state
        # taking a screen shot to get a screen size
        self.driver.save_screenshot("tmp/screen.png")
        temp_img = cv2.imread("tmp/screen.png")
        temp_img = self._image_resize(temp_img)
        img_h, img_w, _ = temp_img.shape
        # creating paths
        expected_img_path = self._expected_image_path(screen_state, img_h, img_w)
        actual_img_path = f"tmp/{screen_state.split('.')[0]}_{img_h}_{img_w}.png"
        # saving screenshot
        self.driver.save_screenshot(actual_img_path)
        self._info(f"Expected result path: {expected_img_path}")
        self._info(f"Actual result path: {actual_img_path}")
        # loading images
        actual = cv2.imread(actual_img_path)
        actual = self._image_resize(actual)
        if not path.exists(expected_img_path):
            cv2.imwrite(expected_img_path, actual)
            logger.warning(f"Image {expected_img_path} is not found. Saving current screenshot")
        screen_state = cv2.imread(expected_img_path)
        # checking that shape is same
        assert screen_state.shape == actual.shape, "Width or Height of the images are not the same"
        # compute difference
        difference = cv2.subtract(screen_state, actual)
        difference_2 = cv2.subtract(actual, screen_state)
        # color the mask red
        conv_hsv_gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
        conv_hsv_gray_2 = cv2.cvtColor(difference_2, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("1.png", conv_hsv_gray)
        cv2.imwrite("2.png", conv_hsv_gray_2)

        # add contrast to image
        # THIS ONE IS VERY IMPORTANT NOT TO LOSE ALL DIFFERENCE
        conv_hsv_gray[conv_hsv_gray != 0] = 255
        conv_hsv_gray_2[conv_hsv_gray_2 != 0] = 255
        mask = cv2.threshold(conv_hsv_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        mask_2 = cv2.threshold(conv_hsv_gray_2, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        # calculating difference
        total_pixels = screen_state.shape[0] * screen_state.shape[1]
        amount_of_different_px = cv2.countNonZero(conv_hsv_gray) + cv2.countNonZero(conv_hsv_gray_2)
        percent_of_dif = float(amount_of_different_px * 100 / total_pixels)
        self._info(f"Different: {percent_of_dif:.5f}%")
        is_different = percent_of_dif > 0.0002
        self._info(f"IS_DIFFERENT == {is_different}")
        # saving image with difference
        if is_different:
            actual[mask != 255] = red_color
            actual[mask_2 != 255] = blue_color
            self._create_report_image(screen_state, actual)
        else:
            self._info("Images are same")
        return is_different

    def _save_image_with_difference(self) -> None:
        """
        Functionality to save image with difference

        :return: None
        """
        self._info(f"Saving image with difference."
                   f" Path: {self.path_to_image_with_difference}")
        cv2.imwrite(self.path_to_image_with_difference, self.image_with_difference)

    @staticmethod
    def _calculate_text_coordinates(image_h: int, image_w: int) -> list:
        """
        Functionality to calculate text coordinates

        :param image_h: int height of the screen
        :param image_w: int width of the screen
        :return: list of coordinates to place text
        """
        total_w = 2 * image_w
        text_x_location = image_h + 70
        y_1 = int(total_w * 0.20)
        y_2 = int(total_w * 0.73)
        return [(y_1, text_x_location), (y_2, text_x_location)]

    @staticmethod
    def _write_text(img: numpy.ndarray, text: str,
                    coordinates: tuple, font_size: int = 2) -> None:
        """
        Functionality to write text on images

        :param img: ndarray image to modify
        :param text: str text to write
        :param coordinates: tuple coordinates for text
        :param font_size: int font size
        :return:
        """
        cv2.putText(img, text,
                    coordinates,
                    FONT, font_size,
                    white_color, 2,
                    cv2.LINE_AA)

    @staticmethod
    def _get_current_date_as_str(type_of_format: int = 0) -> str:
        """
        Functionality to get a datetime.now() as a string in needed format

        :param type_of_format: int type of format to return
        :return: str datetime.now() in needed format
        """
        now = datetime.now()
        if type_of_format == 1:
            return f"{now.day}_{now.month}_{now.year}_{now.hour}_{now.minute}_{now.second}"
        return f"{now.day}.{now.month}.{now.year} {now.hour}:{now.minute}:{now.second}"

    def _create_report_image(self, expected: numpy.ndarray, actual: numpy.ndarray) -> None:
        """
        Creating one image from Expected and Actual screenshots

        :param expected: ndarray
        :param actual:  ndarray
        """
        # creating new path for image with difference
        self.path_to_image_with_difference = f"{self.path_to_result_images}/" \
                                             f"{self.expected_image_name.split('.')[0]}" \
                                             f"_{self.image_id}.png"
        # adding a border to visually separate to images
        size_of_line_between_images = 5
        expected = cv2.copyMakeBorder(expected, 0, 0, 0,
                                      size_of_line_between_images,
                                      cv2.BORDER_CONSTANT, value=(0, 0, 0))
        im_v = cv2.hconcat([expected, actual])
        # adding border for text
        im_v = cv2.copyMakeBorder(im_v, 0, 220, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        # calculating coordinates for text
        text_coordinates = self._calculate_text_coordinates(expected.shape[0], expected.shape[1])
        # creating date text and calculating coordinates
        image_h, image_w, _ = expected.shape
        date_text = self._get_current_date_as_str()
        info_text_coordinates = (10, image_h + 120)
        blue_description = (int(image_w * 1.22), image_h + 160)
        red_description = (int(image_w * 1.22), image_h + 200)
        blue_line_start = (int(image_w * 1.1), image_h + 150)
        blue_line_end = (int(image_w * 1.2), image_h + 150)
        red_line_start = (int(image_w * 1.1), image_h + 190)
        red_line_end = (int(image_w * 1.2), image_h + 190)
        image_name_coordinates = (10, image_h + 160)
        date_text_coordinates = (10, image_h + 200)
        # adding text
        self._write_text(im_v, "Expected", text_coordinates[0])
        self._write_text(im_v, "Actual", text_coordinates[1])
        self._write_text(im_v, "Image info: ", info_text_coordinates, font_size=1)
        self._write_text(im_v, f"{self.expected_image_name}",
                         image_name_coordinates, font_size=1)
        self._write_text(im_v, f"{date_text}", date_text_coordinates, font_size=1)
        self._write_text(im_v, "Expected has and not on Actual", blue_description, font_size=1)
        self._write_text(im_v, "Actual has and not on Expected", red_description, font_size=1)
        cv2.line(im_v, blue_line_start, blue_line_end, blue_color, 15)
        cv2.line(im_v, red_line_start, red_line_end, red_color, 15)
        self.image_with_difference = im_v

    def verify_screen(self, expected: str, hard_assert: bool = True, timeout: int = 2) -> None:
        """
        Screen state verification functionality

        :param expected: str Screen state name
        :param hard_assert: bool raise AssertionError or just display a error message
        :param timeout: int wait for loading to override default timeout
        :return: None
        """
        different = False
        self.image_id = self._get_current_date_as_str(1)
        timeout = int(time()) + timeout
        while int(time()) <= timeout:
            different = self._find_difference(expected)
            if not different:
                break
        else:
            self._save_image_with_difference()
            error_message = f"Expected and Actual images are different for " \
                            f"{self.expected_image_name}" \
                            f"Image to check difference: {self.path_to_image_with_difference}"
            if hard_assert:
                assert not different, error_message
            self._info(error_message)
