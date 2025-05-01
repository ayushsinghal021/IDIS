import logging
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
import spacy
import fitz  # PyMuPDF

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except Exception:
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error("spaCy model loading failed.")
        nlp = None

# Tech keywords that shouldn't appear as PERSON or ORG
TECH_TERMS = {
    "python", "django", "docker", "html", "css", "sql", "pytorch", "nltk", "bert",
    "scikit", "yolo", "qiskit", "tensorflow", "keras", "flask", "mongodb", "pandas",
    "numpy", "matplotlib", "c++", "reactjs", "js", "java"
}

class EntityExtractor:
    def __init__(self, custom_patterns_path: Optional[Path] = None):
        if nlp is None:
            raise RuntimeError("spaCy model not available. Please install one.")
        self.custom_patterns = {}
        if custom_patterns_path and Path(custom_patterns_path).exists():
            with open(custom_patterns_path, 'r') as f:
                self.custom_patterns = json.load(f)

    def extract_from_pdf(self, pdf_path: Path) -> Dict[str, List[str]]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        text = self._extract_text_from_pdf(pdf_path)
        return self.extract_entities(text)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        text = self._clean_text(text)
        doc = nlp(text)
        entities = {}

        # Extract from spaCy
        for ent in doc.ents:
            label = ent.label_
            value = ent.text.strip()
            if value.lower() in TECH_TERMS:
                continue
            if label not in entities:
                entities[label] = []
            if value not in entities[label]:
                entities[label].append(value)

        # Extract from regex
        custom_entities = self._extract_custom_entities(text)
        for label, values in custom_entities.items():
            if label not in entities:
                entities[label] = []
            for value in values:
                if value not in entities[label]:
                    entities[label].append(value)

        return self._post_process_entities(entities)

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[•\u2022]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _extract_custom_entities(self, text: str) -> Dict[str, List[str]]:
        patterns = {
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            "PHONE": r'(\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}',
            "URL": r'https?://[^\s]+',
            "DATE": r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-]?\d{4}\b|\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
            "PERCENT": r'\b\d{1,3}%\b',
            "PROGRAMMING_LANGUAGE": r'\b(Python|Java|Django|Docker|HTML|CSS|SQL|PyTorch|NLTK|BERT|Scikit|YOLO|Keras|Flask|ReactJS|C\+\+|TensorFlow)\b'
        }

        patterns.update(self.custom_patterns)

        results = {}
        for label, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                clean_matches = list(set([m.strip() for m in matches if m.strip()]))
                results[label] = clean_matches

        return results

    def _post_process_entities(self, entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
        for label in ("PERSON", "ORG"):
            if label in entities:
                entities[label] = [
                    e for e in entities[label]
                    if e.lower() not in TECH_TERMS and not re.match(r'^[\d\W]+$', e) and len(e.split()) <= 6
                ]

        # Remove phone-like entries from DATE
        if "DATE" in entities:
            entities["DATE"] = [d for d in entities["DATE"] if not re.search(r'\+?\d{5,}', d)]

        # Normalize language names
        if "PROGRAMMING_LANGUAGE" in entities:
            entities["PROGRAMMING_LANGUAGE"] = sorted(set([pl.title() for pl in entities["PROGRAMMING_LANGUAGE"]]))

        # Clean up
        return {k: sorted(set(v)) for k, v in entities.items()}