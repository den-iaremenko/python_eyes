import cv2
import numpy

from loguru import logger
from time import time
from os import path, listdir, mkdir


class PythonEyes:

    def __init__(self, driver, expected_images_dir: str,
                 path_to_result_images: str,
                 logs_enable: bool = False):
        self.driver = driver
        self.expected_dir = expected_images_dir
        self.path_to_result_images = path_to_result_images
        self.logs_enable = logs_enable
        self.expected_image_name = None
        self.path_to_image_with_difference = None
        self.WHITE_COLOR = (255, 255, 255)
        self.RED_COLOR = (0, 0, 255)
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX
        if not path.exists(expected_images_dir) or not path.isdir(expected_images_dir):
            mkdir(expected_images_dir)
            self.info("Expected images directory is created")
        if not path.exists(path_to_result_images) or not path.isdir(path_to_result_images):
            mkdir(path_to_result_images)
            self.info("Directory for result images is created")
        if not path.exists("tmp") or not path.isdir("tmp"):
            mkdir("tmp")
            self.info("Temp directory is created")
        self.info(f"All files: {listdir()}")
        
    def info(self, msg: str) -> None:
        """
        This function is created to be able to turn on and off logs

        :param msg: str text to display in logs
        :return: None
        """
        if self.logs_enable:
            self.info(msg)
        
    def _find_difference(self, screen_state: str) -> bool:
        """
        This function is created to find a difference between two images

        :param screen_state: str path to template image
        :return: bool images different or not
        """
        # taking a screen shot to get size
        self.driver.save_screenshot("tmp/screen.png")
        temp_img = cv2.imread("tmp/screen.png")
        h, w, _ = temp_img.shape

        # creating paths
        self.expected_image_name: str = screen_state
        expected_img_path = f"{self.expected_dir}/{screen_state.split('.')[0]}_{h}_{w}.png"
        actual_img_path = f"tmp/{screen_state.split('.')[0]}_{h}_{w}.png"

        # saving screenshot
        self.driver.save_screenshot(actual_img_path)
        self.info(f"Expected result path: {expected_img_path}")
        self.info(f"Actual result path: {actual_img_path}")

        # loading images
        actual = cv2.imread(actual_img_path)
        if not path.exists(expected_img_path):
            self.driver.save_screenshot(expected_img_path)
            logger.warning(f"Image {expected_img_path} is not found. Saving current screenshot")
        screen_state = cv2.imread(expected_img_path)

        # checking that images are with same size
        assert screen_state.shape == actual.shape, "Width or Height of the images are not the same"

        # compute difference
        difference = cv2.subtract(screen_state, actual)

        # color the mask red
        conv_hsv_Gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

        # add contrast to image
        # THIS ONE IS VERY IMPORTANT NOT TO LOSE ALL DIFFERENCE
        conv_hsv_Gray[conv_hsv_Gray != 0] = 255

        ret, mask = cv2.threshold(conv_hsv_Gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        # check that images are different, if images are same then f returns False
        total_pixels = screen_state.shape[0] * screen_state.shape[1]
        percent_of_dif = float(cv2.countNonZero(conv_hsv_Gray) * 100 / total_pixels)
        self.info(f"Different: {percent_of_dif:.2f}%")
        is_different = bool(cv2.countNonZero(conv_hsv_Gray))
        if is_different:
            self.info("Expected image and Actual screen shot are not the same. Creating an image for report")
            actual[mask != 255] = self.RED_COLOR
            path_to_image_with_difference = self._create_report_image(screen_state, actual)
            self.path_to_image_with_difference = path_to_image_with_difference
            self.info(path_to_image_with_difference)
        else:
            self.info("Images are same")
        return is_different

    @staticmethod
    def _calculate_coordinates_for_text(image_shape: tuple) -> list:
        """
        This Function is to calculate text coordinates

        :param image_shape: tuple of shape (h, w, _)
        :return: list of coordinates to place text
        """
        h, w, _ = image_shape
        total_w = 2 * w
        x = h + 70
        y_1 = int(total_w * 0.20)
        y_2 = int(total_w * 0.73)
        return [(y_1, x), (y_2, x)]

    def _create_report_image(self, expected: numpy.ndarray, actual: numpy.ndarray) -> str:
        """
        Creating one image from template and current screenshots

        :param expected: ndarray
        :param actual:  ndarray
        :return: path to new created image
        """
        path_to_img = f"{self.path_to_result_images}/{self.expected_image_name.split('.')[0]}_{int(time())}.png"
        expected = cv2.copyMakeBorder(expected, 0, 0, 0, 10, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        im_v = cv2.hconcat([expected, actual])
        im_v = cv2.copyMakeBorder(im_v, 0, 100, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        coordinates_for_text = self._calculate_coordinates_for_text(expected.shape)
        cv2.putText(im_v, "Expected", coordinates_for_text[0], self.FONT, 2, self.WHITE_COLOR, 2, cv2.LINE_AA)
        cv2.putText(im_v, "Actual", coordinates_for_text[1], self.FONT, 2, self.WHITE_COLOR, 2, cv2.LINE_AA)
        cv2.imwrite(path_to_img, im_v)
        return path_to_img

    def verify_screen(self, expected: str, hard_assert: bool = True, timeout: int = 3) -> None:
        """
        Screen state verification functionality

        :param expected: str Screen state name like main_page_with_text.png or login_screen_with_error.png
        :param timeout: int wait for loading to override default timeout
        :param hard_assert: bool raise AssertionError or just display a error message
        :return: None
        """
        timeout = int(time()) + timeout
        while int(time()) <= timeout:
            is_different = self._find_difference(expected)
            if not is_different:
                break
        else:
            error_message = f"Expected and Actual images are different for {self.expected_image_name}" \
                            f"Image to check difference: {self.path_to_image_with_difference}"
            if hard_assert:
                raise AssertionError(error_message)
            self.info(error_message)
