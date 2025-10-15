import boto3
import json
import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directory setup
IMAGES_DIR = Path('./images')
RESULTS_DIR = Path('./rekognition_results')
RESULTS_DIR.mkdir(exist_ok=True)

# Cache file to track analyzed images
CACHE_FILE = RESULTS_DIR / 'analyzed_images.json'


def load_cache():
    """Load the cache of already analyzed images"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Save the cache of analyzed images"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, indent=4, fp=f)


def get_file_hash(filepath):
    """Calculate MD5 hash of a file to detect duplicates"""
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def analyze_image(image_path, rekognition_client):
    """Analyze a single image with AWS Rekognition"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {image_path.name}")
    print(f"{'='*60}")
    
    # Read image
    with open(image_path, 'rb') as fd:
        image_bytes = fd.read()
    
    # Call Rekognition API
    try:
        labels_list = rekognition_client.detect_labels(
            Image={'Bytes': image_bytes}, 
            MaxLabels=10, 
            MinConfidence=70
        )
        
        # Save results
        result_file = RESULTS_DIR / f"{image_path.stem}_labels.json"
        with open(result_file, 'w') as f:
            json.dump(labels_list, indent=4, fp=f)
        
        print(f"✓ Analysis complete! Results saved to: {result_file}")
        print(f"\nDetected {len(labels_list.get('Labels', []))} labels:")
        for label in labels_list.get('Labels', [])[:5]:  # Show top 5
            print(f"  - {label['Name']}: {label['Confidence']:.2f}% confidence")
        
        return labels_list
    
    except Exception as e:
        print(f"✗ Error analyzing image: {e}")
        return None


def main():
    # Initialize Rekognition client
    rekognition = boto3.client(
        'rekognition',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN')
    )
    
    # Load cache of analyzed images
    cache = load_cache()
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png'}
    image_files = [f for f in IMAGES_DIR.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not image_files:
        print("No images found in ./images/ directory")
        return
    
    print(f"Found {len(image_files)} image(s) to process")
    
    # Process each image
    analyzed_count = 0
    skipped_count = 0
    
    for image_path in image_files:
        # Calculate file hash to prevent duplicate analysis
        file_hash = get_file_hash(image_path)
        
        # Check if already analyzed
        if file_hash in cache:
            print(f"\n⊘ Skipping {image_path.name} (already analyzed)")
            skipped_count += 1
            continue
        
        # Analyze the image
        result = analyze_image(image_path, rekognition)
        
        if result:
            # Add to cache
            cache[file_hash] = {
                'filename': image_path.name,
                'analyzed_at': str(Path(RESULTS_DIR / f"{image_path.stem}_labels.json").stat().st_mtime)
            }
            analyzed_count += 1
    
    # Save updated cache
    save_cache(cache)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total images found: {len(image_files)}")
    print(f"Newly analyzed: {analyzed_count}")
    print(f"Skipped (already analyzed): {skipped_count}")
    print(f"\nResults saved in: {RESULTS_DIR}/")


if __name__ == '__main__':
    main()