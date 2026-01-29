import unittest

from PIL import Image

from backend.pipelines.medieval_character_pipeline import MedievalCharacterPipeline


class TestMedievalCharacterPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = MedievalCharacterPipeline()
        self.test_input = Image.open("test_input.jpg")
        self.description = "medieval fantasy character"

    def test_pipeline(self):
        result = self.pipeline.run(self.test_input, self.description)
        output_image = result["image"]
        output_image.save("test_output.jpg")
        self.assertTrue(output_image is not None)


if __name__ == "__main__":
    unittest.main()
