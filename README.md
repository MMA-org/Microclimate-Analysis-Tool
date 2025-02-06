# Microclimate Analysis Tool

The **Microclimate Analysis Tool** is an interactive GUI application designed for researchers, urban planners, and stakeholders to analyze the correlation between urbanization trends and climate changes. The tool allows users to upload remote sensing images from different years, perform segmentation to identify urban features, and integrate historical climate data for comprehensive analysis.

## Demo Video

Watch the demonstration of the application to see its core features in action:

[![Demo Video](https://img.youtube.com/vi/demo.mp4/0.jpg)](demo.mp4)

## Microclimate Analysis Sample Dataset

A **Microclimate Analysis Sample Dataset** is included, created using this tool. It showcases project results for selected areas in cities across the USA. This dataset can be used to explore the tool's features and understand the analysis workflow.

## Features

- Upload remote sensing images for different years.
- Add metadata, including location and year of capture.
- Segment images to identify urban and rural features.
- Analyze climate data in correlation with urban growth.
- Visualize trends through dynamic graphs.

## Installation Instructions

### Clone the Repository

```bash
git clone https://github.com/MMA-org/Microclimate-Analysis-Tool.git
cd Microclimate-Analysis-Tool
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Microsoft Visual C++ Build Tools (Required to compile `pydensecrf`)

1. Download from [Microsoft Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. During installation, select **"Desktop development with C++"**.
3. Ensure that the C++ build tools are checked.

### Run the Application

```bash
python main.py
```

## Testing

The tool includes unit tests to ensure reliability and correctness. Tests are implemented using `pytest` and `pytest-qt` for GUI testing.

### Run All Tests

```bash
pytest tests/
```

### Test Files Overview

- **`conftest.py`**: Sets up the testing environment with a shared `QApplication` instance for PyQt5 GUI tests.
- **`test_create_data_controller.py`**: Tests the Create Data page (UI interactions, input validation, file handling, metadata management).
- **`test_segment_data_controller.py`**: Tests the Segment Data page (UI controls, image upload/removal, segmentation process).

## Workflow

### 1. Uploading Images (Create Data Page)

- Click **Browse** to select remote sensing images from your device.
- Click **Upload** to add the selected images to the session.

### 2. Choosing Location or Adding Coordinates

- **Option 1:** Select a country and city from the dropdown menus to automatically fetch coordinates.
- **Option 2:** Manually enter latitude and longitude.

### 3. Adding Image Metadata

- Enter the corresponding **year** for each uploaded image in the provided input fields.

### 4. Saving the Dataset

- Enter a **session name** to identify your dataset.
- Click **Save** to store the images, metadata, and location information.

### 5. Segmenting Images (Segment Data Page)

- Upload new images for segmentation or select an **Existing Dataset** from the dropdown.
- Click **Start Segmentation** to generate segmentation maps, displayed side-by-side with the original images.

### 6. Analyzing Data (Analysis Page)

- Select a saved dataset from the dropdown menu.
- Click **View Analysis** to:
  - Fetch historical climate data based on the dataset’s coordinates.
  - Visualize climate parameters over the years.
  - Display graphs showing the percentage of urban/rural objects.
  - Analyze correlations between urbanization trends and climate changes.

