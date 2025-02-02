from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
from pathlib import Path
import numpy as np
import glob
from PIL import Image
import torch
import torch.nn.functional as F
import pydensecrf.densecrf as dcrf
from pydensecrf.utils import unary_from_softmax
from collections import defaultdict
import json
from collections import namedtuple

# Define a namedtuple for the segmentation classes

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
        
        # create id2label, label2id, and color_map from lc_classes
        self.num_labels = len(self.lc_classes)
        self.id2label = {lc.id: lc.name for lc in self.lc_classes}
        self.label2id = {lc.name: lc.id for lc in self.lc_classes}
        self.color_map = {lc.id: lc.color for lc in self.lc_classes}


LandCoverClass = LandCoverClasses()
# Load SegFormer model and feature extractor
model = SegformerForSemanticSegmentation.from_pretrained(
    "nave1616/SegFormer-landcover-FT",
    num_labels=LandCoverClass.num_labels,
    id2label=LandCoverClass.id2label, 
    label2id=LandCoverClass.label2id,
)

feature_extractor = SegformerImageProcessor.from_pretrained("nvidia/segformer-b4-finetuned-ade-512-512")

def generate_segmentation_maps(data_dir):
    images_path = Path(data_dir) / "images"
    maps_path = Path(data_dir) / "segmentations"
    images = glob.glob(str(images_path / "*.png")) + glob.glob(str(images_path / "*.jpg"))
    
    updated_images = []
    with torch.no_grad():  # No need for gradients during inference
        for image_path in images:
            image = Image.open(image_path)
            # Prepare the image for SegFormer model
            inputs = feature_extractor(images=image, return_tensors="pt")
            
            # Get the logits from the model
            logits = model(**inputs).logits  # Shape: [batch_size, num_classes, H, W]
            
            # Apply CRF to the logits
            refined_output = apply_crf(np.array(image), logits, num_classes=LandCoverClass.num_labels)
            
            # Calculate label percentages (class 1 to 8)
            label_freq = calculate_class_percentages(refined_output, Path(image_path).name)
            updated_images.append(label_freq)
            
            # Save the output with color map
            output_path = maps_path / (Path(image_path).stem + "_seg.png")
            save_segmentation_image(refined_output, output_path)
            
    update_json_with_label_freq(updated_images,data_dir)
            
            

def apply_crf(image, logits, num_classes):
    """
    Apply a simpler post-processing CRF to the output of SegFormer.
    - `image`: The original input image.
    - `logits`: The model output logits (before softmax).
    - `num_classes`: The number of segmentation classes.
    """
    # Apply softmax to logits to get class probabilities
    probabilities = F.softmax(logits, dim=1)  # Shape: [batch_size, num_classes, height, width]
    
    height, width = image.shape[:2]
    probabilities_upsampled = F.interpolate(probabilities, size=(height, width), mode="bilinear", align_corners=False)
    probabilities_np = probabilities_upsampled.squeeze(0).cpu().numpy()
    road_class_index = 4  # Assuming road is class 4
    probabilities_np[road_class_index] += 0.15 # Boost road confidence slightly
    probabilities_np[8] += 0.1
    probabilities_np = probabilities_np / probabilities_np.sum(axis=0, keepdims=True)
    # Convert the image to numpy for CRF processing
    image_np = np.array(image)

    # Initialize CRF
    d = dcrf.DenseCRF2D(width, height, num_classes)

    # Convert probabilities to unary energy (negative log of probabilities)
    unary = unary_from_softmax(probabilities_np)
    unary = np.ascontiguousarray(unary)  # Ensure the unary energy is contiguous
    d.setUnaryEnergy(unary)

    # Gaussian Pairwise: Spatial smoothness
    d.addPairwiseGaussian(sxy=(3, 3), compat=4, kernel=dcrf.DIAG_KERNEL, normalization=dcrf.NORMALIZE_SYMMETRIC)

    # Bilateral Pairwise: Edge refinement (sharper roads, better object boundaries)
    d.addPairwiseBilateral(sxy=(3,3), srgb=20, rgbim=image_np,
                            compat=5,  # Higher for better class separation
                            kernel=dcrf.FULL_KERNEL,  
                            normalization=dcrf.NORMALIZE_SYMMETRIC)

    refined = d.inference(5)  # Run 3 iterations of inference

    # Convert refined output to segmentation map
    refined_map = np.argmax(np.array(refined), axis=0).reshape((height, width))

    return refined_map

def save_segmentation_image(segmentation_map, output_path):
    """
    Save the refined segmentation map as an image with colors.
    """
    class_colors = LandCoverClass.color_map 

    color_image = np.zeros((segmentation_map.shape[0], segmentation_map.shape[1], 3), dtype=np.uint8)

    # Map the class labels to their respective colors
    for class_id, color in class_colors.items():
        color_image[segmentation_map == class_id] = color

    # Save the final image
    img = Image.fromarray(color_image)
    img.save(output_path)

def calculate_class_percentages(segmentation_map,image_filename, num_classes=8):
    """
    Calculate the percentage of each class in the segmentation map.
    Args:
        segmentation_map (numpy.array): The segmentation map with class labels (shape: H, W)
        num_classes (int): The number of classes (excluding class 0)
    
    Returns:
        label_freq (list): The percentage of each class (1 to 8) in the image.
    """
    # Initialize a dictionary to count the pixels for each class
    class_counts = defaultdict(int)
    total_pixels = segmentation_map.size  # Total pixels in the image

    # Count the pixels for each class (1 to 8)
    for class_id in range(1, num_classes + 1):  # Ignore class 0 (background)
        class_counts[class_id] = np.sum(segmentation_map == class_id)

    # Calculate the percentage for each class
    label_freq = [class_counts[class_id] / total_pixels for class_id in range(1, num_classes + 1)]
    return {'image_filename': image_filename,'label_freq': label_freq}

def update_json_with_label_freq(updated_images, data_dir):
    """
    Update the metadata JSON file with the new images data.
    Args:
        updated_images (list): The list of updated image data with the 'label_freq' field.
        data_dir (str): Path to the dataset directory containing the JSON file.
    """
    # Load the existing JSON
    json_path = Path(data_dir) / "metadata.json"
    with open(json_path, 'r') as f:
        metadata = json.load(f)
        
    # Update the "images" field in the metadata with label_freq data
    for updated_image in updated_images:
        image_filename = updated_image['image_filename']
        label_freq = updated_image['label_freq']
        
        if isinstance(metadata["images"].get(image_filename), dict):
            # If "freq" already exists, update it
            metadata["images"][image_filename]["freq"] = label_freq
        else:
            # Otherwise, create a new dictionary structure
            metadata["images"][image_filename] = {
                "year": metadata["images"][image_filename],  # Preserve the original year value
                "freq": label_freq
            }
    # Write the updated data back to the JSON file
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Updated JSON file saved to {json_path}.")

generate_segmentation_maps("dataset")