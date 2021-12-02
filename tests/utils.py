import pathlib
import random

test_path = pathlib.Path(__file__).parent.absolute()
files_path = test_path / "files"
images_path = files_path / "sample_images"


def get_random_image(n=1):
    samples = [f for f in images_path.glob("*.png") if f.is_file()]
    return [f.open(mode="rb") for f in random.sample(samples, n)]
