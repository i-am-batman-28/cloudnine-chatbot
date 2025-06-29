import pytest
from scraper.scraper import Cloud9Scraper
from scraper.parser import DataParser
from pathlib import Path
import json
import responses
from bs4 import BeautifulSoup

@pytest.fixture
def scraper():
    return Cloud9Scraper()

@pytest.fixture
def parser():
    return DataParser()

@pytest.fixture
def mock_html_content():
    return """
    <html>
        <body>
            <div class="department-card">
                <h3 class="department-name">Cardiology</h3>
                <p class="department-description">Advanced cardiac care and treatment</p>
                <div class="doctor-card">
                    <h4 class="doctor-name">Dr. John Smith</h4>
                    <p class="doctor-specialization">Interventional Cardiology</p>
                    <p class="doctor-qualifications">MD, DM Cardiology</p>
                    <span class="experience">15 years</span>
                    <p class="languages">English, Hindi</p>
                </div>
                <div class="service-card">
                    <h5 class="service-name">Cardiac Consultation</h5>
                    <p class="service-description">Comprehensive heart checkup</p>
                    <span class="duration">30 minutes</span>
                    <span class="cost">2000 INR</span>
                </div>
            </div>
            <div class="faq-item" data-category="general">
                <h6 class="faq-question">What are your working hours?</h6>
                <p class="faq-answer">We are open 24/7 for emergencies. Regular OPD hours are 9 AM to 6 PM.</p>
            </div>
        </body>
    </html>
    """

@responses.activate
def test_scraper_departments(scraper, mock_html_content):
    """Test department scraping functionality"""
    responses.add(
        responses.GET,
        f"{scraper.base_url}/departments",
        body=mock_html_content,
        status=200
    )

    departments = scraper.scrape_departments()
    
    assert departments is not None
    assert len(departments) > 0
    assert 'name' in departments[0]
    assert 'description' in departments[0]
    assert departments[0]['name'] == 'Cardiology'

@responses.activate
def test_scraper_doctors(scraper, mock_html_content):
    """Test doctor information scraping"""
    responses.add(
        responses.GET,
        f"{scraper.base_url}/departments/1/doctors",
        body=mock_html_content,
        status=200
    )

    doctors = scraper.scrape_department_doctors('1')
    
    assert doctors is not None
    assert len(doctors) > 0
    assert 'name' in doctors[0]
    assert 'specialization' in doctors[0]
    assert doctors[0]['name'] == 'Dr. John Smith'

@responses.activate
def test_scraper_services(scraper, mock_html_content):
    """Test service information scraping"""
    responses.add(
        responses.GET,
        f"{scraper.base_url}/departments/1/services",
        body=mock_html_content,
        status=200
    )

    services = scraper.scrape_department_services('1')
    
    assert services is not None
    assert len(services) > 0
    assert 'name' in services[0]
    assert 'description' in services[0]
    assert services[0]['name'] == 'Cardiac Consultation'

@responses.activate
def test_scraper_faqs(scraper, mock_html_content):
    """Test FAQ scraping functionality"""
    responses.add(
        responses.GET,
        f"{scraper.base_url}/faqs",
        body=mock_html_content,
        status=200
    )

    faqs = scraper.scrape_faqs()
    
    assert faqs is not None
    assert len(faqs) > 0
    assert 'question' in faqs[0]
    assert 'answer' in faqs[0]
    assert faqs[0]['question'] == 'What are your working hours?'

def test_parser_departments(parser):
    """Test department data parsing"""
    test_data = [{
        'name': 'Cardiology',
        'description': 'Advanced cardiac care and treatment for heart conditions',
        'doctors': [{
            'name': 'Dr. John Smith',
            'specialization': 'Interventional Cardiology',
            'qualifications': 'MD, DM Cardiology',
            'experience': '15 years',
            'languages': ['English', 'Hindi']
        }]
    }]

    parsed_departments = parser.parse_departments(test_data)
    
    assert parsed_departments is not None
    assert len(parsed_departments) > 0
    assert 'name' in parsed_departments[0]
    assert 'keywords' in parsed_departments[0]
    assert 'doctors' in parsed_departments[0]

def test_parser_faqs(parser):
    """Test FAQ data parsing"""
    test_data = [{
        'question': 'What are your working hours?',
        'answer': 'We are open 24/7 for emergencies. Regular OPD hours are 9 AM to 6 PM.',
        'category': 'general'
    }]

    parsed_faqs = parser.parse_faqs(test_data)
    
    assert parsed_faqs is not None
    assert len(parsed_faqs) > 0
    assert 'question' in parsed_faqs[0]
    assert 'answer' in parsed_faqs[0]
    assert 'keywords' in parsed_faqs[0]

def test_parser_doctors(parser):
    """Test doctor information parsing"""
    test_data = [{
        'name': 'Dr. John Smith',
        'specialization': 'Interventional Cardiology',
        'qualifications': 'MD, DM Cardiology',
        'experience': '15 years',
        'languages': ['English', 'Hindi']
    }]

    parsed_doctors = parser._parse_doctors(test_data)
    
    assert parsed_doctors is not None
    assert len(parsed_doctors) > 0
    assert 'name' in parsed_doctors[0]
    assert 'experience_years' in parsed_doctors[0]
    assert parsed_doctors[0]['experience_years'] == 15

def test_parser_services(parser):
    """Test service information parsing"""
    test_data = [{
        'name': 'Cardiac Consultation',
        'description': 'Comprehensive heart checkup',
        'duration': '30 minutes',
        'cost': '2000 INR'
    }]

    parsed_services = parser._parse_services(test_data)
    
    assert parsed_services is not None
    assert len(parsed_services) > 0
    assert 'name' in parsed_services[0]
    assert 'duration' in parsed_services[0]
    assert 'cost' in parsed_services[0]

def test_parser_text_cleaning(parser):
    """Test text cleaning functionality"""
    test_text = "  This is a   test text with  extra   spaces  "
    cleaned_text = parser._clean_text(test_text)
    
    assert cleaned_text == "This is a test text with extra spaces"

def test_parser_keyword_extraction(parser):
    """Test keyword extraction functionality"""
    test_text = "Cardiology department provides advanced cardiac care and treatment"
    keywords = parser._extract_keywords(test_text)
    
    assert keywords is not None
    assert len(keywords) > 0
    assert 'cardiology' in keywords
    assert 'cardiac' in keywords
    assert 'treatment' in keywords

def test_parser_duration_parsing(parser):
    """Test duration parsing functionality"""
    test_duration = "1 hour 30 minutes"
    parsed_duration = parser._parse_duration(test_duration)
    
    assert parsed_duration is not None
    assert parsed_duration['total_minutes'] == 90
    assert parsed_duration['formatted'] == "1h 30m"

def test_parser_cost_parsing(parser):
    """Test cost parsing functionality"""
    test_cost = "2000 INR"
    parsed_cost = parser._parse_cost(test_cost)
    
    assert parsed_cost is not None
    assert parsed_cost['amount'] == 2000
    assert parsed_cost['currency'] == 'INR'
    assert parsed_cost['formatted'] == "INR 2,000.00"