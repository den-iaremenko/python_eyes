import cv2
import numpy

from time import time


class PythonEye:

    def __init__(self, driver, expected_images_dir: str, path_to_result_images: str):
        self.driver = driver
        self.expected_dir = expected_images_dir
        self.path_to_result_images = path_to_result_images
        self.expected_image_name = None
        self.WHITE_COLOR = (255, 255, 255)
        self.RED_COLOR = (0, 0, 255)
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX

    def find_difference(self, expected: str, actual: str) -> bool:
        """
        This function is created to find a difference between two images

        :param expected: path to template image
        :param actual: path to current state of the app
        :return: bool images different or not
        """
        # load images
        self.expected_image_name: str = expected
        expected = cv2.imread(f"{self.expected_dir}/{expected}")
        actual = cv2.imread(actual)
        assert expected is not None, "Expected is not found"
        assert actual is not None, "Actual image is not found"

        # compute difference
        difference = cv2.subtract(expected, actual)

        # color the mask red
        conv_hsv_Gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

        # add contrast to image
        # THIS ONE IS VERY IMPORTANT NOT TO LOSE ALL DIFFERENCE
        conv_hsv_Gray[conv_hsv_Gray != 0] = 255

        ret, mask = cv2.threshold(conv_hsv_Gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        # Check that images are different, if images are same then f returns False
        total_pixels = expected.shape[0] * expected.shape[1]
        percent_of_dif = float(cv2.countNonZero(conv_hsv_Gray) * 100 / total_pixels)
        print(f"Different: {percent_of_dif}")
        is_different = bool(cv2.countNonZero(conv_hsv_Gray))
        if is_different:
            print("Not the same")
            actual[mask != 255] = self.RED_COLOR
            path_to_img = self.create_report_image(expected, actual)
            print(path_to_img)
        else:
            print("Images are same")
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
        path_to_img = f"{self.path_to_result_images}/{self.expected_image_name}_{int(time())}"
        expected = cv2.copyMakeBorder(expected, 0, 0, 0, 10, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        im_v = cv2.hconcat([expected, actual])
        im_v = cv2.copyMakeBorder(im_v, 0, 100, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        coordinates_for_text = self.calculate_coordinates_for_text(expected.shape)
        cv2.putText(im_v, "Expected", coordinates_for_text[0], self.FONT, 2, self.WHITE_COLOR, 2, cv2.LINE_AA)
        cv2.putText(im_v, "Actual", coordinates_for_text[1], self.FONT, 2, self.WHITE_COLOR, 2, cv2.LINE_AA)
        cv2.imwrite(path_to_img, im_v)
        return path_to_img

    def verify_screen(self, expected: str, timeout: int = 3, hard_assert: bool = False) -> bool:
        """

        :param expected: episode_name
        :param timeout: how long to wait
        :param hard_assert: assert or warning
        :return:
        """
        pass






