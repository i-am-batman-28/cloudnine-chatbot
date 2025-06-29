import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome, ChromeOptions

class CloudNineScraper:
    def __init__(self):
        self.base_url = "https://www.cloudninecare.com"
        self.api_key = "e426f6be00783634bbf620fd4310af20"
        self.output_dir = Path(__file__).parent.parent / 'data/raw/cloudnine_scraped'
        self.driver = self._setup_driver()
        self._setup_logging()

    def _setup_driver(self) -> Chrome:
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return Chrome(options=options)

    def _setup_logging(self):
        logger.add(
            self.output_dir.parent / 'scraper.log',
            rotation="100 MB",
            retention="10 days",
            level="DEBUG"
        )

    def _safe_request(self, url: str, use_selenium: bool = False) -> Optional[str]:
        try:
            if use_selenium:
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            else:
                payload = {
                    'api_key': self.api_key,
                    'url': url
                }
                response = requests.get("https://api.scraperapi.com/", params=payload, timeout=10)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def scrape_departments(self) -> List[Dict]:
        departments = []
        try:
            url = f"{self.base_url}/about-us"
            html = self._safe_request(url, use_selenium=True)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                dept_sections = soup.find_all(['div', 'section'], class_=['department', 'specialty', 'service-section'])
                for section in dept_sections:
                    headers = section.find_all(['h2', 'h3', 'h4'])
                    for header in headers:
                        description = header.find_next('p')
                        department = {
                            'name': header.text.strip(),
                            'description': description.text.strip() if description else '',
                            'services': []
                        }
                        service_elements = section.find_all(['li', 'p', 'div'], class_=['service', 'feature'])
                        for service in service_elements:
                            if service != description:
                                department['services'].append(service.text.strip())
                        if department['name'] and not any(d['name'] == department['name'] for d in departments):
                            departments.append(department)
                logger.info(f"Scraped {len(departments)} departments")
        except Exception as e:
            logger.error(f"Error scraping departments: {str(e)}")
        return departments

    def scrape_doctors(self) -> List[Dict]:
        doctors = []
        try:
            html = self._safe_request(f"{self.base_url}/our-team", use_selenium=True)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                team_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(c in str(x).lower() for c in ['team', 'doctor', 'profile', 'member']))
                for section in team_sections:
                    name_elem = section.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                    if name_elem:
                        name = name_elem.text.strip()
                        if 'dr' in name.lower():
                            role_elem = section.find(['span', 'div', 'p'], class_=lambda x: x and any(c in str(x).lower() for c in ['role', 'position', 'title', 'designation']))
                            role = role_elem.text.strip() if role_elem else ''
                            dept_elem = section.find(['span', 'div', 'p'], class_=lambda x: x and any(c in str(x).lower() for c in ['department', 'specialty', 'expertise']))
                            department = dept_elem.text.strip() if dept_elem else ''
                            desc_elem = section.find('p', class_=lambda x: x and 'role' not in str(x).lower())
                            description = desc_elem.text.strip() if desc_elem else ''
                            if not any(d['name'].lower() == name.lower() for d in doctors):
                                doctors.append({
                                    'name': name,
                                    'description': description,
                                    'role': role,
                                    'department': department,
                                    'source_page': '/our-team'
                                })

            html = self._safe_request(self.base_url, use_selenium=True)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                specialities_menu = soup.find('a', text=lambda t: t and 'Specialities' in t)
                if specialities_menu:
                    speciality_links = specialities_menu.find_parent().find_all('a')
                    for link in speciality_links:
                        if link.get('href'):
                            spec_html = self._safe_request(f"{self.base_url}{link.get('href')}", use_selenium=True)
                            if spec_html:
                                spec_soup = BeautifulSoup(spec_html, 'html.parser')
                                doctor_sections = spec_soup.find_all(['div', 'section'], class_=lambda x: x and any(c in str(x).lower() for c in ['doctor', 'consultant', 'specialist']))
                                for section in doctor_sections:
                                    name_elem = section.find(['h3', 'h4', 'strong'])
                                    if name_elem and 'dr' in name_elem.text.lower():
                                        name = name_elem.text.strip()
                                        desc_elem = section.find('p')
                                        description = desc_elem.text.strip() if desc_elem else ''
                                        if not any(d['name'].lower() == name.lower() for d in doctors):
                                            doctors.append({
                                                'name': name,
                                                'description': description,
                                                'role': '',
                                                'department': link.text.strip(),
                                                'source_page': link.get('href')
                                            })
            logger.info(f"Scraped {len(doctors)} doctor profiles")
        except Exception as e:
            logger.error(f"Error scraping doctors: {str(e)}")
        return doctors

    def scrape_services(self) -> List[Dict]:
        services = []
        try:
            html = self._safe_request(self.base_url, use_selenium=True)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                service_menu = soup.find('a', text=lambda t: t and 'Home Services' in t)
                if service_menu:
                    service_items = service_menu.find_parent().find_all(['a', 'li'])
                    for item in service_items:
                        service_name = item.text.strip()
                        if service_name and service_name != 'Home Services':
                            services.append({
                                'name': service_name,
                                'description': '',
                                'features': [],
                                'source_page': 'navigation'
                            })
                specialities_menu = soup.find('a', text=lambda t: t and 'Specialities' in t)
                if specialities_menu:
                    speciality_items = specialities_menu.find_parent().find_all(['a', 'li'])
                    for item in speciality_items:
                        speciality_name = item.text.strip()
                        if speciality_name and speciality_name != 'Specialities':
                            services.append({
                                'name': speciality_name,
                                'description': '',
                                'features': [],
                                'source_page': 'specialities'
                            })
                service_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(c in str(x).lower() for c in ['service', 'feature', 'offering']))
                for section in service_sections:
                    name_elem = section.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                    if name_elem:
                        service_name = name_elem.text.strip()
                        desc_elem = name_elem.find_next(['p', 'div'])
                        description = desc_elem.text.strip() if desc_elem else ''
                        features = [f.text.strip() for f in section.find_all('li') if f.text.strip()]
                        if service_name and not any(s['name'].lower() == service_name.lower() for s in services):
                            services.append({
                                'name': service_name,
                                'description': description,
                                'features': features[:5],
                                'source_page': 'homepage'
                            })
                service_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(c in str(x).lower() for c in ['card', 'block', 'item']))
                for card in service_cards:
                    card_text = card.get_text().lower()
                    if any(k in card_text for k in ['service', 'care', 'treatment']):
                        name_elem = card.find(['h3', 'h4', 'strong', 'span'])
                        if name_elem:
                            service_name = name_elem.text.strip()
                            desc_elem = card.find('p')
                            description = desc_elem.text.strip() if desc_elem else ''
                            if service_name and not any(s['name'].lower() == service_name.lower() for s in services):
                                services.append({
                                    'name': service_name,
                                    'description': description,
                                    'features': [],
                                    'source_page': 'homepage'
                                })
            logger.info(f"Scraped {len(services)} services")
        except Exception as e:
            logger.error(f"Error scraping services: {str(e)}")
        return services

    def scrape_faqs(self) -> List[Dict]:
        faqs = []
        pages = ['/', '/about-us', '/contact-us']
        try:
            for page in pages:
                url = f"{self.base_url}{page}"
                html = self._safe_request(url, use_selenium=True)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    faq_sections = soup.find_all(['div', 'section'], class_=['faq', 'accordion', 'question-answer'])
                    for section in faq_sections:
                        questions = section.find_all(['h3', 'h4', 'button', 'div'], class_=['question', 'accordion-header'])
                        for question in questions:
                            answer = question.find_next(['p', 'div'], class_=['answer', 'accordion-content'])
                            if answer:
                                faq = {
                                    'question': question.text.strip(),
                                    'answer': answer.text.strip(),
                                    'source_page': page
                                }
                                if faq['question'] and not any(f['question'] == faq['question'] for f in faqs):
                                    faqs.append(faq)
                    qa_elements = soup.find_all(['div', 'section'], class_=['qa', 'help', 'support'])
                    for element in qa_elements:
                        questions = element.find_all(['h3', 'h4', 'strong'])
                        for question in questions:
                            answer = question.find_next('p')
                            if answer:
                                faq = {
                                    'question': question.text.strip(),
                                    'answer': answer.text.strip(),
                                    'source_page': page
                                }
                                if faq['question'] and not any(f['question'] == faq['question'] for f in faqs):
                                    faqs.append(faq)
            logger.info(f"Scraped {len(faqs)} FAQs from {len(pages)} pages")
        except Exception as e:
            logger.error(f"Error scraping FAQs: {str(e)}")
        return faqs

    def save_data(self, data: List[Dict], filename: str):
        try:
            if not self.output_dir.exists():
                self.output_dir.mkdir(parents=True)
            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {output_file}")
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")

    def scrape_all(self):
        try:
            departments = self.scrape_departments()
            self.save_data(departments, 'departments.json')

            doctors = self.scrape_doctors()
            self.save_data(doctors, 'doctors.json')

            services = self.scrape_services()
            self.save_data(services, 'services.json')

            faqs = self.scrape_faqs()
            self.save_data(faqs, 'faqs.json')

            logger.info("Completed scraping all data")
        except Exception as e:
            logger.error(f"Error during complete scrape: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = CloudNineScraper()
    scraper.scrape_all()
