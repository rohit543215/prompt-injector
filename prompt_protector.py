import re
import random
from typing import Dict, List, Tuple
from faker import Faker
from simple_pii_model import SimplePIIProcessor

class PromptProtector:
    """Generate privacy-protected versions of prompts while maintaining intent"""
    
    def __init__(self):
        self.pii_processor = SimplePIIProcessor()
        self.fake = Faker()
        
        # Generic replacements that maintain context
        self.generic_replacements = {
            'PERSON': ['Alex Johnson', 'Sam Wilson', 'Jordan Smith', 'Taylor Brown', 'Casey Davis'],
            'EMAIL': ['user@example.com', 'contact@company.com', 'info@business.org', 'hello@service.net'],
            'PHONE': ['555-0123', '555-0456', '555-0789', '555-0321'],
            'ORGANIZATION': ['TechCorp Inc', 'Global Solutions LLC', 'Innovation Partners', 'Digital Services Co'],
            'LOCATION': ['Springfield', 'Riverside', 'Madison', 'Franklin', 'Georgetown'],
            'ADDRESS': ['123 Main Street, Anytown, ST 12345', '456 Oak Avenue, Somewhere, ST 67890'],
            'SSN': ['XXX-XX-1234', 'XXX-XX-5678'],
            'CREDIT_CARD': ['XXXX-XXXX-XXXX-1234', 'XXXX-XXXX-XXXX-5678'],
            'BANK_ACCOUNT': ['XXXX-XXXX-XXXX-1234', 'XXXX-XXXX-XXXX-5678'],
            'IP_ADDRESS': ['192.168.1.100', '10.0.0.50'],
            'URL': ['https://example.com', 'https://sample-website.org'],
            'DATE': ['2024-01-15', '2024-06-30', '2024-12-01']
        }
        
        # Context-aware suggestions
        self.context_suggestions = {
            'email_writing': "Consider using placeholder emails like 'recipient@company.com' instead of real addresses",
            'data_analysis': "Use sample data or anonymized datasets for analysis examples",
            'customer_service': "Replace customer names with generic identifiers like 'Customer A' or 'User123'",
            'financial': "Use placeholder account numbers and amounts for financial scenarios",
            'medical': "Replace patient information with generic medical case examples",
            'legal': "Use hypothetical parties like 'Party A' and 'Party B' in legal scenarios"
        }
    
    def detect_context(self, text: str) -> str:
        """Detect the likely context/domain of the prompt"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['email', 'message', 'send', 'reply', 'subject']):
            return 'email_writing'
        elif any(word in text_lower for word in ['data', 'analysis', 'chart', 'graph', 'statistics']):
            return 'data_analysis'
        elif any(word in text_lower for word in ['customer', 'client', 'service', 'support', 'complaint']):
            return 'customer_service'
        elif any(word in text_lower for word in ['payment', 'account', 'transaction', 'financial', 'money']):
            return 'financial'
        elif any(word in text_lower for word in ['patient', 'medical', 'health', 'diagnosis', 'treatment']):
            return 'medical'
        elif any(word in text_lower for word in ['contract', 'legal', 'court', 'lawsuit', 'agreement']):
            return 'legal'
        else:
            return 'general'
    
    def generate_protected_prompt(self, original_prompt: str) -> Dict:
        """Generate a privacy-protected version of the prompt"""
        
        # Analyze the original prompt
        analysis = self.pii_processor.analyze_text(original_prompt)
        
        if analysis['pii_count'] == 0:
            return {
                'original_prompt': original_prompt,
                'protected_prompt': original_prompt,
                'protection_applied': False,
                'detected_pii': [],
                'replacements_made': [],
                'suggestions': ["No PII detected. Your prompt appears to be privacy-safe!"],
                'context': self.detect_context(original_prompt),
                'risk_level': 'LOW',
                'pii_count': 0,
                'pii_types': []
            }
        
        # Create protected version
        protected_prompt = original_prompt
        replacements_made = []
        
        # Sort entities by length (longest first) to avoid partial replacements
        entities = sorted(analysis['detected_entities'], key=lambda x: len(x['text']), reverse=True)
        
        for entity in entities:
            pii_text = entity['text']
            pii_type = entity['type']
            
            # Choose appropriate replacement
            if pii_type in self.generic_replacements:
                replacement = random.choice(self.generic_replacements[pii_type])
            else:
                replacement = f"[{pii_type.replace('_', ' ').title()}]"
            
            # Replace in the prompt
            if pii_text in protected_prompt:
                protected_prompt = protected_prompt.replace(pii_text, replacement)
                replacements_made.append({
                    'original': pii_text,
                    'replacement': replacement,
                    'type': pii_type,
                    'confidence': entity['confidence']
                })
        
        # Detect context and provide suggestions
        context = self.detect_context(original_prompt)
        suggestions = self.generate_suggestions(entities, context)
        
        # Determine risk level
        risk_level = self.assess_risk_level(entities)
        
        return {
            'original_prompt': original_prompt,
            'protected_prompt': protected_prompt,
            'protection_applied': True,
            'detected_pii': entities,
            'replacements_made': replacements_made,
            'suggestions': suggestions,
            'context': context,
            'risk_level': risk_level,
            'pii_count': analysis['pii_count'],
            'pii_types': analysis['pii_types']
        }
    
    def generate_suggestions(self, entities: List[Dict], context: str) -> List[str]:
        """Generate context-aware suggestions for better privacy protection"""
        suggestions = []
        
        # Context-specific suggestion
        if context in self.context_suggestions:
            suggestions.append(self.context_suggestions[context])
        
        # PII-specific suggestions
        pii_types = [entity['type'] for entity in entities]
        
        if 'PERSON' in pii_types:
            suggestions.append("Use generic names like 'John Doe' or role-based identifiers like 'the manager'")
        
        if 'EMAIL' in pii_types:
            suggestions.append("Replace with example emails like 'user@example.com' or describe the email type")
        
        if 'PHONE' in pii_types:
            suggestions.append("Use placeholder numbers like '555-0123' or describe as 'phone number'")
        
        if any(pii in pii_types for pii in ['SSN', 'CREDIT_CARD', 'BANK_ACCOUNT']):
            suggestions.append("Replace sensitive numbers with 'XXXX-XXXX-XXXX-1234' format")
        
        if 'ADDRESS' in pii_types:
            suggestions.append("Use generic addresses like '123 Main Street, Anytown, ST 12345'")
        
        if 'ORGANIZATION' in pii_types:
            suggestions.append("Replace with generic company names like 'Company A' or 'TechCorp Inc'")
        
        # General suggestions
        suggestions.append("Review the protected prompt to ensure it still conveys your intended meaning")
        suggestions.append("Consider if any remaining context could indirectly identify individuals")
        
        return suggestions
    
    def assess_risk_level(self, entities: List[Dict]) -> str:
        """Assess the privacy risk level based on detected PII"""
        if not entities:
            return 'LOW'
        
        high_risk_types = ['SSN', 'CREDIT_CARD', 'BANK_ACCOUNT']
        medium_risk_types = ['EMAIL', 'PHONE', 'ADDRESS']
        
        pii_types = [entity['type'] for entity in entities]
        
        if any(pii_type in high_risk_types for pii_type in pii_types):
            return 'HIGH'
        elif any(pii_type in medium_risk_types for pii_type in pii_types):
            return 'MEDIUM'
        elif len(entities) > 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_alternative_prompts(self, original_prompt: str, num_alternatives: int = 3) -> List[str]:
        """Generate multiple alternative protected prompts"""
        alternatives = []
        
        for _ in range(num_alternatives):
            # Use different random replacements each time
            analysis = self.pii_processor.analyze_text(original_prompt)
            
            if analysis['pii_count'] == 0:
                alternatives.append(original_prompt)
                continue
            
            protected_prompt = original_prompt
            entities = sorted(analysis['detected_entities'], key=lambda x: len(x['text']), reverse=True)
            
            for entity in entities:
                pii_text = entity['text']
                pii_type = entity['type']
                
                if pii_type in self.generic_replacements:
                    replacement = random.choice(self.generic_replacements[pii_type])
                else:
                    replacement = f"[{pii_type.replace('_', ' ').title()}]"
                
                if pii_text in protected_prompt:
                    protected_prompt = protected_prompt.replace(pii_text, replacement)
            
            alternatives.append(protected_prompt)
        
        return alternatives

if __name__ == "__main__":
    # Test the prompt protector
    protector = PromptProtector()
    
    test_prompts = [
        "Write an email to John Smith at john.smith@company.com about the meeting scheduled for tomorrow. His phone number is 555-123-4567.",
        "Analyze the customer data for Sarah Johnson who lives at 123 Oak Street, New York, NY. Her account number is 1234567890.",
        "Create a report about the patient Mary Wilson, DOB 1985-03-15, SSN 123-45-6789, who was treated at General Hospital.",
        "Help me write a professional email without any personal information."
    ]
    
    print("🛡️ Prompt Protection System Test")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test Prompt {i}:")
        print(f"Original: {prompt}")
        
        result = protector.generate_protected_prompt(prompt)
        
        print(f"Protected: {result['protected_prompt']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"PII Found: {result['pii_count']} entities")
        
        if result['protection_applied']:
            print("Replacements made:")
            for replacement in result['replacements_made']:
                print(f"  • {replacement['original']} → {replacement['replacement']} ({replacement['type']})")
        
        print("Suggestions:")
        for suggestion in result['suggestions'][:2]:  # Show first 2 suggestions
            print(f"  • {suggestion}")
        
        print("-" * 50)