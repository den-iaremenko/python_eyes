from time import time
from os import path, mkdir
from loguru import logger

import cv2
import numpy

white_color = (255, 255, 255)
red_color = (0, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


class PythonEyes:

    def __init__(self, driver,
                 expected_images_dir: str,
                 path_to_result_images: str,
                 logs_enable: bool = False):
        """
        Init for  PythonEyes class

        :param driver: Selenium or Appium webrdiver
        :param expected_images_dir: str folder for all Images for expected result
        :param path_to_result_images: str folder for all Images with difference
        :param logs_enable: bool ON/OFF logs
        """
        self.driver = driver
        self.expected_dir = expected_images_dir
        self.path_to_result_images = path_to_result_images
        self.logs_enable = logs_enable
        self.expected_image_name = None
        self.path_to_image_with_difference = None
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
        img_h, img_w, _ = temp_img.shape
        # creating paths
        expected_img_path = f"{self.expected_dir}/{screen_state.split('.')[0]}_{img_h}_{img_w}.png"
        actual_img_path = f"tmp/{screen_state.split('.')[0]}_{img_h}_{img_w}.png"
        # saving screenshot
        self.driver.save_screenshot(actual_img_path)
        self._info(f"Expected result path: {expected_img_path}")
        self._info(f"Actual result path: {actual_img_path}")
        # loading images
        actual = cv2.imread(actual_img_path)
        if not path.exists(expected_img_path):
            self.driver.save_screenshot(expected_img_path)
            logger.warning(f"Image {expected_img_path} is not found. Saving current screenshot")
        screen_state = cv2.imread(expected_img_path)
        # checking that shape is same
        assert screen_state.shape == actual.shape, "Width or Height of the images are not the same"
        # compute difference
        difference = cv2.subtract(screen_state, actual)
        # color the mask red
        conv_hsv_gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
        # add contrast to image
        # THIS ONE IS VERY IMPORTANT NOT TO LOSE ALL DIFFERENCE
        conv_hsv_gray[conv_hsv_gray != 0] = 255
        mask = cv2.threshold(conv_hsv_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        # calculating difference
        total_pixels = screen_state.shape[0] * screen_state.shape[1]
        percent_of_dif = float(cv2.countNonZero(conv_hsv_gray) * 100 / total_pixels)
        self._info(f"Different: {percent_of_dif:.2f}%")
        is_different = percent_of_dif > 0.0002
        # saving image with difference
        if is_different:
            self._info("Expected image and Actual screen shot are not the same")
            self._info("Creating an image for report")
            actual[mask != 255] = red_color
            self.path_to_image_with_difference = self._create_report_image(screen_state, actual)
            self._info(self.path_to_image_with_difference)
        else:
            self._info("Images are same")
        return is_different

    @staticmethod
    def _calculate_text_coordinates(image_h: int, image_w: int) -> list:
        """
        Functionality to calculate text coordinates

        :param image_shape: tuple of shape (h, w, _)
        :return: list of coordinates to place text
        """
        total_w = 2 * image_w
        text_x_location = image_h + 70
        y_1 = int(total_w * 0.20)
        y_2 = int(total_w * 0.73)
        return [(y_1, text_x_location), (y_2, text_x_location)]

    def _create_report_image(self, expected: numpy.ndarray, actual: numpy.ndarray) -> str:
        """
        Creating one image from Expected and Actual screenshots

        :param expected: ndarray
        :param actual:  ndarray
        :return: path to new created image
        """
        # creating new path for image with difference
        path_to_img = f"{self.path_to_result_images}/" \
                      f"{self.expected_image_name.split('.')[0]}_{self.image_id}.png"
        # adding a border to visually separate to images
        expected = cv2.copyMakeBorder(expected, 0, 0, 0, 10, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        im_v = cv2.hconcat([expected, actual])
        # adding border for text
        im_v = cv2.copyMakeBorder(im_v, 0, 100, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        # calculating coordinates for text
        text_coordinates = self._calculate_text_coordinates(expected.shape[0], expected.shape[1])
        # adding text
        cv2.putText(im_v, "Expected",
                    text_coordinates[0],
                    FONT, 2,
                    white_color, 2,
                    cv2.LINE_AA)
        cv2.putText(im_v, "Actual",
                    text_coordinates[1],
                    FONT, 2,
                    white_color, 2,
                    cv2.LINE_AA)
        # saving image
        cv2.imwrite(path_to_img, im_v)
        return path_to_img

    def verify_screen(self, expected: str, hard_assert: bool = True, timeout: int = 2) -> None:
        """
        Screen state verification functionality

        :param expected: str Screen state name
        :param timeout: int wait for loading to override default timeout
        :param hard_assert: bool raise AssertionError or just display a error message
        :return: None
        """
        different = False
        self.image_id = int(time())
        timeout = int(time()) + timeout
        while int(time()) <= timeout:
            different = self._find_difference(expected)
            if not different:
                break
        else:
            error_message = f"Expected and Actual images are different for " \
                            f"{self.expected_image_name}" \
                            f"Image to check difference: {self.path_to_image_with_difference}"
            if hard_assert:
                assert not different, error_message
            self._info(error_message)
