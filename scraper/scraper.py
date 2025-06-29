import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import time
from pathlib import Path
from datetime import datetime
import logging
from app.config import SCRAPER_CONFIG, DATA_CONFIG

class Cloud9Scraper:
    def __init__(self):
        self.config = SCRAPER_CONFIG
        self.headers = self.config['HEADERS']
        self.base_url = self.config['BASE_URL']
        self.timeout = self.config['TIMEOUT']
        self.retry_attempts = self.config['RETRY_ATTEMPTS']
        self.delay = self.config['DELAY_BETWEEN_REQUESTS']
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def make_request(self, url: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make HTTP request with retry mechanism"""
        for attempt in range(self.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = requests.get(
                        url,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                elif method.upper() == 'POST':
                    response = requests.post(
                        url,
                        headers=self.headers,
                        json=data,
                        timeout=self.timeout
                    )
                else:
                    self.logger.error(f"Unsupported HTTP method: {method}")
                    return None

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {self.retry_attempts} attempts")
                    return None

    def scrape_departments(self) -> List[Dict]:
        """Scrape department information"""
        departments = []
        department_url = f"{self.base_url}/departments"  # Adjust based on actual URL structure
        
        response = self.make_request(department_url)
        if not response:
            return departments

        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust selectors based on actual website structure
        department_elements = soup.find_all('div', class_='department-card')

        for element in department_elements:
            department = {
                'name': element.find('h3', class_='department-name').text.strip(),
                'description': element.find('p', class_='department-description').text.strip(),
                'doctors': self.scrape_department_doctors(element.get('data-department-id')),
                'services': self.scrape_department_services(element.get('data-department-id'))
            }
            departments.append(department)

        return departments

    def scrape_department_doctors(self, department_id: str) -> List[Dict]:
        """Scrape doctors for a specific department"""
        doctors = []
        doctors_url = f"{self.base_url}/departments/{department_id}/doctors"  # Adjust URL

        response = self.make_request(doctors_url)
        if not response:
            return doctors

        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust selectors based on actual website structure
        doctor_elements = soup.find_all('div', class_='doctor-card')

        for element in doctor_elements:
            doctor = {
                'name': element.find('h4', class_='doctor-name').text.strip(),
                'specialization': element.find('p', class_='doctor-specialization').text.strip(),
                'qualifications': element.find('p', class_='doctor-qualifications').text.strip(),
                'experience': element.find('span', class_='experience').text.strip(),
                'languages': [lang.strip() for lang in element.find('p', class_='languages').text.split(',')]
            }
            doctors.append(doctor)

        return doctors

    def scrape_department_services(self, department_id: str) -> List[Dict]:
        """Scrape services offered by a specific department"""
        services = []
        services_url = f"{self.base_url}/departments/{department_id}/services"  # Adjust URL

        response = self.make_request(services_url)
        if not response:
            return services

        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust selectors based on actual website structure
        service_elements = soup.find_all('div', class_='service-card')

        for element in service_elements:
            service = {
                'name': element.find('h5', class_='service-name').text.strip(),
                'description': element.find('p', class_='service-description').text.strip(),
                'duration': element.find('span', class_='duration').text.strip(),
                'cost': element.find('span', class_='cost').text.strip()
            }
            services.append(service)

        return services

    def scrape_faqs(self) -> List[Dict]:
        """Scrape frequently asked questions"""
        faqs = []
        faq_url = f"{self.base_url}/faqs"  # Adjust URL

        response = self.make_request(faq_url)
        if not response:
            return faqs

        soup = BeautifulSoup(response.text, 'html.parser')
        # Adjust selectors based on actual website structure
        faq_elements = soup.find_all('div', class_='faq-item')

        for element in faq_elements:
            faq = {
                'question': element.find('h6', class_='faq-question').text.strip(),
                'answer': element.find('p', class_='faq-answer').text.strip(),
                'category': element.get('data-category', 'general')
            }
            faqs.append(faq)

        return faqs

    def scrape_all(self) -> Dict:
        """Scrape all relevant information"""
        scraped_data = {
            'departments': self.scrape_departments(),
            'faqs': self.scrape_faqs(),
            'timestamp': datetime.now().isoformat()
        }

        # Save scraped data
        self.save_scraped_data(scraped_data)
        return scraped_data

    def save_scraped_data(self, data: Dict) -> None:
        """Save scraped data to files"""
        output_dir = Path(DATA_CONFIG['RAW_DATA_DIR'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each data type separately
        for data_type, content in data.items():
            output_file = output_dir / f"{data_type}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Scraped data saved to {output_dir}")

    def load_scraped_data(self, date_str: Optional[str] = None) -> Dict:
        """Load previously scraped data"""
        data = {}
        input_dir = Path(DATA_CONFIG['RAW_DATA_DIR'])

        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')

        for data_type in ['departments', 'faqs']:
            input_file = input_dir / f"{data_type}_{date_str}.json"
            if input_file.exists():
                with open(input_file, 'r', encoding='utf-8') as f:
                    data[data_type] = json.load(f)
            else:
                self.logger.warning(f"No data file found for {data_type} on {date_str}")

        return data