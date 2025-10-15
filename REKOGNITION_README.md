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

### `Recognize_1.py` - Label Detection
Analyzes all images in `./images/` and detects labels (objects, scenes, etc.)

**Usage:**
```bash
python Recognize_1.py
```

**Output:** `rekognition_results/{filename}_labels.json`

### `Recognize_2.py` - Or what comes in next task
TBD


## Features

- ✅ Batch processing of multiple images
- ✅ Duplicate prevention (saves costs by tracking analyzed images)
- ✅ Results saved as JSON files

## Notes

All scripts use a cache system to prevent re-analyzing the same image twice.
