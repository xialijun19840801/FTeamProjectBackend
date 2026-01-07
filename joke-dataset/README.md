# Joke Extraction Tool

This tool extracts jokes in question-and-answer format from PDF files or folders containing images using OpenAI's API.

## Features

- **PDF Processing**: Extracts jokes from PDF files (text-based or image-based)
- **Image Folder Processing**: Processes folders containing joke book images
- **Q&A Format Detection**: Uses GPT-4 to intelligently extract only question-and-answer format jokes
- **JSON Output**: Saves extracted jokes as JSON files with the same name as the input

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install system dependencies for PDF processing (macOS):
```bash
brew install poppler
```

For other systems, install poppler using your package manager.

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or provide it via the `--api-key` argument when running the script.

## Usage

### Process a PDF file:
```bash
python extract_jokes.py joke_books/100-KIDS-JOKES.pdf
```

### Process an image folder:
```bash
python extract_jokes.py joke_books/LOTS_OF_JOKES_FOR_KIDS/
```

### Specify output directory:
```bash
python extract_jokes.py joke_books/100-KIDS-JOKES.pdf --output-dir ./output
```

### Provide API key via command line:
```bash
python extract_jokes.py joke_books/100-KIDS-JOKES.pdf --api-key "your-api-key"
```

### Batch process all files in joke_books directory:
```bash
export OPENAI_API_KEY="your-api-key-here"
python process_all.py
```

This will process all PDF files and image folders in the `joke_books` directory and generate JSON files for each.

## Output Format

The tool generates JSON files with the following structure:

```json
[
  {
    "Question": "Why did the chicken cross the road?",
    "Answer": "To get to the other side!",
    "Age Group": "5-8",
    "Scenario": ["home", "party"]
  },
  {
    "Question": "What do you call a fake noodle?",
    "Answer": "An impasta!",
    "Age Group": "8-12",
    "Scenario": ["school", "home"]
  }
]
```

Each joke object contains:
- **Question**: The question part of the joke
- **Answer**: The answer/punchline of the joke
- **Age Group**: One of `"5-8"`, `"8-12"`, or `">12"` - classified based on whether kids in that age group can understand the joke and would not find it too simple or naive
- **Scenario**: A list containing one or more from `["school", "home", "party", "vacation"]` - scenarios where the joke would be appropriate and relevant

The output file name matches the input:
- For PDF files: `filename.json`
- For folders: `foldername.json`

## How It Works

1. **PDF Files**: 
   - First attempts to extract text directly from the PDF
   - If text extraction fails or yields poor results, converts PDF pages to images and processes them with GPT-4 Vision

2. **Image Folders**:
   - Processes each image file in the folder sequentially
   - Uses GPT-4 Vision to extract jokes from images

3. **Joke Extraction**:
   - Uses OpenAI's GPT-4/GPT-4o models to identify and extract Q&A format jokes
   - Filters out non-Q&A content
   - Returns structured JSON with Question and Answer fields

## Requirements

- Python 3.7+
- OpenAI API key
- poppler (for PDF to image conversion)
- See `requirements.txt` for Python package dependencies

