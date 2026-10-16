import re

TECHNICAL_TERMS = [
    "CPU", "RAM", "SQL", "API", "Python", "Java",
    "Database", "Neural Network", "Machine Learning",
    "Deep Learning", "IoT", "AI", "NLP", "GPU",
    "DBMS", "HTTP", "HTTPS", "JSON", "XML", "C++",
    "JavaScript", "HTML", "Operating System",
    "Compiler", "Algorithm", "Microcontroller",
    "Circuit", "Digital Signal Processing",
    "Control System", "Embedded System"
]


def remove_pdf_artifacts(text: str) -> str:
    if not text:
        return ""

    cleaned_lines = []
    seen_lines = set()

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove common extraction artifacts WITHOUT
        # deleting the entire line containing valid content.
        line = line.replace("_BAR_", " ")
        line = re.sub(r"\bDT[A-Z0-9_]{2,}\b", " ", line)
        line = re.sub(r"\b[A-Za-z]*\.kgm\b", " ", line)

        # Remove obvious standalone page numbers
        if re.fullmatch(r"\d{1,4}", line):
            continue

        # Remove repeated lines
        normalized = line.lower()

        if normalized in seen_lines:
            continue

        seen_lines.add(normalized)

        # Clean excessive whitespace
        line = re.sub(r"\s+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def normalize_whitespace(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\t", " ")

    # Multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Too many blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_sentences(text: str):
    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def protect_technical_terms(text: str):
    protected_terms = {}
    working_text = text

    for index, term in enumerate(
        sorted(TECHNICAL_TERMS, key=len, reverse=True)
    ):
        token = f"TECHTERM{index}X"

        protected_terms[token] = term

        working_text = re.sub(
            re.escape(term),
            token,
            working_text,
            flags=re.IGNORECASE
        )

    return working_text, protected_terms


def restore_technical_terms(text: str, protected_terms: dict):
    restored_text = text

    for token, term in protected_terms.items():
        restored_text = restored_text.replace(token, term)

    return restored_text


def preprocess_text(text: str):

    cleaned_text = remove_pdf_artifacts(text)

    cleaned_text = normalize_whitespace(cleaned_text)

    protected_text, protected_terms = protect_technical_terms(
        cleaned_text
    )

    sentences = split_into_sentences(protected_text)

    return {
        "text": protected_text,
        "sentences": sentences,
        "protected_terms": protected_terms,
    }