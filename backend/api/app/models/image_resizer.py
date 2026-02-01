from PIL import Image


class ImageResizer:
    """
    이미지 리사이저
    """

    def resize(self, image, target_width, target_height):
        """
        이미지 리사이즈
        """
        return image.resize((target_width, target_height), Image.LANCZOS)
