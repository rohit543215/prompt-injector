import re
import json
import spacy
from typing import List, Dict, Tuple
import random
from faker import Faker
import hashlib
from dataclasses import dataclass

@dataclass
class PIIEntity:
    """Represents a detected PII entity"""
    text: str
    pii_type: str
    start_pos: int
    end_pos: int
    confidence: float
    mask_id: str

class SimplePIIMasker:
    """Simple PII masking and unmasking functionality"""
    
    def __init__(self):
        self.mask_store: Dict[str, PIIEntity] = {}
        
        # Mask templates for different PII types
        self.mask_templates = {
            'PERSON': '[PERSON_{}]',
            'EMAIL': '[EMAIL_{}]', 
            'PHONE': '[PHONE_{}]',
            'SSN': '[SSN_{}]',
            'CREDIT_CARD': '[CARD_{}]',
            'ADDRESS': '[ADDRESS_{}]',
            'DATE': '[DATE_{}]',
            'ORGANIZATION': '[ORG_{}]',
            'LOCATION': '[LOCATION_{}]',
            'IP_ADDRESS': '[IP_{}]',
            'URL': '[URL_{}]',
            'BANK_ACCOUNT': '[ACCOUNT_{}]'
        }
    
    def generate_mask_id(self, text: str, pii_type: str) -> str:
        """Generate a unique mask ID for a PII entity"""
        content = f"{text}_{pii_type}_{len(self.mask_store)}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:8]
    
    def mask_text(self, text: str, entities: List[Tuple[str, str, float]]) -> Tuple[str, Dict[str, PIIEntity]]:
        """Mask PII entities in text"""
        masked_text = text
        current_masks = {}
        
        # Sort entities by their position in text (reverse order for replacement)
        entity_positions = []
        for entity_text, pii_type, confidence in entities:
            start = 0
            while True:
                pos = masked_text.find(entity_text, start)
                if pos == -1:
                    break
                entity_positions.append((pos, pos + len(entity_text), entity_text, pii_type, confidence))
                start = pos + 1
        
        # Sort by position (reverse order for safe replacement)
        entity_positions.sort(key=lambda x: x[0], reverse=True)
        
        # Replace entities with masks
        for start_pos, end_pos, entity_text, pii_type, confidence in entity_positions:
            mask_id = self.generate_mask_id(entity_text, pii_type)
            mask_template = self.mask_templates.get(pii_type, '[PII_{}]')
            mask_token = mask_template.format(mask_id)
            
            pii_entity = PIIEntity(
                text=entity_text,
                pii_type=pii_type,
                start_pos=start_pos,
                end_pos=end_pos,
                confidence=confidence,
                mask_id=mask_id
            )
            
            current_masks[mask_token] = pii_entity
            self.mask_store[mask_token] = pii_entity
            
            masked_text = masked_text[:start_pos] + mask_token + masked_text[end_pos:]
        
        return masked_text, current_masks
    
    def unmask_text(self, masked_text: str, mask_mapping: Dict[str, PIIEntity] = None) -> str:
        """Unmask PII entities in text"""
        unmasked_text = masked_text
        mappings = mask_mapping if mask_mapping else self.mask_store
        
        for mask_token, pii_entity in mappings.items():
            unmasked_text = unmasked_text.replace(mask_token, pii_entity.text)
        
        return unmasked_text
    
    def get_mask_info(self, masked_text: str) -> List[Dict]:
        """Get information about masks in the text"""
        mask_info = []
        mask_pattern = r'\[(\w+)_([a-f0-9]{8})\]'
        matches = re.finditer(mask_pattern, masked_text)
        
        for match in matches:
            mask_token = match.group(0)
            if mask_token in self.mask_store:
                entity = self.mask_store[mask_token]
                mask_info.append({
                    'mask_token': mask_token,
                    'pii_type': entity.pii_type,
                    'original_text': entity.text,
                    'confidence': entity.confidence,
                    'position': match.span()
                })
        
        return mask_info

