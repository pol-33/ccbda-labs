# AWS Rekognition Scripts

Collection of scripts for analyzing images using AWS Rekognition.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials:
   - Copy `.env.example` to `.env`
   - Add your AWS credentials
   - **Never commit the `.env` file!**

## Scripts

### `Recognize_1.py` - Label Detection (Local Images)
Analyzes all images in `./images/` and detects labels (objects, scenes, etc.)

**Usage:**
```bash
python Recognize_1.py
```

**Output:** `rekognition_results/{filename}_labels.json`

### `Recognize_2.py` - Web Image Analysis
Extracts insights from web images scraped from UPC website.

**Features:**
- Reads image URLs from `imageScraper/images.json`
- Downloads and analyzes images with Rekognition
- Generates insights summary showing most common labels and patterns
- Prevents re-analyzing the same URL (hash-based caching)

**Usage:**
```bash
python Recognize_2.py
# Enter how many images to analyze when prompted
```

**Output:** 
- Individual analysis: `web_insights/{url_hash}_web_labels.json`
- Insights summary: `web_insights/web_insights_summary.json`
- Downloaded images: `downloaded_images/`


## Features

- ✅ Batch processing of multiple images
- ✅ Duplicate prevention (saves costs by tracking analyzed images)
- ✅ Results saved as JSON files

## Notes

All scripts use a cache system to prevent re-analyzing the same image twice.
