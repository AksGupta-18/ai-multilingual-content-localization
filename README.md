# AI-Powered Multilingual Content Localization Engine for Skill Courses

A Streamlit-based MVP for engineering educational content localization. The application extracts text from PDF, DOCX, PPTX, and TXT files, detects the source language, preprocesses the content, translates it into Hindi or Telugu using IndicTrans2, and displays the output for review.

## Project Structure

## Project Structure

```text
AI-Localization-Engine/
├── app.py
├── requirements.txt
├── README.md
├── modules/
│   ├── __init__.py
│   ├── extractor.py
│   ├── preprocess.py
│   ├── detector.py
│   ├── translator.py
│   └── localization.py
├── uploads/
└── outputs/
```


## Features

- Upload PDF, DOCX, PPTX, or TXT files
- Extract raw content from the chosen file type
- Preprocess text while preserving technical terms
- Detect the source language automatically
- Translate into Hindi or Telugu using a pretrained multilingual model
- Display original and translated content in the Streamlit UI

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download NLTK data (needed for sentence operations):
   ```python
   import nltk
   nltk.download("punkt")
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown by Streamlit in the browser.

## Authentication for Hugging Face

Before the first translation run, authenticate with Hugging Face from your local machine using the CLI or a local environment variable. Do not store the token in the project files.

Examples:

```bash
huggingface-cli login
```

or:

```bash
set HF_TOKEN=your_local_token
```

The app will read the token from the local Hugging Face configuration or environment, not from source code.

## Notes

- The app uses Hugging Face models for translation. The first run may take time to download the model weights.
- This project uses the English-to-Indic IndicTrans model `ai4bharat/indictrans2-en-indic-dist-200M` with `eng_Latn` as the source language and `hin_Deva` or `tel_Telu` as translation targets.
- For the initial version, the workflow is designed to work as a clean MVP: upload -> extract -> preprocess -> detect -> translate -> display.
- The system preserves important engineering terminology such as CPU, RAM, SQL, API, Python, Java, Database, Neural Network, and Machine Learning.

## Future Improvements

- Add document-level translation quality checks
- Support more regional languages
- Generate localized PDF/DOCX/PPTX outputs
- Add a lightweight backend and storage layer
