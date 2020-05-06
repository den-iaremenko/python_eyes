import cv2
import numpy

from loguru import logger
from time import time
from os import path, listdir, mkdir


class PythonEyes:

    def __init__(self, driver, expected_images_dir: str, path_to_result_images: str):
        self.driver = driver
        self.expected_dir = expected_images_dir
        self.path_to_result_images = path_to_result_images
        self.expected_image_name = None
        self.WHITE_COLOR = (255, 255, 255)
        self.RED_COLOR = (0, 0, 255)
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX
        if not path.exists(expected_images_dir) or not path.isdir(expected_images_dir):
            mkdir(expected_images_dir)
            logger.info("Expected images directory is created")
        if not path.exists(path_to_result_images) or not path.isdir(path_to_result_images):
            mkdir(path_to_result_images)
            logger.info("Directory for result images is created")
        if not path.exists("tmp") or not path.isdir("tmp"):
            mkdir("tmp")
            logger.info("Temp directory is created")
        logger.info(f"All files: {listdir()}")

    def find_difference(self, screen_state: str, hard_assert: bool = True) -> bool:
        """
        This function is created to find a difference between two images

        :param screen_state: str path to template image
        :param hard_assert: bool assert or show error in log
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
        logger.info(f"Expected result path: {expected_img_path}")
        logger.info(f"Actual result path: {actual_img_path}")

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
        logger.info(f"Different: {percent_of_dif}")
        is_different = bool(cv2.countNonZero(conv_hsv_Gray))
        if is_different:
            logger.error("Expected image and Actual screen shot are not the same. Creating an image for report")
            actual[mask != 255] = self.RED_COLOR
            path_to_report_img = self.create_report_image(screen_state, actual)
            logger.info(path_to_report_img)
            if hard_assert:
                error_message = f"Expected and Actual screens are not the same for {self.expected_image_name} state. " \
                                f"Image for report: {path_to_report_img}"
                assert not is_different, error_message
        else:
            logger.info("Images are same")
        return is_different

    @staticmethod
    def calculate_coordinates_for_text(image_shape: tuple) -> list:
        """
        Template image shape
        :param image_shape: tuple of shape (h, w, _)
        :return: list of coordinates to place text
        """
        h, w, _ = image_shape
        total_w = 2 * w
        x = h + 70
        y_1 = int(total_w * 0.20)
        y_2 = int(total_w * 0.73)
        return [(y_1, x), (y_2, x)]

    def create_report_image(self, expected: numpy.ndarray, actual: numpy.ndarray) -> str:
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
        coordinates_for_text = self.calculate_coordinates_for_text(expected.shape)
        cv2.putText(im_v, "Expected", coordinates_for_text[0], self.FONT, 2, self.WHITE_COLOR, 2, cv2.LINE_AA)
        cv2.putText(im_v, "Actual", coordinates_for_text[1], self.FONT, 2, self.WHITE_COLOR, 2, cv2.LINE_AA)
        cv2.imwrite(path_to_img, im_v)
        return path_to_img

    def verify_screen(self, expected: str, timeout: int = 3, hard_assert: bool = False) -> bool:
        pass
