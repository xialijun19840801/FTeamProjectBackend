#!/usr/bin/env python3
"""
Joke Extraction Tool

Extracts Q&A format jokes from PDF files or folders containing images.
Uses OpenAI API to intelligently extract jokes and outputs JSON files.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import base64
from io import BytesIO

try:
    import openai
    from PIL import Image
    import PyPDF2
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    exit(1)


def encode_image(image_path: str) -> str:
    """Encode image to base64 string for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file."""
    text_content = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
    except Exception as e:
        print(f"Warning: Text extraction from PDF failed: {e}")
        print("Attempting image-based extraction...")
        return None
    
    return "\n\n".join(text_content) if text_content else None


def pdf_to_images(pdf_path: str) -> List[Image.Image]:
    """Convert PDF pages to images."""
    try:
        images = convert_from_path(pdf_path)
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        print("Please ensure poppler is installed (brew install poppler on macOS)")
        return []


def extract_jokes_from_text(text: str, api_key: str) -> List[Dict[str, str]]:
    """Use OpenAI API to extract Q&A jokes from text."""
    client = openai.OpenAI(api_key=api_key)
    
    prompt = """Extract all jokes that are in question and answer format from the following text. 
For each joke, identify the question and the answer.

Return the results as a JSON object with a "jokes" field containing an array of objects, where each object has two fields:
- "Question": the question part of the joke
- "Answer": the answer part of the joke

Only include jokes that are clearly in Q&A format. Skip any other content.
If there are no Q&A jokes, return {"jokes": []}.

Example format:
{"jokes": [
  {"Question": "Why did the chicken cross the road?", "Answer": "To get to the other side!"},
  {"Question": "What do you call a fake noodle?", "Answer": "An impasta!"}
]}

Text to analyze:
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts jokes in question-answer format. Always return a valid JSON object with a 'jokes' array field."
                },
                {
                    "role": "user",
                    "content": prompt + text
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        
        # Extract jokes array
        if 'jokes' in parsed:
            return parsed['jokes']
        elif isinstance(parsed, list):
            return parsed
        else:
            # Try to find any array value
            for value in parsed.values():
                if isinstance(value, list):
                    return value
            return []
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response was: {content[:200]}...")
        return []
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []


def extract_jokes_from_image(image_path: str, api_key: str) -> List[Dict[str, str]]:
    """Use OpenAI Vision API to extract Q&A jokes from an image."""
    client = openai.OpenAI(api_key=api_key)
    
    base64_image = encode_image(image_path)
    
    prompt = """Extract all jokes that are in question and answer format from this image. 
For each joke, identify the question and the answer.

Return the results as a JSON object with a "jokes" field containing an array of objects, where each object has two fields:
- "Question": the question part of the joke
- "Answer": the answer part of the joke

Only include jokes that are clearly in Q&A format. Skip any other content.
If there are no Q&A jokes, return {"jokes": []}.

Example format:
{"jokes": [
  {"Question": "Why did the chicken cross the road?", "Answer": "To get to the other side!"},
  {"Question": "What do you call a fake noodle?", "Answer": "An impasta!"}
]}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts jokes in question-answer format from images. Always return valid JSON only."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        
        # Extract jokes array
        if 'jokes' in parsed:
            return parsed['jokes']
        elif isinstance(parsed, list):
            return parsed
        else:
            # Try to find any array value
            for value in parsed.values():
                if isinstance(value, list):
                    return value
            return []
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response was: {content[:200]}...")
        return []
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []


def extract_jokes_from_pdf(pdf_path: str, api_key: str) -> List[Dict[str, str]]:
    """Extract jokes from a PDF file (tries text first, then images)."""
    all_jokes = []
    
    # Try text extraction first
    text = extract_text_from_pdf(pdf_path)
    if text and len(text.strip()) > 50:  # Only use if we got substantial text
        print(f"  Extracting from PDF text...")
        jokes = extract_jokes_from_text(text, api_key)
        if jokes:
            all_jokes.extend(jokes)
            print(f"  Found {len(jokes)} jokes from text extraction")
    
    # If text extraction failed or didn't yield results, try image-based extraction
    if not all_jokes:
        print(f"  Converting PDF to images...")
        images = pdf_to_images(pdf_path)
        if images:
            print(f"  Processing {len(images)} pages as images...")
            for i, image in enumerate(images, 1):
                print(f"  Processing page {i}/{len(images)}...")
                # Save temporary image
                temp_path = f"/tmp/temp_pdf_page_{i}.png"
                image.save(temp_path, "PNG")
                
                jokes = extract_jokes_from_image(temp_path, api_key)
                if jokes:
                    all_jokes.extend(jokes)
                    print(f"    Found {len(jokes)} jokes on page {i}")
                
                # Clean up
                os.remove(temp_path)
    
    return all_jokes


def extract_jokes_from_image_folder(folder_path: str, api_key: str) -> List[Dict[str, str]]:
    """Extract jokes from a folder containing images."""
    all_jokes = []
    
    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    
    # Get all image files, sorted
    image_files = sorted([
        f for f in os.listdir(folder_path)
        if Path(f).suffix.lower() in image_extensions
    ])
    
    if not image_files:
        print(f"  No image files found in {folder_path}")
        return []
    
    print(f"  Found {len(image_files)} image files")
    
    for i, image_file in enumerate(image_files, 1):
        image_path = os.path.join(folder_path, image_file)
        print(f"  Processing {image_file} ({i}/{len(image_files)})...")
        
        jokes = extract_jokes_from_image(image_path, api_key)
        if jokes:
            all_jokes.extend(jokes)
            print(f"    Found {len(jokes)} jokes")
    
    return all_jokes


def process_input(input_path: str, api_key: str, output_dir: str = None) -> str:
    """Process a single input (PDF file or image folder) and save JSON output."""
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    
    # Determine output filename
    if input_path.is_file():
        output_filename = input_path.stem + ".json"
        input_type = "PDF file"
    else:
        output_filename = input_path.name + ".json"
        input_type = "image folder"
    
    # Determine output directory
    if output_dir:
        output_path = Path(output_dir) / output_filename
    else:
        output_path = input_path.parent / output_filename
    
    print(f"\nProcessing {input_type}: {input_path.name}")
    
    # Extract jokes
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        jokes = extract_jokes_from_pdf(str(input_path), api_key)
    elif input_path.is_dir():
        jokes = extract_jokes_from_image_folder(str(input_path), api_key)
    else:
        raise ValueError(f"Unsupported input type: {input_path}")
    
    # Save to JSON
    output_data = jokes
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved {len(jokes)} jokes to {output_path}")
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Extract Q&A format jokes from PDF files or image folders using OpenAI API"
    )
    parser.add_argument(
        "input",
        help="Input PDF file or folder containing images"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)",
        default=None
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for JSON files (default: same as input)",
        default=None
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required.")
        print("Provide it via --api-key argument or OPENAI_API_KEY environment variable")
        exit(1)
    
    # Process input
    try:
        output_path = process_input(args.input, api_key, args.output_dir)
        print(f"\n✓ Successfully extracted jokes to: {output_path}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

