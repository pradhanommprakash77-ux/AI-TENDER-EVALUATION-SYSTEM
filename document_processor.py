import PyPDF2
import pdfplumber
import re
import spacy
from typing import Dict, List, Any
import os

class DocumentProcessor:
    def __init__(self):
        # Load NLP model (will download first time)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Document patterns for Indian government documents
        self.document_patterns = {
            'gst_certificate': r'GST|Goods and Services Tax|GSTIN[:\s]*([0-9A-Z]{15})',
            'pan_card': r'Permanent Account Number|PAN[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            'epf_registration': r'EPF|Employee Provident Fund|PF Code[:\s]*([A-Z0-9]+)',
            'esi_registration': r'ESI|Employee State Insurance|ESI Code[:\s]*([A-Z0-9]+)',
            'msme_certificate': r'MSME|Udyam|Udyog Aadhar|UAM[:\s]*([0-9]+)',
            'income_tax_return': r'Income Tax Return|ITR|Form 16',
            'company_registration': r'CIN[:\s]*([A-Z0-9]{21})|Certificate of Incorporation'
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except:
                pass
                
        return text

    def identify_documents(self, text: str) -> Dict[str, bool]:
        """Identify which documents are present in the text"""
        documents_found = {}
        
        for doc_type, pattern in self.document_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            documents_found[doc_type] = match is not None
            
            # Extract ID if found
            if match and match.groups():
                documents_found[f"{doc_type}_id"] = match.group(1)
                
        return documents_found

    def extract_company_details(self, text: str) -> Dict[str, str]:
        """Extract company details from text"""
        details = {}
        
        # Extract company name
        name_patterns = [
            r'(?:Company|Firm|Organization)\s*Name[:\s]*([A-Za-z\s]+)(?:\n|$)',
            r'(?:M/s|M/s\.)\s*([A-Za-z\s]+)(?:\n|$)',
            r'^([A-Za-z\s]+(?:Pvt|Private|Limited|Ltd|LLP))'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['company_name'] = match.group(1).strip()
                break
                
        # Extract contact details
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'(?:\+91|0)?[6-9]\d{9}'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        if emails:
            details['email'] = emails[0]
        if phones:
            details['phone'] = phones[0]
            
        # Extract address
        address_pattern = r'Address[:\s]*([^\n]+(?:\n[^\n]+){0,3})'
        match = re.search(address_pattern, text, re.IGNORECASE)
        if match:
            details['address'] = match.group(1).strip()
            
        return details

    def extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract experience information"""
        experience = {
            'years': 0,
            'projects': [],
            'total_projects': 0,
            'total_value': 0
        }
        
        # Find years of experience
        year_patterns = [
            r'(\d+)\s*(?:years|yrs)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\s*(?:years|yrs)'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                experience['years'] = int(match.group(1))
                break
                
        # Find project details
        project_lines = re.findall(r'(?:Project|Contract)[^.]*?(?:worth|value|amount)[^.]*?(?:Rs\.?|₹)\s*([\d,]+)', text)
        for value in project_lines:
            try:
                clean_value = float(value.replace(',', ''))
                experience['total_value'] += clean_value
                experience['total_projects'] += 1
                experience['projects'].append({'value': clean_value})
            except:
                pass
                
        return experience

    def extract_financial_info(self, text: str) -> Dict[str, Any]:
        """Extract financial information"""
        financial = {
            'turnover': [],
            'bid_amount': None,
            'quoted_items': []
        }
        
        # Find turnover
        turnover_patterns = [
            r'turnover[^.]*?(?:Rs\.?|₹)\s*([\d,]+)',
            r'annual[^.]*?(?:Rs\.?|₹)\s*([\d,]+)',
            r'revenue[^.]*?(?:Rs\.?|₹)\s*([\d,]+)'
        ]
        
        for pattern in turnover_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.replace(',', ''))
                    financial['turnover'].append(value)
                except:
                    pass
                    
        # Find bid amount
        bid_patterns = [
            r'bid\s*(?:amount|price|value)[^.]*?(?:Rs\.?|₹)\s*([\d,]+)',
            r'total\s*(?:amount|price|value)[^.]*?(?:Rs\.?|₹)\s*([\d,]+)'
        ]
        
        for pattern in bid_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    financial['bid_amount'] = float(match.group(1).replace(',', ''))
                    break
                except:
                    pass
                    
        return financial

    def process_bid(self, file_path: str) -> Dict[str, Any]:
        """Process a bid document and return extracted data"""
        text = self.extract_text_from_pdf(file_path)
        if not text:
            return {"error": "Could not extract text from PDF"}
        return {
            'filename': os.path.basename(file_path),
            'documents': self.identify_documents(text),
            'company_details': self.extract_company_details(text),
            'experience': self.extract_experience(text),
            'financial': self.extract_financial_info(text)
        }

    def process_all_bids(self, bid_folder: str) -> List[Dict[str, Any]]:
        """Process all bids in a folder"""
        results = []
        
        for filename in os.listdir(bid_folder):
            if filename.endswith('.pdf'):
                file_path = os.path.join(bid_folder, filename)
                result = self.process_bid(file_path)
                results.append(result)
                
        return results