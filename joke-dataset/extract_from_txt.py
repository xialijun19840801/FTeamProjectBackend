#!/usr/bin/env python3
"""
Extract jokes from a text file containing Q&A jokes.
Filters out knock-knock jokes and adds Age Group and Scenario fields.
"""

import os
import json
import argparse
import ast
from pathlib import Path
from typing import List, Dict, Any

try:
    import openai
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    exit(1)


def load_jokes_from_txt(txt_path: str) -> List[Dict[str, str]]:
    """Load jokes from a text file. Handles both Python list format and plain text."""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Try to parse as Python literal (list of dicts)
    try:
        jokes = ast.literal_eval(content)
        if isinstance(jokes, list):
            return jokes
    except (ValueError, SyntaxError):
        pass
    
    # If that fails, treat as plain text and return empty list
    # (we'll need to extract from text using LLM)
    return []


def filter_knock_knock_jokes(jokes: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filter out knock-knock jokes."""
    filtered = []
    for joke in jokes:
        question = joke.get('Question', '').lower()
        answer = joke.get('Answer', '').lower()
        
        # Check if it's a knock-knock joke
        is_knock_knock = (
            'knock knock' in question or
            'knock-knock' in question or
            'who\'s there' in question or
            'who is there' in question or
            question.startswith('knock')
        )
        
        if not is_knock_knock:
            filtered.append(joke)
    
    return filtered


def add_metadata_to_jokes(jokes: List[Dict[str, str]], api_key: str, batch_size: int = 20) -> List[Dict[str, Any]]:
    """Add Age Group and Scenario fields to jokes using OpenAI API."""
    client = openai.OpenAI(api_key=api_key)
    
    enriched_jokes = []
    
    # Process in batches to avoid token limits
    for i in range(0, len(jokes), batch_size):
        batch = jokes[i:i + batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(jokes) + batch_size - 1)//batch_size} ({len(batch)} jokes)...")
        
        # Create prompt with all jokes in batch
        jokes_text = "\n".join([
            f"{idx + 1}. Q: {joke.get('Question', '')} A: {joke.get('Answer', '')}"
            for idx, joke in enumerate(batch)
        ])
        
        prompt = f"""For each of the following jokes, classify them with Age Group and Scenario.

Return a JSON object with a "jokes" field containing an array of objects. Each object must have four fields:
- "Question": the question part of the joke (keep exactly as provided)
- "Answer": the answer part of the joke (keep exactly as provided)
- "Age Group": one of "5-8", "8-12", or ">12". Choose based on whether kids in that age group can understand the joke and would not find it too simple or naive. Consider the complexity, vocabulary, and concepts used.
- "Scenario": a list containing one or more from ["school", "home", "party", "vacation"]. Choose scenarios where this joke would be appropriate and relevant.

Jokes to classify:
{jokes_text}

Return the jokes in the same order as provided, with the exact same Question and Answer text.
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that classifies jokes with age group and scenario tags. Always return a valid JSON object with a 'jokes' array field. Each joke must include Question, Answer, Age Group (one of: 5-8, 8-12, >12), and Scenario (list of one or more from: school, home, party, vacation). Preserve the exact Question and Answer text as provided."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            parsed = json.loads(content)
            
            # Extract jokes array
            if 'jokes' in parsed:
                batch_enriched = parsed['jokes']
                enriched_jokes.extend(batch_enriched)
            elif isinstance(parsed, list):
                enriched_jokes.extend(parsed)
            else:
                # Try to find any array value
                for value in parsed.values():
                    if isinstance(value, list):
                        enriched_jokes.extend(value)
                        break
            
        except json.JSONDecodeError as e:
            print(f"    Error parsing JSON response: {e}")
            print(f"    Response was: {content[:200]}...")
            # Fallback: add jokes without metadata
            for joke in batch:
                enriched_jokes.append({
                    "Question": joke.get('Question', ''),
                    "Answer": joke.get('Answer', ''),
                    "Age Group": "8-12",  # Default
                    "Scenario": ["home"]  # Default
                })
        except Exception as e:
            print(f"    Error calling OpenAI API: {e}")
            # Fallback: add jokes without metadata
            for joke in batch:
                enriched_jokes.append({
                    "Question": joke.get('Question', ''),
                    "Answer": joke.get('Answer', ''),
                    "Age Group": "8-12",  # Default
                    "Scenario": ["home"]  # Default
                })
    
    return enriched_jokes


def main():
    parser = argparse.ArgumentParser(
        description="Extract Q&A jokes from a text file, filter knock-knock jokes, and add Age Group and Scenario fields"
    )
    parser.add_argument(
        "input_txt",
        help="Input text file containing jokes"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY environment variable)",
        default=None
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path (default: same name as input with .json extension)",
        default=None
    )
    parser.add_argument(
        "--batch-size",
        help="Number of jokes to process per API call (default: 20)",
        type=int,
        default=20
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required.")
        print("Provide it via --api-key argument or OPENAI_API_KEY environment variable")
        exit(1)
    
    # Determine input and output paths
    input_path = Path(args.input_txt)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / (input_path.stem + ".json")
    
    print(f"Loading jokes from: {input_path}")
    
    # Load jokes
    jokes = load_jokes_from_txt(str(input_path))
    if not jokes:
        print("Error: Could not parse jokes from file. Expected a Python list of dictionaries.")
        exit(1)
    
    print(f"Loaded {len(jokes)} jokes")
    
    # Filter knock-knock jokes
    print("Filtering out knock-knock jokes...")
    filtered_jokes = filter_knock_knock_jokes(jokes)
    print(f"After filtering: {len(filtered_jokes)} jokes")
    
    if not filtered_jokes:
        print("No jokes remaining after filtering.")
        exit(0)
    
    # Add metadata
    print("Adding Age Group and Scenario fields...")
    enriched_jokes = add_metadata_to_jokes(filtered_jokes, api_key, args.batch_size)
    
    # Save to JSON
    print(f"Saving {len(enriched_jokes)} jokes to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_jokes, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully saved to: {output_path}")


if __name__ == "__main__":
    main()

