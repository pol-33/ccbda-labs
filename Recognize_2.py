import boto3
import json
import os
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Directory setup
IMAGES_JSON = Path('./imageScraper/images.json')
INSIGHTS_DIR = Path('./web_insights')
DOWNLOADED_IMAGES_DIR = Path('./downloaded_images')
INSIGHTS_DIR.mkdir(exist_ok=True)
DOWNLOADED_IMAGES_DIR.mkdir(exist_ok=True)

# Cache file to track analyzed images
CACHE_FILE = INSIGHTS_DIR / 'analyzed_web_images.json'

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


def get_url_hash(url):
    """Calculate MD5 hash of a URL to identify unique images"""
    return hashlib.md5(url.encode()).hexdigest()


def download_image(url, save_path):
    """Download an image from a URL"""
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"  ✗ Error downloading image: {e}")
        return False


def analyze_image_with_rekognition(image_bytes, rekognition_client):
    """Analyze an image with AWS Rekognition - detect labels"""
    try:
        # Detect labels in the image
        response = rekognition_client.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=10,
            MinConfidence=70
        )
        return response
    except Exception as e:
        print(f"  ✗ Error calling Rekognition: {e}")
        return None


def analyze_web_image(url, image_data, rekognition_client):
    """Analyze a single web image"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {url}")
    print(f"{'='*60}")
    
    # Generate a safe filename from URL
    url_hash = get_url_hash(url)
    parsed_url = urlparse(url)
    extension = Path(parsed_url.path).suffix or '.jpg'
    safe_filename = f"{url_hash}{extension}"
    save_path = DOWNLOADED_IMAGES_DIR / safe_filename
    
    # Download the image
    print("Downloading image...")
    if not download_image(url, save_path):
        return None
    
    # Read the downloaded image
    with open(save_path, 'rb') as f:
        image_bytes = f.read()
    
    # Analyze with Rekognition
    print("Analyzing with Rekognition...")
    result = analyze_image_with_rekognition(image_bytes, rekognition_client)
    
    if result:
        # Save results
        result_file = INSIGHTS_DIR / f"{url_hash}_web_labels.json"
        result['source_url'] = url
        result['appears_on'] = image_data.get('appears_url', 'unknown')
        result['depth'] = image_data.get('depth', 0)
        
        with open(result_file, 'w') as f:
            json.dump(result, indent=4, fp=f)
        
        print(f"✓ Analysis complete! Results saved to: {result_file}")
        
        # Show top labels
        labels = result.get('Labels', [])
        if labels:
            print(f"\nDetected {len(labels)} labels:")
            for label in labels[:5]:  # Show top 5
                print(f"  - {label['Name']}: {label['Confidence']:.2f}% confidence")
        
        return result
    
    return None


def load_scraped_images():
    """Load the scraped images from images.json"""
    if not IMAGES_JSON.exists():
        print(f"Error: {IMAGES_JSON} not found!")
        return []
    
    # Read the file content
    with open(IMAGES_JSON, 'r') as f:
        content = f.read()
    
    # Handle malformed JSON (multiple arrays concatenated)
    data = []
    
    # Try to parse as a single array first
    try:
        parsed = json.loads(content)
        if isinstance(parsed, list):
            data = parsed
    except json.JSONDecodeError:
        # If that fails, extract all JSON objects manually
        print("Warning: Malformed JSON detected. Attempting to fix...")
        
        # Find all JSON objects in the file (lines with "img_url")
        import re
        # Match lines that look like JSON objects
        pattern = r'\{[^}]*"img_url"[^}]*\}'
        matches = re.findall(pattern, content)
        
        for match in matches:
            try:
                obj = json.loads(match)
                data.append(obj)
            except json.JSONDecodeError:
                continue
    
    if not data:
        print("Error: No valid image data found in images.json")
        return []
    
    # Filter out duplicates by URL
    unique_images = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        url = item.get('img_url')
        if url and url not in unique_images:
            unique_images[url] = item
    
    return list(unique_images.values())


def generate_insights(cache):
    """Generate insights from all analyzed images"""
    print(f"\n{'='*60}")
    print("GENERATING INSIGHTS FROM WEB IMAGES")
    print(f"{'='*60}")
    
    # Collect all labels from all analyzed images
    all_labels = {}
    page_labels = {}  # Labels per page
    
    # Read all result files
    for url_hash, cache_entry in cache.items():
        result_file = INSIGHTS_DIR / f"{url_hash}_web_labels.json"
        if not result_file.exists():
            continue
        
        with open(result_file, 'r') as f:
            result = json.load(f)
        
        page_url = result.get('appears_on', 'unknown')
        
        # Initialize page entry
        if page_url not in page_labels:
            page_labels[page_url] = []
        
        # Collect labels
        for label in result.get('Labels', []):
            label_name = label['Name']
            confidence = label['Confidence']
            
            # Track global label frequency
            if label_name not in all_labels:
                all_labels[label_name] = []
            all_labels[label_name].append(confidence)
            
            # Track labels per page
            page_labels[page_url].append(label_name)
    
    if not all_labels:
        print("No analysis results found to generate insights.")
        return
    
    # Calculate insights
    print(f"\nTotal images analyzed: {len(cache)}")
    print(f"Total unique labels detected: {len(all_labels)}")
    print(f"Pages analyzed: {len(page_labels)}")
    
    # Top 10 most common labels across all images
    label_counts = {label: len(occurrences) for label, occurrences in all_labels.items()}
    top_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n{'─'*60}")
    print("TOP 10 MOST DETECTED LABELS ACROSS ALL WEB IMAGES:")
    print(f"{'─'*60}")
    for label, count in top_labels:
        avg_confidence = sum(all_labels[label]) / len(all_labels[label])
        print(f"  {label:.<40} {count} times (avg {avg_confidence:.1f}% confidence)")
    
    # Insights by page type
    print(f"\n{'─'*60}")
    print("INSIGHTS BY WEB PAGE:")
    print(f"{'─'*60}")
    for page_url, labels in list(page_labels.items())[:5]:  # Show first 5 pages
        unique_labels = set(labels)
        print(f"\nPage: {page_url}")
        print(f"  Images on this page: {len(labels)}")
        print(f"  Unique labels: {len(unique_labels)}")
        print(f"  Most common: {', '.join(list(unique_labels)[:5])}")
    
    # Save insights to file
    insights_summary = {
        'total_images_analyzed': len(cache),
        'total_unique_labels': len(all_labels),
        'pages_analyzed': len(page_labels),
        'top_labels': [{'label': label, 'occurrences': count, 
                       'avg_confidence': sum(all_labels[label]) / len(all_labels[label])}
                      for label, count in top_labels],
        'pages': {url: {'image_count': len(labels), 
                       'unique_labels': len(set(labels)),
                       'top_labels': list(set(labels))[:10]}
                 for url, labels in page_labels.items()}
    }
    
    insights_file = INSIGHTS_DIR / 'web_insights_summary.json'
    with open(insights_file, 'w') as f:
        json.dump(insights_summary, indent=4, fp=f)
    
    print(f"\n{'─'*60}")
    print(f"📊 Insights summary saved to: {insights_file}")
    print(f"{'─'*60}")


def main():
    print("="*60)
    print("AWS Rekognition Web Image Analysis")
    print("="*60)
    
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
    
    # Load scraped images
    print("\nLoading scraped images from images.json...")
    scraped_images = load_scraped_images()
    
    if not scraped_images:
        print("No images found in images.json")
        return
    
    print(f"Found {len(scraped_images)} unique image URLs")
    
    # Ask user how many to analyze
    try:
        max_images = int(input(f"\nHow many images would you like to analyze? (max {len(scraped_images)}): "))
        max_images = min(max_images, len(scraped_images))
    except ValueError:
        max_images = 5  # Default to 5
        print(f"Invalid input. Analyzing first {max_images} images...")
    
    # Process images
    analyzed_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, image_data in enumerate(scraped_images[:max_images]):
        url = image_data.get('img_url')
        if not url:
            continue
        
        # Calculate URL hash
        url_hash = get_url_hash(url)
        
        # Check if already analyzed
        if url_hash in cache:
            print(f"\n⊘ Skipping {url} (already analyzed)")
            skipped_count += 1
            continue
        
        # Analyze the image
        result = analyze_web_image(url, image_data, rekognition)
        
        if result:
            # Add to cache
            cache[url_hash] = {
                'url': url,
                'appears_on': image_data.get('appears_url', 'unknown'),
                'depth': image_data.get('depth', 0),
                'analyzed': True
            }
            analyzed_count += 1
        else:
            error_count += 1
    
    # Save updated cache
    save_cache(cache)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total unique URLs: {len(scraped_images)}")
    print(f"Newly analyzed: {analyzed_count}")
    print(f"Skipped (already analyzed): {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"\nResults saved in: {INSIGHTS_DIR}/")
    print(f"Downloaded images in: {DOWNLOADED_IMAGES_DIR}/")
    
    # Generate insights if we analyzed any images
    if analyzed_count > 0 or len(cache) > 0:
        generate_insights(cache)


if __name__ == '__main__':
    main()