class SimplePIIDetector:
    """Simple rule-based PII detector for demo purposes"""
    
    def __init__(self):
        self.fake = Faker()
        
        # PII patterns
        self.patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'CREDIT_CARD': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'IP_ADDRESS': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'URL': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
            'DATE': r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}-\d{1,2}-\d{4}\b'
        }
        
        # Try to load spaCy model for person/organization detection
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.use_spacy = True
        except OSError:
            print("spaCy model not found. Using pattern-based detection only.")
            self.use_spacy = False
    
    def detect_pii(self, text: str) -> List[Tuple[str, str, float]]:
        """Detect PII entities in text"""
        entities = []
        
        # Pattern-based detection
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group(), pii_type, 0.9))
        
        # spaCy-based detection for persons and organizations
        if self.use_spacy:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    entities.append((ent.text, "PERSON", 0.85))
                elif ent.label_ == "ORG":
                    entities.append((ent.text, "ORGANIZATION", 0.85))
                elif ent.label_ == "GPE":  # Geopolitical entity
                    entities.append((ent.text, "LOCATION", 0.8))
        
        # Remove duplicates and sort by position
        unique_entities = []
        seen = set()
        for entity in entities:
            if entity[0] not in seen:
                unique_entities.append(entity)
                seen.add(entity[0])
        
        return unique_entities
    
    def predict(self, text: str) -> List[Tuple[str, str, float]]:
        """Alias for detect_pii for compatibility"""
        return self.detect_pii(text)

class SimplePIIProcessor:
    """Simplified PII processor using rule-based detection"""
    
    def __init__(self):
        self.detector = SimplePIIDetector()
        self.masker = SimplePIIMasker()
    
    def process_for_chatbot(self, text: str) -> Tuple[str, Dict]:
        """Process text before sending to chatbot"""
        entities = self.detector.predict(text)
        masked_text, mask_mapping = self.masker.mask_text(text, entities)
        
        session_data = {
            'original_text': text,
            'masked_text': masked_text,
            'mask_mapping': {k: {
                'text': v.text,
                'pii_type': v.pii_type,
                'confidence': v.confidence
            } for k, v in mask_mapping.items()},
            'detected_entities': entities
        }
        
        return masked_text, session_data
    
    def process_chatbot_response(self, response_text: str, session_data: Dict) -> str:
        """Process chatbot response"""
        mask_mapping = {}
        for mask_token, entity_data in session_data['mask_mapping'].items():
            entity = PIIEntity(
                text=entity_data['text'],
                pii_type=entity_data['pii_type'],
                start_pos=0,
                end_pos=0,
                confidence=entity_data['confidence'],
                mask_id=mask_token.split('_')[-1].rstrip(']')
            )
            mask_mapping[mask_token] = entity
        
        return self.masker.unmask_text(response_text, mask_mapping)
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text and return detailed PII information"""
        entities = self.detector.predict(text)
        masked_text, mask_mapping = self.masker.mask_text(text, entities)
        
        return {
            'original_text': text,
            'masked_text': masked_text,
            'detected_entities': [
                {
                    'text': entity[0],
                    'type': entity[1], 
                    'confidence': entity[2]
                } for entity in entities
            ],
            'mask_info': self.masker.get_mask_info(masked_text),
            'pii_count': len(entities),
            'pii_types': list(set([entity[1] for entity in entities]))
        }

if __name__ == "__main__":
    # Test the simple PII detector
    processor = SimplePIIProcessor()
    
    test_text = """
    Hello John Smith, 
    
    Please contact me at john.smith@email.com or call 555-123-4567.
    My SSN is 123-45-6789 and my credit card number is 4532-1234-5678-9012.
    I work at TechCorp Inc and live in New York.
    Visit our website at https://example.com or connect to 192.168.1.1.
    
    Best regards,
    Jane Doe
    """
    
    print("Testing Simple PII Detection System")
    print("=" * 40)
    
    # Analyze the text
    analysis = processor.analyze_text(test_text)
    
    print(f"Original text:\n{test_text}")
    print(f"\nMasked text:\n{analysis['masked_text']}")
    
    print(f"\nDetected {analysis['pii_count']} PII entities:")
    for entity in analysis['detected_entities']:
        print(f"  • {entity['text']} → {entity['type']} ({entity['confidence']:.2f})")
    
    print(f"\nPII types found: {', '.join(analysis['pii_types'])}")