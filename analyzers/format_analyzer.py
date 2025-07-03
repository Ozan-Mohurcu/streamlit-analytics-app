# analyzers/format_analyzer.py
import re
import fitz  # PyMuPDF
from typing import Dict, List, Any, Optional
import streamlit as st

class FormatAnalyzer:
    """CV format ve yapı analizi yapan sınıf"""
    
    def __init__(self):
        self.ats_safe_fonts = [
            'Arial', 'Calibri', 'Times New Roman', 'Helvetica', 
            'Georgia', 'Verdana', 'Tahoma', 'Trebuchet MS',
            'Book Antiqua', 'Garamond'
        ]
        
        self.required_sections = {
            'contact': {
                'keywords': ['phone', 'email', 'linkedin', 'contact', 'mobile', 'tel'],
                'weight': 0.2,
                'critical': True
            },
            'summary': {
                'keywords': ['summary', 'objective', 'profile', 'about', 'overview'],
                'weight': 0.15,
                'critical': False
            },
            'experience': {
                'keywords': ['experience', 'employment', 'work history', 'professional experience', 'career'],
                'weight': 0.25,
                'critical': True
            },
            'skills': {
                'keywords': ['skills', 'technical skills', 'competencies', 'technologies', 'tools'],
                'weight': 0.2,
                'critical': True
            },
            'education': {
                'keywords': ['education', 'qualifications', 'academic', 'degree', 'university', 'college'],
                'weight': 0.15,
                'critical': True
            },
            'projects': {
                'keywords': ['projects', 'portfolio', 'work samples', 'key projects'],
                'weight': 0.05,
                'critical': False
            }
        }
    
    def analyze_format(self, uploaded_file, cv_text: str) -> Dict[str, Any]:
        """CV formatını kapsamlı analiz eder"""
        try:
            analysis = {
                'file_format': self._check_file_format(uploaded_file),
                'length': self._check_length(cv_text),
                'sections': self._check_sections(cv_text),
                'contact_info': self._check_contact_info(cv_text),
                'fonts': self._check_fonts(uploaded_file),
                'formatting': self._check_formatting_elements(uploaded_file, cv_text),
                'readability': self._check_readability(cv_text),
                'structure': self._check_structure(cv_text),
                'ats_compliance': 0
            }
            
            # Genel ATS uyumluluk skorunu hesapla
            analysis['ats_compliance'] = self._calculate_format_score(analysis)
            
            # Format önerilerini generate et
            analysis['recommendations'] = self._generate_format_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            return {
                'ats_compliance': 50,
                'error': str(e),
                'file_format': {'score': 50, 'status': 'Error in analysis'},
                'length': {'score': 50, 'status': 'Error in analysis'},
                'sections': {'score': 50, 'found_sections': {}, 'missing_sections': []},
                'contact_info': {'score': 50, 'details': {}},
                'fonts': {'score': 50, 'primary_font': 'Unknown'},
                'formatting': {'score': 50, 'issues': []},
                'readability': {'score': 50},
                'structure': {'score': 50},
                'recommendations': []
            }
    
    def _check_file_format(self, uploaded_file) -> Dict[str, Any]:
        """Dosya formatını kontrol eder"""
        try:
            file_type = uploaded_file.type
            file_size = uploaded_file.size
            file_name = uploaded_file.name
            
            if file_type == 'application/pdf':
                score = 100
                status = 'Excellent - PDF format is ATS-friendly'
                recommendations = []
            elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                score = 85
                status = 'Good - DOCX format (PDF preferred for better compatibility)'
                recommendations = ['Consider converting to PDF for maximum ATS compatibility']
            elif file_type == 'application/msword':
                score = 70
                status = 'Fair - Old DOC format (upgrade to DOCX or PDF)'
                recommendations = ['Convert to PDF or newer DOCX format']
            else:
                score = 0
                status = f'Poor - Unsupported format: {file_type}'
                recommendations = ['Convert to PDF or DOCX format']
            
            size_mb = file_size / (1024 * 1024)
            if size_mb > 5:
                score -= 10
                recommendations.append(f'File size ({size_mb:.1f}MB) is large - consider optimizing')
            
            return {
                'score': max(0, score),
                'file_type': file_type,
                'size_mb': round(size_mb, 2),
                'filename': file_name,
                'status': status,
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'score': 50,
                'error': str(e),
                'status': 'Error checking file format',
                'recommendations': ['Please check file format']
            }
    
    def _check_length(self, text: str) -> Dict[str, Any]:
        """CV uzunluğunu analiz eder"""
        try:
            words = text.split()
            word_count = len(words)
            estimated_pages = word_count / 250
            
            if 400 <= word_count <= 1000:
                score = 100
                status = 'Optimal length for ATS systems'
                level = 'Excellent'
            elif 300 <= word_count < 400:
                score = 80
                status = 'Slightly short - could include more details'
                level = 'Good'
            elif 1000 < word_count <= 1200:
                score = 75
                status = 'Slightly long - consider condensing'
                level = 'Good'
            elif 200 <= word_count < 300:
                score = 60
                status = 'Too short - add more relevant details'
                level = 'Needs Improvement'
            else:
                score = 30
                status = 'Length is problematic for ATS parsing'
                level = 'Poor'
            
            recommendations = []
            if word_count < 400:
                recommendations.extend([
                    'Add more specific project details',
                    'Include quantified achievements',
                    'Expand technical skills section'
                ])
            elif word_count > 1000:
                recommendations.extend([
                    'Remove outdated or irrelevant experience',
                    'Combine similar projects',
                    'Use bullet points instead of paragraphs'
                ])
            
            return {
                'score': score,
                'word_count': word_count,
                'estimated_pages': round(estimated_pages, 1),
                'status': status,
                'level': level,
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'score': 50,
                'error': str(e),
                'word_count': 0,
                'estimated_pages': 0,
                'status': 'Error checking length',
                'recommendations': []
            }
    
    def _check_sections(self, text: str) -> Dict[str, Any]:
        """CV bölümlerini kontrol eder"""
        try:
            text_lower = text.lower()
            found_sections = {}
            missing_sections = []
            section_scores = {}
            
            for section_name, section_config in self.required_sections.items():
                keywords = section_config['keywords']
                found = False
                
                for keyword in keywords:
                    patterns = [
                        rf'\b{re.escape(keyword)}\b',
                        rf'^{re.escape(keyword)}[:.]',
                        rf'\n{re.escape(keyword)}[:.]',
                        rf'\b{re.escape(keyword)}\s*\n',
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, text_lower, re.MULTILINE):
                            found = True
                            break
                    
                    if found:
                        break
                
                found_sections[section_name] = found
                
                if found:
                    section_scores[section_name] = 100
                else:
                    section_scores[section_name] = 0
                    if section_config['critical']:
                        missing_sections.append(section_name)
            
            total_weight = sum(config['weight'] for config in self.required_sections.values())
            weighted_score = sum(
                section_scores[name] * config['weight'] 
                for name, config in self.required_sections.items()
            ) / total_weight
            
            return {
                'score': round(weighted_score, 1),
                'found_sections': found_sections,
                'missing_sections': missing_sections,
                'section_scores': section_scores,
                'critical_missing': [s for s in missing_sections if self.required_sections[s]['critical']],
                'recommendations': self._generate_section_recommendations(missing_sections)
            }
        except Exception as e:
            return {
                'score': 50,
                'error': str(e),
                'found_sections': {},
                'missing_sections': [],
                'recommendations': []
            }
    
    def _check_contact_info(self, text: str) -> Dict[str, Any]:
        """İletişim bilgilerini kontrol eder"""
        try:
            contact_analysis = {
                'email': self._find_email(text),
                'phone': self._find_phone(text),
                'linkedin': self._find_linkedin(text),
                'location': self._find_location(text),
                'website': self._find_website(text)
            }
            
            found_count = sum(1 for item in contact_analysis.values() if item['found'])
            base_score = (found_count / len(contact_analysis)) * 100
            
            recommendations = []
            for item_name, item_data in contact_analysis.items():
                if not item_data['found']:
                    recommendations.append(f"Add {item_name} information")
            
            return {
                'score': round(base_score, 1),
                'details': contact_analysis,
                'found_count': found_count,
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'score': 50,
                'error': str(e),
                'details': {},
                'recommendations': ['Please check contact information']
            }
    
    def _check_fonts(self, uploaded_file) -> Dict[str, Any]:
        """Font analizi"""
        try:
            if uploaded_file.type == 'application/pdf':
                return self._analyze_pdf_fonts(uploaded_file)
            else:
                return {
                    'score': 85,
                    'primary_font': 'Unknown (DOCX format)',
                    'ats_safe': True,
                    'consistency': True,
                    'font_count': 1,
                    'recommendations': [
                        'Use Arial, Calibri, or Times New Roman',
                        'Ensure consistent font usage throughout'
                    ]
                }
        except Exception as e:
            return {
                'score': 75,
                'error': str(e),
                'primary_font': 'Unknown',
                'ats_safe': True,
                'consistency': True,
                'recommendations': ['Use standard fonts like Arial or Calibri']
            }
    
    def _analyze_pdf_fonts(self, uploaded_file) -> Dict[str, Any]:
        """PDF font detaylı analizi"""
        try:
            doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
            font_usage = {}
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                blocks = page.get_text("dict")
                
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                font_name = span.get("font", "Unknown")
                                if font_name in font_usage:
                                    font_usage[font_name] += 1
                                else:
                                    font_usage[font_name] = 1
            
            doc.close()
            
            primary_font = max(font_usage, key=font_usage.get) if font_usage else "Unknown"
            ats_safe = any(safe_font.lower() in primary_font.lower() for safe_font in self.ats_safe_fonts)
            consistency = len(font_usage) <= 2
            
            score = 100
            if not ats_safe:
                score -= 30
            if not consistency:
                score -= 20
            
            recommendations = []
            if not ats_safe:
                recommendations.append(f"Change font from {primary_font} to Arial or Calibri")
            if not consistency:
                recommendations.append("Use only one font family throughout the CV")
            
            return {
                'score': max(0, score),
                'primary_font': primary_font,
                'ats_safe': ats_safe,
                'consistency': consistency,
                'font_count': len(font_usage),
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'score': 70,
                'error': f"Font analysis error: {str(e)}",
                'primary_font': 'Unknown',
                'ats_safe': True,
                'consistency': True,
                'recommendations': ['Use Arial, Calibri, or Times New Roman fonts']
            }
    
    def _check_formatting_elements(self, uploaded_file, cv_text: str) -> Dict[str, Any]:
        """Formatting elementlerini kontrol eder"""
        try:
            issues = []
            score = 100
            
            # Metin analizi
            text_issues = self._analyze_text_formatting(cv_text)
            issues.extend(text_issues['issues'])
            score -= text_issues['penalty']
            
            recommendations = []
            for issue in issues:
                recommendations.append(self._get_formatting_recommendation(issue))
            
            return {
                'score': max(0, score),
                'issues': issues,
                'ats_friendly': score >= 80,
                'recommendations': list(set(recommendations))
            }
        except Exception as e:
            return {
                'score': 75,
                'error': str(e),
                'issues': [],
                'ats_friendly': True,
                'recommendations': []
            }
    
    def _check_readability(self, text: str) -> Dict[str, Any]:
        """Okunabilirlik analizi"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
            
            score = 100
            if avg_words_per_sentence > 25:
                score -= 10
            elif avg_words_per_sentence > 30:
                score -= 20
            
            recommendations = []
            if avg_words_per_sentence > 25:
                recommendations.append("Break long sentences into shorter ones")
            
            return {
                'score': max(0, score),
                'avg_sentence_length': round(avg_words_per_sentence, 1),
                'level': 'Good' if score >= 80 else 'Needs Improvement',
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'score': 75,
                'error': str(e),
                'recommendations': ['Ensure text is clear and well-structured']
            }
    
    def _check_structure(self, text: str) -> Dict[str, Any]:
        """CV yapısını analiz eder"""
        try:
            lines = text.split('\n')
            total_lines = len(lines)
            
            bullet_count = sum(1 for line in lines if re.match(r'^\s*[•\-\*\u2022]', line.strip()))
            bullet_percentage = (bullet_count / total_lines) * 100 if total_lines > 0 else 0
            
            numbers_count = len(re.findall(r'\d+[%\$KMB]?', text))
            
            score = 100
            if bullet_percentage < 10:
                score -= 15
            if numbers_count < 3:
                score -= 10
            
            recommendations = []
            if bullet_percentage < 15:
                recommendations.append("Use more bullet points for better readability")
            if numbers_count < 5:
                recommendations.append("Add more quantified achievements and metrics")
            
            return {
                'score': score,
                'bullet_percentage': round(bullet_percentage, 1),
                'numbers_count': numbers_count,
                'total_lines': total_lines,
                'recommendations': recommendations
            }
        except Exception as e:
            return {
                'score': 75,
                'error': str(e),
                'recommendations': []
            }
    
    def _find_email(self, text: str) -> Dict[str, Any]:
        """Email adresi bulur"""
        try:
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(pattern, text)
            
            if matches:
                return {'found': True, 'value': matches[0], 'count': len(matches)}
            return {'found': False, 'value': None, 'count': 0}
        except:
            return {'found': False, 'value': None, 'count': 0}
    
    def _find_phone(self, text: str) -> Dict[str, Any]:
        """Telefon numarası bulur"""
        try:
            patterns = [
                r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                r'\d{3}-\d{3}-\d{4}',
                r'\(\d{3}\)\s?\d{3}-\d{4}'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return {'found': True, 'value': matches[0], 'count': len(matches)}
            
            return {'found': False, 'value': None, 'count': 0}
        except:
            return {'found': False, 'value': None, 'count': 0}
    
    def _find_linkedin(self, text: str) -> Dict[str, Any]:
        """LinkedIn profili bulur"""
        try:
            patterns = [
                r'linkedin\.com/in/[A-Za-z0-9-]+',
                r'linkedin\.com/pub/[A-Za-z0-9-]+',
                r'www\.linkedin\.com/in/[A-Za-z0-9-]+'
            ]
            
            text_lower = text.lower()
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    return {'found': True, 'value': matches[0], 'count': len(matches)}
            
            return {'found': False, 'value': None, 'count': 0}
        except:
            return {'found': False, 'value': None, 'count': 0}
    
    def _find_location(self, text: str) -> Dict[str, Any]:
        """Konum bilgisi bulur"""
        try:
            patterns = [
                r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',
                r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b',
                r'\b[A-Z][a-z]+\s+\d{5}\b'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return {'found': True, 'value': matches[0], 'count': len(matches)}
            
            return {'found': False, 'value': None, 'count': 0}
        except:
            return {'found': False, 'value': None, 'count': 0}
    
    def _find_website(self, text: str) -> Dict[str, Any]:
        """Website/portfolio bulur"""
        try:
            patterns = [
                r'https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
                r'www\.[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
                r'[A-Za-z0-9.-]+\.com\b',
                r'github\.com/[A-Za-z0-9-]+',
                r'portfolio\.[A-Za-z0-9.-]+'
            ]
            
            text_lower = text.lower()
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    clean_matches = [m for m in matches if 'linkedin' not in m.lower()]
                    if clean_matches:
                        return {'found': True, 'value': clean_matches[0], 'count': len(clean_matches)}
            
            return {'found': False, 'value': None, 'count': 0}
        except:
            return {'found': False, 'value': None, 'count': 0}
    
    def _analyze_text_formatting(self, text: str) -> Dict[str, Any]:
        """Metin formatting analizi"""
        try:
            issues = []
            penalty = 0
            
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
            if caps_ratio > 0.15:
                issues.append("excessive_caps")
                penalty += 10
            
            punct_ratio = sum(1 for c in text if c in '!@#$%^&*()') / len(text) if text else 0
            if punct_ratio > 0.05:
                issues.append("excessive_punctuation")
                penalty += 5
            
            return {'issues': issues, 'penalty': penalty}
        except:
            return {'issues': [], 'penalty': 0}
    
    def _get_formatting_recommendation(self, issue: str) -> str:
        """Format sorunu için öneri döndürür"""
        recommendations = {
            'excessive_caps': 'Reduce use of ALL CAPS text',
            'excessive_punctuation': 'Remove unnecessary special characters',
            'long_paragraphs': 'Break long paragraphs into bullet points',
            'too_many_images': 'Limit images and graphics (ATS cannot parse them)',
            'complex_tables': 'Replace tables with simple text format',
            'pdf_analysis_error': 'Ensure PDF is text-based, not scanned image'
        }
        
        return recommendations.get(issue, 'Review formatting for ATS compatibility')
    
    def _generate_section_recommendations(self, missing_sections: List[str]) -> List[str]:
        """Eksik bölümler için öneriler generate eder"""
        recommendations = []
        
        section_advice = {
            'contact': 'Add contact information section with email, phone, and LinkedIn',
            'summary': 'Include a professional summary highlighting your key strengths',
            'experience': 'Add work experience section with job titles, companies, and achievements',
            'skills': 'Create a technical skills section listing relevant technologies',
            'education': 'Include education section with degrees and institutions',
            'projects': 'Consider adding a projects section to showcase your work'
        }
        
        for section in missing_sections:
            if section in section_advice:
                recommendations.append(section_advice[section])
        
        return recommendations
    
    def _calculate_format_score(self, analysis: Dict[str, Any]) -> float:
        """Genel format skorunu hesaplar"""
        try:
            weights = {
                'file_format': 0.15,
                'length': 0.15,
                'sections': 0.25,
                'contact_info': 0.15,
                'fonts': 0.10,
                'formatting': 0.10,
                'readability': 0.05,
                'structure': 0.05
            }
            
            total_score = 0
            for component, weight in weights.items():
                if component in analysis and 'score' in analysis[component]:
                    total_score += analysis[component]['score'] * weight
            
            return round(total_score, 1)
        except:
            return 50.0
    
    def _generate_format_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format analizi sonuçlarından öneriler generate eder"""
        try:
            recommendations = []
            
            if analysis['file_format']['score'] < 90:
                recommendations.append({
                    'type': 'format',
                    'category': 'file_format',
                    'priority': 'MEDIUM',
                    'title': 'Optimize File Format',
                    'description': analysis['file_format']['status'],
                    'recommendations': analysis['file_format']['recommendations'],
                    'impact': '+5-10 points'
                })
            
            if analysis['length']['score'] < 80:
                recommendations.append({
                    'type': 'format',
                    'category': 'length',
                    'priority': 'MEDIUM',
                    'title': 'Adjust CV Length',
                    'description': analysis['length']['status'],
                    'recommendations': analysis['length']['recommendations'],
                    'impact': '+10-15 points'
                })
            
            if analysis['sections']['score'] < 85:
                missing_critical = analysis['sections']['critical_missing']
                if missing_critical:
                    recommendations.append({
                        'type': 'format',
                        'category': 'sections',
                        'priority': 'HIGH',
                        'title': 'Add Missing Critical Sections',
                        'description': f"Missing {len(missing_critical)} critical sections",
                        'recommendations': analysis['sections']['recommendations'],
                        'impact': '+15-25 points'
                    })
            
            if analysis['contact_info']['score'] < 80:
                recommendations.append({
                    'type': 'format',
                    'category': 'contact',
                    'priority': 'HIGH',
                    'title': 'Complete Contact Information',
                    'description': f"Missing contact details",
                    'recommendations': analysis['contact_info']['recommendations'],
                    'impact': '+10-20 points'
                })
            
            return recommendations
        except:
            return []