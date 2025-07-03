# analyzers/content_analyzer.py
import re
from typing import Dict, List, Any, Tuple
from collections import Counter

class ContentAnalyzer:
    """CV içerik kalitesi analizi yapan sınıf"""
    
    def __init__(self):
        # Güçlü action verbs
        self.strong_action_verbs = [
            'achieved', 'accelerated', 'accomplished', 'analyzed', 'architected',
            'automated', 'built', 'collaborated', 'created', 'designed', 'developed',
            'delivered', 'deployed', 'enhanced', 'established', 'executed', 'generated',
            'implemented', 'improved', 'increased', 'initiated', 'launched', 'led',
            'managed', 'optimized', 'orchestrated', 'pioneered', 'produced', 'reduced',
            'resolved', 'restructured', 'scaled', 'spearheaded', 'streamlined', 'transformed',
            'validated', 'visualized'
        ]
        
        # Zayıf ifadeler
        self.weak_phrases = [
            'responsible for', 'worked on', 'helped with', 'assisted with', 'involved in',
            'participated in', 'contributed to', 'worked with', 'familiar with', 'exposure to',
            'duties included', 'tasks included', 'handled', 'dealt with'
        ]
        
        # Impact keywords
        self.impact_keywords = [
            'increased', 'decreased', 'improved', 'reduced', 'enhanced', 'optimized',
            'accelerated', 'generated', 'saved', 'delivered', 'achieved', 'exceeded',
            'streamlined', 'automated', 'eliminated', 'minimized', 'maximized'
        ]
        
        # Quantification patterns
        self.quantification_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+[KMB]?',  # Dollar amounts
            r'\d+[KMB]\+?',  # Large numbers with K/M/B
            r'\d+x',  # Multipliers
            r'\d+:\d+',  # Ratios
            r'\d{1,3}(?:,\d{3})*',  # Comma-separated numbers
            r'\d+\.\d+[KMB]?',  # Decimal numbers
            r'\d+\s*(hours?|days?|weeks?|months?|years?)',  # Time periods
            r'\d+\s*(people|users|customers|clients|teams?)',  # Scale indicators
        ]
    
    def analyze_content_quality(self, cv_text: str, target_role: str) -> Dict[str, Any]:
        """CV içerik kalitesini kapsamlı analiz eder"""
        try:
            analysis = {
                'quantification': self._analyze_quantification(cv_text),
                'action_verbs': self._analyze_action_verbs(cv_text),
                'impact_language': self._analyze_impact_language(cv_text),
                'technical_depth': self._analyze_technical_depth(cv_text, target_role),
                'achievement_quality': self._analyze_achievements(cv_text),
                'language_quality': self._analyze_language_quality(cv_text),
                'buzzwords': self._analyze_buzzwords(cv_text),
                'consistency': self._analyze_consistency(cv_text),
                'overall_score': 0
            }
            
            # Genel içerik skorunu hesapla
            analysis['overall_score'] = self._calculate_content_score(analysis)
            
            # İçerik önerilerini generate et
            analysis['recommendations'] = self._generate_content_recommendations(analysis, target_role)
            
            return analysis
            
        except Exception as e:
            return {
                'overall_score': 50,
                'error': str(e),
                'quantification': {'score': 50, 'count': 0, 'examples': []},
                'action_verbs': {'score': 50, 'strong_verbs': [], 'weak_phrases': []},
                'impact_language': {'score': 50, 'impact_keywords': []},
                'technical_depth': {'score': 50, 'depth_level': 'Unknown'},
                'achievement_quality': {'score': 50, 'achievement_count': 0},
                'language_quality': {'score': 50},
                'buzzwords': {'score': 50, 'buzzwords': [], 'cliches': []},
                'consistency': {'score': 50},
                'recommendations': []
            }
    
    def _analyze_quantification(self, text: str) -> Dict[str, Any]:
        """Sayısal sonuçları ve metrikleri analiz eder"""
        try:
            quantified_statements = []
            
            # Tüm quantification pattern'larını bul
            for pattern in self.quantification_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Çevresel context'i al
                    start = max(0, match.start() - 80)
                    end = min(len(text), match.end() + 80)
                    context = text[start:end].strip()
                    
                    # Impact keyword'ü var mı kontrol et
                    has_impact = any(keyword in context.lower() for keyword in self.impact_keywords)
                    
                    quantified_statements.append({
                        'value': match.group(),
                        'context': context,
                        'has_impact': has_impact,
                        'pattern': pattern
                    })
            
            # Duplicate'leri temizle
            seen_contexts = set()
            unique_statements = []
            for stmt in quantified_statements:
                if stmt['context'] not in seen_contexts:
                    unique_statements.append(stmt)
                    seen_contexts.add(stmt['context'])
            
            # Scoring
            count = len(unique_statements)
            impact_count = sum(1 for stmt in unique_statements if stmt['has_impact'])
            
            base_score = min(100, count * 12)  # Her quantified statement 12 puan
            impact_bonus = impact_count * 5    # Impact keyword'ü olan +5 puan
            
            total_score = min(100, base_score + impact_bonus)
            
            # Quality assessment
            if count >= 8:
                quality = "Excellent"
            elif count >= 5:
                quality = "Good"
            elif count >= 3:
                quality = "Fair"
            else:
                quality = "Poor"
            
            return {
                'score': total_score,
                'count': count,
                'impact_count': impact_count,
                'quality': quality,
                'examples': [stmt['context'][:100] + "..." for stmt in unique_statements[:5]],
                'recommendations': self._get_quantification_recommendations(count, impact_count)
            }
        except Exception as e:
            return {
                'score': 50,
                'count': 0,
                'impact_count': 0,
                'quality': 'Error',
                'examples': [],
                'recommendations': ['Add quantified achievements with specific numbers']
            }
    
    def _analyze_action_verbs(self, text: str) -> Dict[str, Any]:
        """Action verb kullanımını analiz eder"""
        try:
            text_lower = text.lower()
            
            # Güçlü action verb'leri bul
            found_strong = []
            for verb in self.strong_action_verbs:
                if verb in text_lower:
                    count = text_lower.count(verb)
                    found_strong.extend([verb] * count)
            
            # Zayıf ifadeleri bul
            found_weak = []
            for phrase in self.weak_phrases:
                if phrase in text_lower:
                    count = text_lower.count(phrase)
                    found_weak.extend([phrase] * count)
            
            # Unique verb'leri al
            unique_strong = list(set(found_strong))
            unique_weak = list(set(found_weak))
            
            # Scoring
            strong_score = min(80, len(unique_strong) * 8)  # Her unique strong verb 8 puan
            weak_penalty = len(unique_weak) * 5  # Her weak phrase -5 puan
            
            total_score = max(0, strong_score - weak_penalty)
            
            # Variety bonus
            if len(unique_strong) >= 10:
                total_score += 20
            elif len(unique_strong) >= 6:
                total_score += 10
            
            total_score = min(100, total_score)
            
            return {
                'score': total_score,
                'strong_verbs': unique_strong,
                'weak_phrases': unique_weak,
                'strong_count': len(found_strong),
                'weak_count': len(found_weak),
                'variety_score': len(unique_strong),
                'recommendations': self._get_action_verb_recommendations(unique_strong, unique_weak)
            }
        except Exception as e:
            return {
                'score': 50,
                'strong_verbs': [],
                'weak_phrases': [],
                'strong_count': 0,
                'weak_count': 0,
                'variety_score': 0,
                'recommendations': ['Use more strong action verbs']
            }
    
    def _analyze_impact_language(self, text: str) -> Dict[str, Any]:
        """Impact ve achievement language analiz eder"""
        try:
            text_lower = text.lower()
            
            # Impact keyword'lerini bul
            found_impact = []
            for keyword in self.impact_keywords:
                if keyword in text_lower:
                    count = text_lower.count(keyword)
                    found_impact.extend([keyword] * count)
            
            # Business value keywords
            business_keywords = [
                'revenue', 'profit', 'cost', 'efficiency', 'productivity', 'performance',
                'quality', 'accuracy', 'speed', 'time', 'customer', 'user', 'satisfaction',
                'retention', 'conversion', 'roi', 'return on investment'
            ]
            
            found_business = []
            for keyword in business_keywords:
                if keyword in text_lower:
                    found_business.append(keyword)
            
            # Results-oriented phrases
            results_phrases = [
                'resulted in', 'led to', 'achieved', 'delivered', 'produced', 'generated',
                'contributed to', 'enabled', 'facilitated', 'drove'
            ]
            
            found_results = []
            for phrase in results_phrases:
                if phrase in text_lower:
                    found_results.append(phrase)
            
            # Scoring
            impact_score = min(40, len(set(found_impact)) * 5)
            business_score = min(30, len(set(found_business)) * 3)
            results_score = min(30, len(set(found_results)) * 4)
            
            total_score = impact_score + business_score + results_score
            
            return {
                'score': total_score,
                'impact_keywords': list(set(found_impact)),
                'business_keywords': list(set(found_business)),
                'results_phrases': list(set(found_results)),
                'impact_frequency': len(found_impact),
                'recommendations': self._get_impact_recommendations(total_score)
            }
        except Exception as e:
            return {
                'score': 50,
                'impact_keywords': [],
                'business_keywords': [],
                'results_phrases': [],
                'impact_frequency': 0,
                'recommendations': ['Add more impact-focused language']
            }
    
    def _analyze_technical_depth(self, text: str, role: str) -> Dict[str, Any]:
        """Technical depth ve expertise analiz eder"""
        try:
            text_lower = text.lower()
            
            # Role-specific technical indicators
            technical_indicators = self._get_technical_indicators(role)
            
            found_indicators = {}
            depth_score = 0
            
            for category, indicators in technical_indicators.items():
                found = []
                for indicator in indicators:
                    if indicator.lower() in text_lower:
                        found.append(indicator)
                
                found_indicators[category] = found
                depth_score += len(found) * 3  # Her indicator 3 puan
            
            # Methodology mentions
            methodologies = [
                'agile', 'scrum', 'waterfall', 'devops', 'ci/cd', 'test-driven',
                'data-driven', 'machine learning', 'deep learning', 'statistical modeling'
            ]
            
            found_methodologies = []
            for method in methodologies:
                if method in text_lower:
                    found_methodologies.append(method)
            
            methodology_score = len(found_methodologies) * 4
            
            # Complexity indicators
            complexity_words = [
                'complex', 'advanced', 'sophisticated', 'enterprise', 'large-scale',
                'distributed', 'real-time', 'high-performance', 'scalable'
            ]
            
            complexity_count = sum(1 for word in complexity_words if word in text_lower)
            complexity_score = min(20, complexity_count * 3)
            
            total_score = min(100, depth_score + methodology_score + complexity_score)
            
            # Determine depth level
            if total_score >= 80:
                depth_level = "Expert"
            elif total_score >= 60:
                depth_level = "Advanced"
            elif total_score >= 40:
                depth_level = "Intermediate"
            else:
                depth_level = "Basic"
            
            return {
                'score': total_score,
                'depth_level': depth_level,
                'technical_indicators': found_indicators,
                'methodologies': found_methodologies,
                'complexity_score': complexity_score,
                'recommendations': self._get_technical_depth_recommendations(total_score, role)
            }
        except Exception as e:
            return {
                'score': 50,
                'depth_level': 'Unknown',
                'technical_indicators': {},
                'methodologies': [],
                'complexity_score': 0,
                'recommendations': ['Add more technical details']
            }
    
    def _analyze_achievements(self, text: str) -> Dict[str, Any]:
        """Achievement quality analiz eder"""
        try:
            sentences = text.split('.')
            
            # Achievement indicators
            achievement_patterns = [
                r'(increased|improved|enhanced|optimized|reduced|decreased|eliminated|minimized|maximized|generated|delivered|achieved|exceeded|streamlined|automated)',
                r'(awarded|recognized|promoted|selected|chosen|honored)',
                r'(led|managed|directed|supervised|mentored|trained|coached)',
                r'(created|developed|built|designed|implemented|established|launched|initiated)'
            ]
            
            achievement_sentences = []
            for sentence in sentences:
                for pattern in achievement_patterns:
                    if re.search(pattern, sentence.lower()):
                        achievement_sentences.append(sentence)
                        break
            
            # Quality metrics
            quantified_achievements = []
            for sentence in achievement_sentences:
                has_number = bool(re.search(r'\d+', sentence))
                has_impact = any(keyword in sentence.lower() for keyword in self.impact_keywords)
                if has_number and has_impact:
                    quantified_achievements.append(sentence)
            
            # Scoring
            achievement_count = len(achievement_sentences)
            quantified_count = len(quantified_achievements)
            
            base_score = min(60, achievement_count * 6)
            quantified_bonus = quantified_count * 8
            
            total_score = min(100, base_score + quantified_bonus)
            
            return {
                'score': total_score,
                'achievement_count': achievement_count,
                'quantified_count': quantified_count,
                'quality_ratio': quantified_count / achievement_count if achievement_count > 0 else 0,
                'examples': quantified_achievements[:3],
                'recommendations': self._get_achievement_recommendations(achievement_count, quantified_count)
            }
        except Exception as e:
            return {
                'score': 50,
                'achievement_count': 0,
                'quantified_count': 0,
                'quality_ratio': 0,
                'examples': [],
                'recommendations': ['Add more achievement-focused bullet points']
            }
    
    def _analyze_language_quality(self, text: str) -> Dict[str, Any]:
        """Language quality ve professionalism analiz eder"""
        try:
            # Sentence structure analysis
            sentences = text.split('.')
            total_sentences = len(sentences)
            
            if total_sentences == 0:
                return {'score': 0, 'error': 'No sentences found'}
            
            # Average sentence length
            words = text.split()
            avg_sentence_length = len(words) / total_sentences
            
            # Vocabulary diversity
            unique_words = set(word.lower() for word in words if word.isalpha())
            vocab_diversity = len(unique_words) / len(words) if words else 0
            
            # Professional tone indicators
            professional_words = [
                'professional', 'expertise', 'experience', 'skilled', 'proficient',
                'accomplished', 'successful', 'effective', 'efficient', 'strategic',
                'innovative', 'collaborative', 'analytical', 'detail-oriented'
            ]
            
            professional_count = sum(1 for word in professional_words if word in text.lower())
            
            # Avoid informal language
            informal_words = [
                'awesome', 'cool', 'stuff', 'things', 'lots', 'tons', 'crazy',
                'super', 'really', 'very', 'pretty', 'quite', 'kinda', 'sorta'
            ]
            
            informal_count = sum(1 for word in informal_words if word in text.lower())
            
            # Scoring
            length_score = 100 if 15 <= avg_sentence_length <= 25 else max(0, 100 - abs(avg_sentence_length - 20) * 3)
            diversity_score = min(100, vocab_diversity * 200)
            professional_score = min(30, professional_count * 5)
            informal_penalty = informal_count * 10
            
            total_score = max(0, (length_score + diversity_score + professional_score - informal_penalty) / 3)
            
            return {
                'score': round(total_score, 1),
                'avg_sentence_length': round(avg_sentence_length, 1),
                'vocab_diversity': round(vocab_diversity, 3),
                'professional_count': professional_count,
                'informal_count': informal_count,
                'recommendations': self._get_language_recommendations(avg_sentence_length, vocab_diversity, informal_count)
            }
        except Exception as e:
            return {
                'score': 50,
                'error': str(e),
                'recommendations': ['Improve language quality and professionalism']
            }
    
    def _analyze_buzzwords(self, text: str) -> Dict[str, Any]:
        """Buzzword ve cliche kullanımını analiz eder"""
        try:
            text_lower = text.lower()
            
            # Overused buzzwords
            buzzwords = [
                'synergy', 'leverage', 'paradigm', 'disruptive', 'innovative', 'cutting-edge',
                'state-of-the-art', 'best-in-class', 'world-class', 'industry-leading',
                'game-changer', 'think outside the box', 'low-hanging fruit', 'move the needle',
                'hit the ground running', 'wear many hats', 'go the extra mile'
            ]
            
            found_buzzwords = []
            for buzzword in buzzwords:
                if buzzword in text_lower:
                    found_buzzwords.append(buzzword)
            
            # Cliche phrases
            cliches = [
                'team player', 'self-motivated', 'results-oriented', 'detail-oriented',
                'fast-paced environment', 'excellent communication skills', 'proven track record',
                'hands-on experience', 'go-getter', 'self-starter'
            ]
            
            found_cliches = []
            for cliche in cliches:
                if cliche in text_lower:
                    found_cliches.append(cliche)
            
            # Scoring (lower is better for buzzwords)
            buzzword_penalty = len(found_buzzwords) * 8
            cliche_penalty = len(found_cliches) * 5
            
            total_penalty = buzzword_penalty + cliche_penalty
            score = max(0, 100 - total_penalty)
            
            return {
                'score': score,
                'buzzwords': found_buzzwords,
                'cliches': found_cliches,
                'total_issues': len(found_buzzwords) + len(found_cliches),
                'recommendations': self._get_buzzword_recommendations(found_buzzwords, found_cliches)
            }
        except Exception as e:
            return {
                'score': 75,
                'buzzwords': [],
                'cliches': [],
                'total_issues': 0,
                'recommendations': []
            }
    
    def _analyze_consistency(self, text: str) -> Dict[str, Any]:
        """Tutarlılık ve formatting consistency analiz eder"""
        try:
            lines = text.split('\n')
            
            # Date format consistency
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
                r'\d{4}-\d{2}-\d{2}',      # YYYY-MM-DD
                r'\w+ \d{4}',              # Month YYYY
                r'\d{1,2}/\d{4}',          # MM/YYYY
            ]
            
            found_date_formats = []
            for pattern in date_patterns:
                if re.search(pattern, text):
                    found_date_formats.append(pattern)
            
            date_consistency = len(found_date_formats) <= 1
            
            # Bullet point consistency
            bullet_patterns = [r'•', r'-', r'\*', r'◦', r'▪']
            found_bullets = []
            for pattern in bullet_patterns:
                if re.search(f'^\\s*{pattern}', text, re.MULTILINE):
                    found_bullets.append(pattern)
            
            bullet_consistency = len(found_bullets) <= 1
            
            # Scoring
            consistency_score = 100
            if not date_consistency:
                consistency_score -= 15
            if not bullet_consistency:
                consistency_score -= 10
            
            return {
                'score': consistency_score,
                'date_consistency': date_consistency,
                'bullet_consistency': bullet_consistency,
                'found_date_formats': len(found_date_formats),
                'found_bullet_types': len(found_bullets),
                'recommendations': self._get_consistency_recommendations(date_consistency, bullet_consistency)
            }
        except Exception as e:
            return {
                'score': 75,
                'date_consistency': True,
                'bullet_consistency': True,
                'recommendations': []
            }
    
    def _get_technical_indicators(self, role: str) -> Dict[str, List[str]]:
        """Role-specific technical indicators döndürür"""
        indicators = {
            'data_scientist': {
                'algorithms': ['regression', 'classification', 'clustering', 'neural networks', 'random forest', 'gradient boosting'],
                'techniques': ['feature engineering', 'dimensionality reduction', 'cross-validation', 'hyperparameter tuning'],
                'domains': ['nlp', 'computer vision', 'time series', 'recommendation systems', 'anomaly detection'],
                'deployment': ['model deployment', 'mlops', 'api', 'docker', 'kubernetes', 'cloud platforms']
            },
            'data_analyst': {
                'analysis': ['statistical analysis', 'trend analysis', 'cohort analysis', 'funnel analysis', 'a/b testing'],
                'visualization': ['dashboard', 'reporting', 'kpi', 'metrics', 'data storytelling'],
                'tools': ['sql', 'excel', 'tableau', 'power bi', 'python', 'r'],
                'business': ['business intelligence', 'data warehouse', 'etl', 'data pipeline']
            },
            'business_analyst': {
                'analysis': ['requirements analysis', 'gap analysis', 'process mapping', 'stakeholder analysis'],
                'documentation': ['brd', 'frd', 'user stories', 'use cases', 'process flow'],
                'methodologies': ['agile', 'scrum', 'waterfall', 'lean', 'six sigma'],
                'tools': ['jira', 'confluence', 'visio', 'lucidchart', 'sharepoint']
            }
        }
        
        return indicators.get(role, {})
    
    def _get_quantification_recommendations(self, count: int, impact_count: int) -> List[str]:
        """Quantification önerileri"""
        recommendations = []
        
        if count < 3:
            recommendations.append("Add specific numbers, percentages, and metrics to your achievements")
        elif count < 5:
            recommendations.append("Include more quantified results to strengthen your impact")
        
        if impact_count < count // 2:
            recommendations.append("Connect your numbers to business impact (increased, reduced, improved)")
        
        return recommendations
    
    def _get_action_verb_recommendations(self, strong_verbs: List[str], weak_phrases: List[str]) -> List[str]:
        """Action verb önerileri"""
        recommendations = []
        
        if len(strong_verbs) < 5:
            recommendations.append("Use more strong action verbs (achieved, developed, implemented, optimized)")
        
        if weak_phrases:
            recommendations.extend([
                f"Replace '{phrase}' with stronger action verbs" for phrase in weak_phrases[:3]
            ])
        
        return recommendations
    
    def _get_impact_recommendations(self, score: int) -> List[str]:
        """Impact language önerileri"""
        recommendations = []
        
        if score < 30:
            recommendations.extend([
                "Focus on results and outcomes rather than just tasks",
                "Use impact verbs like 'increased', 'reduced', 'improved'",
                "Connect your work to business value"
            ])
        elif score < 60:
            recommendations.extend([
                "Add more business impact keywords",
                "Quantify the results of your improvements"
            ])
        
        return recommendations
    
    def _get_technical_depth_recommendations(self, score: int, role: str) -> List[str]:
        """Technical depth önerileri"""
        recommendations = []
        
        if score < 40:
            recommendations.extend([
                f"Add more technical details specific to {role} roles",
                "Include methodologies and frameworks you've used",
                "Mention complexity and scale of your projects"
            ])
        elif score < 70:
            recommendations.append("Provide more specific technical implementation details")
        
        return recommendations
    
    def _get_achievement_recommendations(self, achievement_count: int, quantified_count: int) -> List[str]:
        """Achievement önerileri"""
        recommendations = []
        
        if achievement_count < 3:
            recommendations.append("Add more achievement-focused bullet points")
        
        if quantified_count < achievement_count // 2:
            recommendations.append("Quantify more of your achievements with specific metrics")
        
        return recommendations
    
    def _get_language_recommendations(self, avg_length: float, diversity: float, informal_count: int) -> List[str]:
        """Language quality önerileri"""
        recommendations = []
        
        if avg_length < 10:
            recommendations.append("Use more detailed sentences to better describe your experience")
        elif avg_length > 30:
            recommendations.append("Break down long sentences for better readability")
        
        if diversity < 0.3:
            recommendations.append("Use more varied vocabulary to avoid repetition")
        
        if informal_count > 0:
            recommendations.append("Replace informal words with professional language")
        
        return recommendations
    
    def _get_buzzword_recommendations(self, buzzwords: List[str], cliches: List[str]) -> List[str]:
        """Buzzword önerileri"""
        recommendations = []
        
        if buzzwords:
            recommendations.append("Replace buzzwords with specific, measurable achievements")
        
        if cliches:
            recommendations.append("Avoid overused phrases - be specific about your skills")
        
        return recommendations
    
    def _get_consistency_recommendations(self, date_consistency: bool, bullet_consistency: bool) -> List[str]:
        """Consistency önerileri"""
        recommendations = []
        
        if not date_consistency:
            recommendations.append("Use consistent date format throughout CV (e.g., 'Jan 2020 - Dec 2022')")
        
        if not bullet_consistency:
            recommendations.append("Use the same bullet point style throughout (• recommended)")
        
        return recommendations
    
    def _calculate_content_score(self, analysis: Dict[str, Any]) -> float:
        """Genel içerik skorunu hesaplar"""
        try:
            weights = {
                'quantification': 0.25,
                'action_verbs': 0.20,
                'impact_language': 0.15,
                'technical_depth': 0.15,
                'achievement_quality': 0.10,
                'language_quality': 0.10,
                'buzzwords': 0.03,
                'consistency': 0.02
            }
            
            total_score = 0
            for component, weight in weights.items():
                if component in analysis and 'score' in analysis[component]:
                    total_score += analysis[component]['score'] * weight
            
            return round(total_score, 1)
        except:
            return 50.0
    
    def _generate_content_recommendations(self, analysis: Dict[str, Any], target_role: str) -> List[Dict[str, Any]]:
        """İçerik analizi sonuçlarından öneriler generate eder"""
        try:
            recommendations = []
            
            # Quantification recommendations
            if analysis['quantification']['score'] < 70:
                recommendations.append({
                    'type': 'content',
                    'category': 'quantification',
                    'priority': 'HIGH',
                    'title': 'Add Quantified Results',
                    'description': f"Only {analysis['quantification']['count']} quantified achievements found",
                    'recommendations': analysis['quantification']['recommendations'],
                    'impact': '+15-25 points',
                    'examples': [
                        "• Increased model accuracy by 15% using advanced feature engineering",
                        "• Reduced data processing time by 40% through automation",
                        "• Managed datasets with 10M+ records for predictive analytics"
                    ]
                })
            
            # Action verbs recommendations
            if analysis['action_verbs']['score'] < 70:
                recommendations.append({
                    'type': 'content',
                    'category': 'action_verbs',
                    'priority': 'HIGH',
                    'title': 'Strengthen Action Verbs',
                    'description': f"Found {len(analysis['action_verbs']['weak_phrases'])} weak phrases",
                    'recommendations': analysis['action_verbs']['recommendations'],
                    'impact': '+10-20 points',
                    'examples': [
                        "Replace 'responsible for' with 'managed', 'led', or 'executed'",
                        "Change 'worked on' to 'developed', 'built', or 'implemented'",
                        "Use 'achieved' instead of 'helped with'"
                    ]
                })
            
            # Impact language recommendations
            if analysis['impact_language']['score'] < 60:
                recommendations.append({
                    'type': 'content',
                    'category': 'impact',
                    'priority': 'MEDIUM',
                    'title': 'Focus on Business Impact',
                    'description': "Limited business impact language detected",
                    'recommendations': analysis['impact_language']['recommendations'],
                    'impact': '+8-15 points',
                    'examples': [
                        "• Delivered $50K cost savings through process optimization",
                        "• Improved customer satisfaction by 20% via data-driven insights",
                        "• Generated 15% revenue increase through predictive modeling"
                    ]
                })
            
            # Technical depth recommendations
            if analysis['technical_depth']['score'] < 60:
                recommendations.append({
                    'type': 'content',
                    'category': 'technical',
                    'priority': 'MEDIUM',
                    'title': 'Increase Technical Depth',
                    'description': f"Technical depth level: {analysis['technical_depth']['depth_level']}",
                    'recommendations': analysis['technical_depth']['recommendations'],
                    'impact': '+10-18 points',
                    'examples': self._get_technical_examples(target_role)
                })
            
            # Achievement quality recommendations
            if analysis['achievement_quality']['score'] < 70:
                recommendations.append({
                    'type': 'content',
                    'category': 'achievements',
                    'priority': 'MEDIUM',
                    'title': 'Improve Achievement Quality',
                    'description': f"Only {analysis['achievement_quality']['quantified_count']} quantified achievements",
                    'recommendations': analysis['achievement_quality']['recommendations'],
                    'impact': '+5-15 points',
                    'examples': [
                        "• Architected ML pipeline reducing training time from 6 hours to 45 minutes",
                        "• Led cross-functional team of 8 developers delivering project 2 weeks ahead of schedule",
                        "• Established data governance framework adopted across 3 business units"
                    ]
                })
            
            # Language quality recommendations
            if analysis['language_quality']['score'] < 70:
                recommendations.append({
                    'type': 'content',
                    'category': 'language',
                    'priority': 'LOW',
                    'title': 'Enhance Language Quality',
                    'description': "Language quality needs improvement",
                    'recommendations': analysis['language_quality']['recommendations'],
                    'impact': '+5-10 points'
                })
            
            # Buzzword recommendations
            if analysis['buzzwords']['score'] < 85:
                recommendations.append({
                    'type': 'content',
                    'category': 'buzzwords',
                    'priority': 'LOW',
                    'title': 'Reduce Buzzwords and Clichés',
                    'description': f"Found {analysis['buzzwords']['total_issues']} overused terms",
                    'recommendations': analysis['buzzwords']['recommendations'],
                    'impact': '+3-8 points'
                })
            
            return recommendations
        except:
            return []
    
    def _get_technical_examples(self, role: str) -> List[str]:
        """Role-specific technical examples"""
        examples = {
            'data_scientist': [
                "• Implemented ensemble methods (Random Forest, XGBoost) achieving 94% accuracy",
                "• Built end-to-end ML pipeline using Apache Airflow and Docker containers",
                "• Deployed models to production using AWS SageMaker with auto-scaling"
            ],
            'data_analyst': [
                "• Created automated ETL pipeline processing 2M+ daily transactions",
                "• Built interactive Tableau dashboards tracking 15 key business metrics",
                "• Performed statistical analysis using Python and SQL on 50GB datasets"
            ],
            'business_analyst': [
                "• Conducted stakeholder interviews across 5 departments for requirements gathering",
                "• Documented 25 user stories and acceptance criteria using Agile methodology",
                "• Facilitated cross-functional workshops leading to 30% process improvement"
            ]
        }
        
        return examples.get(role, [
            "• Add specific technical implementations and methodologies",
            "• Include scale and complexity of projects worked on",
            "• Mention tools, frameworks, and technologies used"
        ])