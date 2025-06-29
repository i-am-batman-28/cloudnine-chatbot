from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime
import re
from app.config import DATA_CONFIG

class DataParser:
    def __init__(self):
        self.processed_data_dir = Path(DATA_CONFIG['PROCESSED_DATA_DIR'])
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

    def parse_departments(self, departments_data: List[Dict]) -> List[Dict]:
        """Parse and structure department information"""
        parsed_departments = []

        for dept in departments_data:
            parsed_dept = {
                'name': self._clean_text(dept['name']),
                'description': self._clean_text(dept['description']),
                'keywords': self._extract_keywords(dept['description']),
                'doctors': self._parse_doctors(dept.get('doctors', [])),
                'services': self._parse_services(dept.get('services', [])),
                'common_conditions': self._extract_conditions(dept['description'])
            }
            parsed_departments.append(parsed_dept)

        return parsed_departments

    def parse_faqs(self, faqs_data: List[Dict]) -> List[Dict]:
        """Parse and structure FAQ information"""
        parsed_faqs = []

        for faq in faqs_data:
            parsed_faq = {
                'question': self._clean_text(faq['question']),
                'answer': self._clean_text(faq['answer']),
                'category': faq.get('category', 'general'),
                'keywords': self._extract_keywords(faq['question'] + ' ' + faq['answer']),
                'entities': self._extract_entities(faq['answer'])
            }
            parsed_faqs.append(parsed_faq)

        return parsed_faqs

    def _parse_doctors(self, doctors_data: List[Dict]) -> List[Dict]:
        """Parse and structure doctor information"""
        parsed_doctors = []

        for doctor in doctors_data:
            parsed_doctor = {
                'name': self._clean_text(doctor['name']),
                'specialization': self._clean_text(doctor['specialization']),
                'qualifications': self._parse_qualifications(doctor['qualifications']),
                'experience_years': self._extract_experience_years(doctor['experience']),
                'languages': [self._clean_text(lang) for lang in doctor.get('languages', [])],
                'expertise': self._extract_expertise(doctor.get('specialization', ''))
            }
            parsed_doctors.append(parsed_doctor)

        return parsed_doctors

    def _parse_services(self, services_data: List[Dict]) -> List[Dict]:
        """Parse and structure service information"""
        parsed_services = []

        for service in services_data:
            parsed_service = {
                'name': self._clean_text(service['name']),
                'description': self._clean_text(service['description']),
                'duration': self._parse_duration(service.get('duration', '')),
                'cost': self._parse_cost(service.get('cost', '')),
                'keywords': self._extract_keywords(service['description'])
            }
            parsed_services.append(parsed_service)

        return parsed_services

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters except punctuation
        text = re.sub(r'[^\w\s.,;?!-]', '', text)
        return text

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Remove common words and extract key terms
        common_words = {'and', 'or', 'the', 'in', 'at', 'of', 'to', 'for', 'a', 'an'}
        words = text.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        return list(set(keywords))

    def _extract_conditions(self, text: str) -> List[str]:
        """Extract medical conditions from text"""
        # This is a simplified version - in practice, you'd use a medical NER model
        condition_patterns = [
            r'(?i)(treats|treating|treatment of|for) ([\w\s]+)',
            r'(?i)(conditions like|such as) ([\w\s]+)',
            r'(?i)(specializes in) ([\w\s]+)'
        ]

        conditions = []
        for pattern in condition_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                condition = match.group(2).strip()
                if condition and len(condition) > 3:
                    conditions.append(condition)

        return list(set(conditions))

    def _parse_qualifications(self, qualifications: str) -> List[str]:
        """Parse and structure qualification information"""
        # Split by common separators
        quals = re.split(r'[,;]', qualifications)
        return [self._clean_text(qual) for qual in quals if qual.strip()]

    def _extract_experience_years(self, experience: str) -> int:
        """Extract years of experience from text"""
        # Look for numbers followed by 'years' or 'yrs'
        match = re.search(r'(\d+)\s*(?:years?|yrs?)', experience.lower())
        return int(match.group(1)) if match else 0

    def _extract_expertise(self, specialization: str) -> List[str]:
        """Extract areas of expertise from specialization"""
        # Split by common separators and clean
        expertise = re.split(r'[,;&]', specialization)
        return [self._clean_text(exp) for exp in expertise if exp.strip()]

    def _parse_duration(self, duration: str) -> Dict:
        """Parse duration information"""
        duration = duration.lower()
        minutes = 0

        # Extract hours and minutes
        hr_match = re.search(r'(\d+)\s*(?:hours?|hrs?)', duration)
        min_match = re.search(r'(\d+)\s*(?:minutes?|mins?)', duration)

        if hr_match:
            minutes += int(hr_match.group(1)) * 60
        if min_match:
            minutes += int(min_match.group(1))

        return {
            'total_minutes': minutes,
            'formatted': f"{minutes // 60}h {minutes % 60}m" if minutes >= 60 else f"{minutes}m"
        }

    def _parse_cost(self, cost: str) -> Dict:
        """Parse cost information"""
        # Extract numeric value and currency
        match = re.search(r'([\d,]+)\s*([\w]+)', cost)
        if not match:
            return {'amount': 0, 'currency': 'INR'}

        amount = float(match.group(1).replace(',', ''))
        currency = match.group(2) or 'INR'

        return {
            'amount': amount,
            'currency': currency,
            'formatted': f"{currency} {amount:,.2f}"
        }

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'locations': [],
            'procedures': [],
            'medications': [],
            'medical_terms': []
        }

        # This is a simplified version - in practice, you'd use a medical NER model
        # Extract locations
        locations = re.findall(r'(?i)(?:at|in) ([\w\s]+(?:hospital|clinic|center))', text)
        entities['locations'].extend([loc.strip() for loc in locations])

        # Extract procedures
        procedures = re.findall(r'(?i)(?:procedure|surgery|test) ([\w\s]+)', text)
        entities['procedures'].extend([proc.strip() for proc in procedures])

        return entities

    def generate_intents(self, parsed_data: Dict) -> List[Dict]:
        """Generate intent patterns from parsed data"""
        intents = []

        # Generate department-related intents
        for dept in parsed_data.get('departments', []):
            intent = {
                'name': f"department_{dept['name'].lower().replace(' ', '_')}",
                'patterns': [
                    f"Tell me about the {dept['name']} department",
                    f"What services does {dept['name']} offer?",
                    f"Who are the doctors in {dept['name']}?"
                ],
                'responses': [dept['description']],
                'context': {
                    'department': dept['name'],
                    'keywords': dept['keywords']
                }
            }
            intents.append(intent)

        # Generate FAQ-based intents
        for faq in parsed_data.get('faqs', []):
            intent = {
                'name': f"faq_{faq['category'].lower()}",
                'patterns': [faq['question']],
                'responses': [faq['answer']],
                'context': {
                    'category': faq['category'],
                    'keywords': faq['keywords']
                }
            }
            intents.append(intent)

        return intents

    def save_processed_data(self, data: Dict, date_str: Optional[str] = None) -> None:
        """Save processed data to files"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')

        # Save structured data
        for data_type, content in data.items():
            output_file = self.processed_data_dir / f"{data_type}_{date_str}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

        # Generate and save intents
        intents = self.generate_intents(data)
        intents_file = self.processed_data_dir / 'intents.json'
        with open(intents_file, 'w', encoding='utf-8') as f:
            json.dump({'intents': intents}, f, indent=2, ensure_ascii=False)