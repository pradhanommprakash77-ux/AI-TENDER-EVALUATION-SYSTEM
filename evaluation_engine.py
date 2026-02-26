from typing import Dict, List, Any
import re

class EvaluationEngine:
    def __init__(self):
        self.tender_requirements = self.load_default_requirements()
        
    def load_default_requirements(self):
        """Load default tender requirements"""
        return {
            'mandatory_documents': [
                'gst_certificate',
                'pan_card',
                'epf_registration',
                'esi_registration',
                'income_tax_return'
            ],
            'min_experience_years': 3,
            'min_annual_turnover': 5000000,  # 50 Lakhs
            'technical_weight': 0.7,
            'financial_weight': 0.3,
            'experience_weight': 0.4,
            'document_compliance_weight': 0.3,
            'capacity_weight': 0.3
        }
        
    def evaluate_compliance(self, bid_data: Dict) -> Dict[str, Any]:
        """Evaluate document compliance"""
        documents = bid_data.get('documents', {})
        requirements = self.tender_requirements
        
        compliance = {
            'mandatory_present': [],
            'mandatory_missing': [],
            'compliance_score': 0,
            'details': {}
        }
        
        # Check each mandatory document
        for doc in requirements['mandatory_documents']:
            present = documents.get(doc, False)
            compliance['details'][doc] = present
            
            if present:
                compliance['mandatory_present'].append(doc)
            else:
                compliance['mandatory_missing'].append(doc)
                
        # Calculate compliance score
        total_mandatory = len(requirements['mandatory_documents'])
        if total_mandatory > 0:
            compliance['compliance_score'] = (
                len(compliance['mandatory_present']) / total_mandatory
            ) * 100
            
        return compliance
        
    def evaluate_experience(self, bid_data: Dict) -> Dict[str, Any]:
        """Evaluate experience"""
        experience = bid_data.get('experience', {})
        requirements = self.tender_requirements
        
        result = {
            'years_score': 0,
            'projects_score': 0,
            'total_score': 0,
            'details': {}
        }
        
        # Score years of experience
        years = experience.get('years', 0)
        required_years = requirements['min_experience_years']
        
        if years >= required_years:
            result['years_score'] = 100
        elif years > 0:
            result['years_score'] = (years / required_years) * 100
        else:
            result['years_score'] = 0
            
        # Score number of projects (assuming 5+ projects is excellent)
        total_projects = experience.get('total_projects', 0)
        if total_projects >= 5:
            result['projects_score'] = 100
        else:
            result['projects_score'] = (total_projects / 5) * 100
            
        # Weighted average (70% years, 30% projects)
        result['total_score'] = (
            result['years_score'] * 0.7 + 
            result['projects_score'] * 0.3
        )
        
        result['details'] = {
            'years': years,
            'required_years': required_years,
            'total_projects': total_projects
        }
        
        return result
        
    def evaluate_financial(self, bid_data: Dict) -> Dict[str, Any]:
        """Evaluate financial aspects"""
        financial = bid_data.get('financial', {})
        requirements = self.tender_requirements
        
        result = {
            'turnover_score': 0,
            'price_score': 0,
            'total_score': 0,
            'details': {}
        }
        
        # Evaluate turnover
        turnover_list = financial.get('turnover', [])
        if turnover_list:
            avg_turnover = sum(turnover_list) / len(turnover_list)
            required_turnover = requirements['min_annual_turnover']
            
            if avg_turnover >= required_turnover:
                result['turnover_score'] = 100
            else:
                result['turnover_score'] = (avg_turnover / required_turnover) * 100
                
            result['details']['avg_turnover'] = avg_turnover
        else:
            result['turnover_score'] = 0
            result['details']['avg_turnover'] = 0
            
        # Price score will be calculated relative to other bids
        result['details']['bid_amount'] = financial.get('bid_amount', 0)
        
        return result
        
    def calculate_price_score(self, bid_amount: float, all_bids: List[float]) -> float:
        """Calculate price score relative to other bids"""
        if not all_bids or bid_amount is None:
            return 50  # Default score
            
        # Remove None values
        valid_bids = [b for b in all_bids if b is not None]
        
        if not valid_bids:
            return 50
            
        lowest_bid = min(valid_bids)
        
        if bid_amount == lowest_bid:
            return 100
        else:
            # Higher price = lower score
            return (lowest_bid / bid_amount) * 100
            
    def evaluate_all_bids(self, all_bids_data: List[Dict]) -> List[Dict]:
        """Evaluate all bids and rank them"""
        evaluated_bids = []
        
        # First pass: basic evaluation
        for bid in all_bids_data:
            if 'error' in bid:
                evaluated_bids.append({
                    'filename': bid.get('filename', 'Unknown'),
                    'error': bid['error'],
                    'total_score': 0,
                    'rank': 999
                })
                continue
                
            # Evaluate each aspect
            compliance = self.evaluate_compliance(bid)
            experience = self.evaluate_experience(bid)
            financial = self.evaluate_financial(bid)
            
            # Store evaluated data
            evaluated_bid = {
                'filename': bid['filename'],
                'company_name': bid.get('company_details', {}).get('company_name', 'Unknown'),
                'compliance': compliance,
                'experience': experience,
                'financial': financial,
                'raw_data': bid
            }
            evaluated_bids.append(evaluated_bid)
            
        # Second pass: calculate price scores relative to all bids
        all_bid_amounts = [
            b['financial']['details'].get('bid_amount') 
            for b in evaluated_bids 
            if 'error' not in b
        ]
        
        for bid in evaluated_bids:
            if 'error' in bid:
                continue
                
            # Calculate price score
            bid_amount = bid['financial']['details'].get('bid_amount')
            price_score = self.calculate_price_score(bid_amount, all_bid_amounts)
            bid['financial']['price_score'] = price_score
            
            # Calculate weighted total score
            req = self.tender_requirements
            
            # Technical score (70% of total)
            technical_score = (
                bid['compliance']['compliance_score'] * req['document_compliance_weight'] +
                bid['experience']['total_score'] * req['experience_weight']
            )
            
            # Financial score (30% of total)
            financial_score = (
                bid['financial']['turnover_score'] * 0.5 +
                price_score * 0.5
            )
            
            # Final score
            bid['total_score'] = (
                technical_score * req['technical_weight'] +
                financial_score * req['financial_weight']
            )
            
            # Determine status
            if bid['compliance']['mandatory_missing']:
                bid['status'] = 'Non-Compliant'
            elif bid['total_score'] >= 80:
                bid['status'] = 'Highly Recommended'
            elif bid['total_score'] >= 60:
                bid['status'] = 'Recommended'
            else:
                bid['status'] = 'Not Recommended'
                
        # Sort by total score (descending)
        evaluated_bids.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Assign ranks
        for i, bid in enumerate(evaluated_bids, 1):
            bid['rank'] = i if 'error' not in bid else 'Error'
            
        return evaluated_bids