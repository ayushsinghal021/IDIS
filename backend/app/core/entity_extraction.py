import logging
import re
from typing import List, Dict, Any, Set, Optional
import spacy
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to load spaCy model, or use a lightweight model as fallback
try:
    nlp = spacy.load("en_core_web_md")
except Exception as e:
    logger.warning(f"Failed to load full spaCy model, trying lightweight model: {e}")
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception as e2:
        logger.error(f"Failed to load spaCy model: {e2}")
        nlp = None


class EntityExtractor:
    """Extracts structured entities from document text"""
    
    def __init__(self, custom_patterns_path: Optional[Path] = None):
        """
        Initialize entity extractor
        
        Args:
            custom_patterns_path: Path to JSON file with custom entity patterns
        """
        if nlp is None:
            raise RuntimeError("spaCy model not available. Install with 'python -m spacy download en_core_web_md'")
            
        self.custom_patterns = {}
        if custom_patterns_path and Path(custom_patterns_path).exists():
            try:
                with open(custom_patterns_path, 'r') as f:
                    self.custom_patterns = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load custom patterns: {e}")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of entity types and values
        """
        doc = nlp(text)
        
        # Extract spaCy named entities
        entities = {}
        for ent in doc.ents:
            entity_type = ent.label_
            entity_text = ent.text.strip()
            
            if entity_type not in entities:
                entities[entity_type] = []
                
            # Avoid duplicates
            if entity_text not in entities[entity_type]:
                entities[entity_type].append(entity_text)
        
        # Add custom extraction with regex patterns
        custom_entities = self._extract_custom_entities(text)
        for entity_type, values in custom_entities.items():
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].extend([v for v in values if v not in entities.get(entity_type, [])])
        
        return entities
    
    def _extract_custom_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using custom regex patterns"""
        results = {}
        
        # Extract common entities with regex
        # Example patterns
        patterns = {
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "PHONE": r'\b(\+\d{1,2}\s?)?(\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "URL": r'https?://[^\s]+',
            "SSN": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
            "CREDIT_CARD": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "DATE": r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
            "INVOICE_NUMBER": r'\b(?:INV|INVOICE)[-\s]?\d{5,10}\b',
            "AMOUNT": r'\$\s?[\d,]+(?:\.\d{2})?',
        }
        
        # Add custom patterns
        patterns.update(self.custom_patterns)
        
        # Apply patterns
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                results[entity_type] = [match for match in matches]
        
        return results
    
    def extract_table_data(self, text: str) -> List[Dict[str, Any]]:
        """
        Attempt to extract tabular data from text
        
        Args:
            text: Text potentially containing tabular data
            
        Returns:
            List of dictionaries representing table rows
        """
        # Simple heuristic: look for patterns that might indicate table rows
        lines = text.split('\n')
        potential_headers = []
        rows = []
        
        # Try to identify header line (e.g., line with multiple capitalized words)
        for i, line in enumerate(lines[:10]):  # Check first 10 lines for headers
            words = line.split()
            if len(words) >= 3 and sum(1 for w in words if w and w[0].isupper()) >= 3:
                potential_headers = [w.strip() for w in re.split(r'\s{2,}', line) if w.strip()]
                if len(potential_headers) >= 3:
                    break
        
        if not potential_headers:
            return []
            
        # Try to extract rows based on similar structure as headers
        for line in lines[i+1:]:
            if not line.strip():
                continue
                
            cells = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
            if len(cells) == len(potential_headers):
                row = dict(zip(potential_headers, cells))
                rows.append(row)
                
        return rows