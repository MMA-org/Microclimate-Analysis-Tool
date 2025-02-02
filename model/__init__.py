import warnings
warnings.filterwarnings(
    "ignore", category=UserWarning, module="transformers.utils.deprecation"
)
from model import generate_segmentation_maps
__all__ = [generate_segmentation_maps]