#!/usr/bin/env python3
"""
Batch process all PDF files and image folders in the joke_books directory.
"""

import os
import sys
from pathlib import Path
from extract_jokes import process_input

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    joke_books_dir = script_dir / "joke_books"
    
    if not joke_books_dir.exists():
        print(f"Error: joke_books directory not found at {joke_books_dir}")
        sys.exit(1)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Find all PDF files and directories
    pdf_files = sorted(joke_books_dir.glob("*.pdf"))
    directories = sorted([d for d in joke_books_dir.iterdir() if d.is_dir()])
    
    all_inputs = list(pdf_files) + directories
    
    if not all_inputs:
        print(f"No PDF files or directories found in {joke_books_dir}")
        sys.exit(0)
    
    print(f"Found {len(all_inputs)} items to process:")
    for item in all_inputs:
        print(f"  - {item.name}")
    
    print("\n" + "="*60)
    print("Starting batch processing...")
    print("="*60 + "\n")
    
    results = []
    for i, input_path in enumerate(all_inputs, 1):
        print(f"\n[{i}/{len(all_inputs)}]", "="*60)
        try:
            output_path = process_input(str(input_path), api_key)
            results.append(("✓", input_path.name, output_path))
        except Exception as e:
            print(f"✗ Error processing {input_path.name}: {e}")
            results.append(("✗", input_path.name, str(e)))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for status, name, result in results:
        print(f"{status} {name}")
        if status == "✓":
            print(f"   → {result}")
    
    successful = sum(1 for status, _, _ in results if status == "✓")
    print(f"\nCompleted: {successful}/{len(results)} successful")

if __name__ == "__main__":
    main()

