from typing import Dict, List, Any
import re
from collections import Counter
import hashlib

class RiskAnalyzer:
    def __init__(self):
        self.risk_flags = []
        
    def analyze_bidder_patterns(self, all_bids: List[Dict]) -> List[Dict]:
        """Analyze patterns across all bids to detect collusion"""
        flags = []
        
        # Check for identical IP addresses (if available)
        # In real system, you'd have IP data
        
        # Check for similar pricing patterns
        bid_amounts = []
        for bid in all_bids:
            if 'error' not in bid:
                amount = bid.get('raw_data', {}).get('financial', {}).get('bid_amount')
                if amount:
                    bid_amounts.append({
                        'filename': bid['filename'],
                        'amount': amount
                    })
                    
        # Check for round number bidding (possible collusion indicator)
        for bid_data in bid_amounts:
            amount = bid_data['amount']
            if amount and amount % 100000 == 0:  # Round to lakhs
                flags.append({
                    'bidder': bid_data['filename'],
                    'risk_type': 'Suspicious Pricing Pattern',
                    'description': 'Bid amount is a round number - possible collusion indicator',
                    'severity': 'Medium'
                })
                
        # Check for identical document hashes (same file submitted)
        # In real system, you'd compute file hashes
        
        return flags
        
    def detect_anomalies(self, bid_data: Dict, all_bids: List[Dict]) -> List[Dict]:
        """Detect anomalies in individual bids"""
        flags = []
        
        if 'error' in bid_data:
            return flags
            
        financial = bid_data.get('financial', {})
        bid_amount = financial.get('details', {}).get('bid_amount')
        
        if bid_amount:
            # Check for extremely low bid (possible lowballing)
            all_amounts = [
                b.get('financial', {}).get('details', {}).get('bid_amount')
                for b in all_bids
                if 'error' not in b and b.get('financial', {}).get('details', {}).get('bid_amount')
            ]
            
            if all_amounts and len(all_amounts) > 1:
                avg_amount = sum(all_amounts) / len(all_amounts)
                
                if bid_amount < avg_amount * 0.7:  # 30% below average
                    flags.append({
                        'bidder': bid_data['filename'],
                        'risk_type': 'Abnormally Low Bid',
                        'description': f'Bid is {(1 - bid_amount/avg_amount)*100:.1f}% below average',
                        'severity': 'High'
                    })
                elif bid_amount > avg_amount * 1.5:  # 50% above average
                    flags.append({
                        'bidder': bid_data['filename'],
                        'risk_type': 'Abnormally High Bid',
                        'description': f'Bid is {(bid_amount/avg_amount - 1)*100:.1f}% above average',
                        'severity': 'Medium'
                    })
                    
        # Check for missing mandatory documents
        compliance = bid_data.get('compliance', {})
        missing = compliance.get('mandatory_missing', [])
        if missing:
            flags.append({
                'bidder': bid_data['filename'],
                'risk_type': 'Missing Documents',
                'description': f'Missing: {", ".join(missing)}',
                'severity': 'High'
            })
            
        # Check for low experience
        experience = bid_data.get('experience', {})
        years = experience.get('details', {}).get('years', 0)
        if years < 2:
            flags.append({
                'bidder': bid_data['filename'],
                'risk_type': 'Insufficient Experience',
                'description': f'Only {years} years of experience',
                'severity': 'Medium'
            })
            
        return flags
        
    def analyze_all_risks(self, evaluated_bids: List[Dict]) -> Dict[str, Any]:
        """Complete risk analysis for all bids"""
        risk_report = {
            'individual_flags': [],
            'collusion_flags': [],
            'summary': {
                'total_flags': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0
            }
        }
        
        # Analyze individual bids
        for bid in evaluated_bids:
            if 'error' not in bid:
                flags = self.detect_anomalies(bid, evaluated_bids)
                for flag in flags:
                    risk_report['individual_flags'].append(flag)
                    risk_report['summary']['total_flags'] += 1
                    
                    severity = flag.get('severity', 'Low')
                    if severity == 'High':
                        risk_report['summary']['high_severity'] += 1
                    elif severity == 'Medium':
                        risk_report['summary']['medium_severity'] += 1
                    else:
                        risk_report['summary']['low_severity'] += 1
                        
        # Analyze patterns across bids
        collusion_flags = self.analyze_bidder_patterns(evaluated_bids)
        for flag in collusion_flags:
            risk_report['collusion_flags'].append(flag)
            risk_report['summary']['total_flags'] += 1
            
        return risk_report