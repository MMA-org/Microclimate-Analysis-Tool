from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
from pathlib import Path
import numpy as np
import glob
from PIL import Image
import torch
import torch.nn.functional as F
import pydensecrf.densecrf as dcrf
from pydensecrf.utils import unary_from_softmax
from collections import defaultdict, namedtuple
import json


class LandCoverClasses:
    def __init__(self):
        self.LandCoverClass = namedtuple('LandCoverClass', ['name', 'id', 'color'])
        self.lc_classes = [
            self.LandCoverClass('background', 0, (0, 0, 0)),             # Black
            self.LandCoverClass('Bareland', 1, (255, 0, 0)),             # Red
            self.LandCoverClass('Rangeland', 2, (255, 255, 0)),          # Yellow
            self.LandCoverClass('Developed Space', 3, (192, 192, 192)),  # Gray
            self.LandCoverClass('Road', 4, (255, 255, 255)),             # White
            self.LandCoverClass('Tree', 5, (0, 255, 0)),                 # Green
            self.LandCoverClass('Water', 6, (0, 0, 255)),                # Blue
            self.LandCoverClass('Agriculture land', 7, (128, 0, 128)),   # Purple
            self.LandCoverClass('Building', 8, (255, 165, 0)),           # Orange
        ]

        self.num_labels = len(self.lc_classes)
        self.id2label = {lc.id: lc.name for lc in self.lc_classes}
        self.label2id = {lc.name: lc.id for lc in self.lc_classes}
        self.color_map = {lc.id: lc.color for lc in self.lc_classes}


LandCoverClass = LandCoverClasses()

# Load the SegFormer model
model = SegformerForSemanticSegmentation.from_pretrained(
    "nave1616/SegFormer-landcover-FT",
    num_labels=LandCoverClass.num_labels,
    id2label=LandCoverClass.id2label,
    label2id=LandCoverClass.label2id,
)

feature_extractor = SegformerImageProcessor.from_pretrained("nvidia/segformer-b4-finetuned-ade-512-512")

def generate_segmentation_maps(dataset_path):
    images_path = Path(dataset_path) / "images"
    segmentations_path = Path(dataset_path) / "segmentations"
    segmentations_path.mkdir(exist_ok=True)

    images = glob.glob(str(images_path / "*.png")) + glob.glob(str(images_path / "*.jpg"))
    updated_images = []

    with torch.no_grad():
        for image_path in images:
            image = Image.open(image_path).convert("RGB")
            inputs = feature_extractor(images=image, return_tensors="pt")
            logits = model(**inputs).logits

            refined_output = apply_crf(np.array(image), logits, num_classes=LandCoverClass.num_labels)

            label_freq = calculate_class_percentages(refined_output, Path(image_path).name)
            updated_images.append(label_freq)

            output_path = segmentations_path / (Path(image_path).stem + "_seg.png")
            save_segmentation_image(refined_output, output_path)

    update_json_with_label_freq(updated_images, dataset_path)

def apply_crf(image, logits, num_classes):
    probabilities = F.softmax(logits, dim=1)
    height, width = image.shape[:2]
    probabilities_upsampled = F.interpolate(probabilities, size=(height, width), mode="bilinear", align_corners=False)
    probabilities_np = probabilities_upsampled.squeeze(0).cpu().numpy()

    d = dcrf.DenseCRF2D(width, height, num_classes)
    unary = unary_from_softmax(probabilities_np)
    d.setUnaryEnergy(np.ascontiguousarray(unary))

    d.addPairwiseGaussian(sxy=(3, 3), compat=4)
    d.addPairwiseBilateral(sxy=(3, 3), srgb=20, rgbim=image, compat=5)

    refined = d.inference(5)
    return np.argmax(np.array(refined), axis=0).reshape((height, width))

def save_segmentation_image(segmentation_map, output_path):
    color_image = np.zeros((*segmentation_map.shape, 3), dtype=np.uint8)
    for class_id, color in LandCoverClass.color_map.items():
        color_image[segmentation_map == class_id] = color
    Image.fromarray(color_image).save(output_path)

def calculate_class_percentages(segmentation_map, image_filename):
    class_counts = defaultdict(int)
    total_pixels = segmentation_map.size

    for class_id in range(1, LandCoverClass.num_labels):
        class_counts[class_id] = np.sum(segmentation_map == class_id)

    label_freq = [class_counts[class_id] / total_pixels for class_id in range(1, LandCoverClass.num_labels)]
    return {'image_filename': image_filename, 'label_freq': label_freq}

def update_json_with_label_freq(updated_images, dataset_path):
    json_path = Path(dataset_path) / "metadata.json"
    if not json_path.exists():
        print(f"metadata.json not found in {dataset_path}")
        return

    with open(json_path, 'r') as f:
        try:
            metadata = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {json_path}")
            return

    if "coordinates" in metadata:
        metadata["coordinates"]["latitude"] = float(metadata["coordinates"].get("latitude", 0))
        metadata["coordinates"]["longitude"] = float(metadata["coordinates"].get("longitude", 0))

    for updated_image in updated_images:
        image_filename = updated_image['image_filename']
        label_freq = updated_image['label_freq']

        rounded_freq = [round(freq, 2) for freq in label_freq]

        if "images" not in metadata:
            metadata["images"] = {}

        if image_filename in metadata["images"]:
            image_data = metadata["images"][image_filename]
            year = image_data.get("year")

            metadata["images"][image_filename] = {
                "year": year,
                "freq": rounded_freq
            }
        else:
            print(f"Warning: No year data found for image '{image_filename}' in metadata.json.")

    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=4)


