from PIL import Image

from failurelab.datasets import load_folder_dataset


def test_load_folder_dataset(tmp_path):
    class_folder = (
        tmp_path
        / "golden_retriever"
    )

    class_folder.mkdir()

    image_path = (
        class_folder
        / "sample.jpg"
    )

    Image.new(
        "RGB",
        (10, 10),
        color=(200, 200, 200),
    ).save(image_path)

    category_to_index = {
        "golden retriever": 5,
    }

    dataset = load_folder_dataset(
        root=tmp_path,
        category_to_index=category_to_index,
    )

    assert len(dataset) == 1

    image, target = dataset[0]

    assert image.size == (10, 10)
    assert target == 5