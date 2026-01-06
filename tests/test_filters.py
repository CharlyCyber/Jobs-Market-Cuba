import pytest
from filters.job_filter import JobFilter


class TestJobFilter:
    
    def setup_method(self):
        self.filter = JobFilter()
    
    def test_filter_matches_ai_keywords(self):
        offers = [
            {
                'title': 'Machine Learning Engineer',
                'company': 'Tech Corp',
                'description': 'Working with AI models',
                'link': 'http://example.com',
                'source': 'Test'
            }
        ]
        
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 1
    
    def test_filter_matches_design_keywords(self):
        offers = [
            {
                'title': 'Diseñador Gráfico',
                'company': 'Design Studio',
                'description': 'Crear diseños para web',
                'link': 'http://example.com',
                'source': 'Test'
            }
        ]
        
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 1
    
    def test_filter_matches_writing_keywords(self):
        offers = [
            {
                'title': 'Content Writer',
                'company': 'Media Co',
                'description': 'Redacción de artículos',
                'link': 'http://example.com',
                'source': 'Test'
            }
        ]
        
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 1
    
    def test_filter_matches_automation_keywords(self):
        offers = [
            {
                'title': 'Automation Specialist',
                'company': 'Tech Inc',
                'description': 'Building automation workflows',
                'link': 'http://example.com',
                'source': 'Test'
            }
        ]
        
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 1
    
    def test_filter_excludes_non_matching_offers(self):
        offers = [
            {
                'title': 'Accountant',
                'company': 'Finance Corp',
                'description': 'Managing financial records',
                'link': 'http://example.com',
                'source': 'Test'
            }
        ]
        
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 0
    
    def test_filter_mixed_offers(self):
        offers = [
            {
                'title': 'AI Engineer',
                'company': 'Tech',
                'description': 'AI work',
                'link': 'http://example.com',
                'source': 'Test'
            },
            {
                'title': 'Accountant',
                'company': 'Finance',
                'description': 'Finance work',
                'link': 'http://example.com',
                'source': 'Test'
            },
            {
                'title': 'Designer',
                'company': 'Studio',
                'description': 'Design work',
                'link': 'http://example.com',
                'source': 'Test'
            }
        ]
        
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 2
    
    def test_filter_empty_list(self):
        offers = []
        filtered = self.filter.filter_offers(offers)
        assert len(filtered) == 0
