from pathlib import Path
from PIL import Image
SUPPORTED_EXTENSIONS={".jpg",".jpeg",".png",".webp"}
def load_folder_dataset(root, category_to_index):
    root=Path(root)
    if not root.exists(): raise FileNotFoundError(f"Dataset folder does not exist: {root}")
    dataset=[]
    for folder in sorted(root.iterdir()):
        if not folder.is_dir(): continue
        class_name=folder.name.replace("_"," ").lower()
        if class_name not in category_to_index: raise ValueError(f"Unknown model class folder: {folder.name}")
        target=category_to_index[class_name]
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS: continue
            dataset.append((Image.open(path).convert("RGB"),target))
    if not dataset: raise ValueError(f"No supported images found in {root}")
    return dataset
