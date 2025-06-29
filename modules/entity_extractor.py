import spacy
import re
from typing import Dict, List, Optional
from app.config import NLP_CONFIG

class EntityExtractor:
    def __init__(self):
        self.config = NLP_CONFIG['ENTITY_EXTRACTOR']
        self.nlp = spacy.load(self.config['MODEL_TYPE'])
        self.custom_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict:
        return {
            'SYMPTOM': [
                r'(head|stomach|back|chest|throat)\s?(ache|pain)',
                r'(feeling|feel)\s(sick|nauseous|dizzy|tired|weak)',
                r'(have|having)\s(fever|cough|cold|flu|anxiety|depression)'
            ],
            'DEPARTMENT': [
                r'(cardiology|neurology|pediatrics|orthopedics|gynecology|dermatology|oncology|ent|dental)',
                r'(heart|brain|child|bone|skin|cancer|ear|tooth)\s?(specialist|department|clinic|center)'
            ],
            'DOCTOR': [
                r'dr\.?\s[a-z]+',
                r'doctor\s[a-z]+',
                r'(specialist|physician|surgeon)\s(dr\.?\s)?[a-z]+'
            ],
            'DATE_TIME': [
                r'(today|tomorrow|next|this)\s(morning|afternoon|evening|week|month)',
                r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                r'\d{1,2}[:/]\d{1,2}([:/]\d{2,4})?',
                r'\d{1,2}\s?(am|pm|AM|PM)'
            ],
            'URGENCY': [
                r'(emergency|urgent|immediate|asap|critical)',
                r'(life[\s-]threatening|severe|serious)'
            ],
            'PREVIOUS_VISIT': [
                r'\b(yes|i have|been there before|visited before)\b',
                r'\b(no|i haven\'?t|never been|first time)\b'
            ]
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {
            'PERSON': [],
            'DATE': [],
            'TIME': [],
            'SYMPTOM': [],
            'DEPARTMENT': [],
            'DOCTOR': [],
            'URGENCY': [],
            'PREVIOUS_VISIT': []
        }

        doc = self.nlp(text.lower())
        for ent in doc.ents:
            if ent.label_.upper() in entities:
                entities[ent.label_.upper()].append(ent.text)

        for entity_type, patterns in self.custom_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    value = match.group().strip()
                    if value not in entities[entity_type]:
                        entities[entity_type].append(value)

        return self._clean_entities(entities)

    def _clean_entities(self, entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
        cleaned = {}
        for entity_type, values in entities.items():
            unique = list(set([v.strip() for v in values if v.strip()]))
            unique.sort(key=len, reverse=True)
            final_values = []
            for i, val in enumerate(unique):
                if not any(val in other for j, other in enumerate(unique) if i != j):
                    final_values.append(val)
            cleaned[entity_type] = final_values
        return cleaned

    def extract_medical_context(self, text: str) -> Dict[str, any]:
        entities = self.extract_entities(text)
        context = {
            'symptoms': entities.get('SYMPTOM', []),
            'urgency_level': self._determine_urgency(entities.get('URGENCY', [])),
            'department_preference': entities.get('DEPARTMENT', []),
            'doctor_preference': entities.get('DOCTOR', []),
            'previous_visit': self._resolve_previous_visit(entities.get('PREVIOUS_VISIT', [])),
            'temporal_context': self._merge_temporal_entities(entities)
        }
        return context

    def _determine_urgency(self, urgency_entities: List[str]) -> str:
        emergency_terms = {'emergency', 'critical', 'life-threatening'}
        urgent_terms = {'urgent', 'immediate', 'asap'}
        for term in urgency_entities:
            if any(e in term for e in emergency_terms):
                return 'emergency'
            if any(u in term for u in urgent_terms):
                return 'urgent'
        return 'routine'

    def _merge_temporal_entities(self, entities: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
        return {
        'date': entities.get('DATE')[0] if entities.get('DATE') else None,
        'time': entities.get('TIME')[0] if entities.get('TIME') else None,
        'relative_time': entities.get('DATE_TIME')[0] if entities.get('DATE_TIME') else None
    }

        

    def _resolve_previous_visit(self, visit_phrases: List[str]) -> Optional[str]:
        for phrase in visit_phrases:
            if re.search(r'\b(no|never|not|first time|haven\'?t)\b', phrase):
                return 'no'
            elif re.search(r'\b(yes|visited|been|have)\b', phrase):
                return 'yes'
        return None
