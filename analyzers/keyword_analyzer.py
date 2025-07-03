# analyzers/keyword_analyzer.py
import json
import re
from typing import Dict, List, Any
from pathlib import Path

class KeywordAnalyzer:
    """Akıllı anahtar kelime analizi yapan sınıf"""
    
    def __init__(self):
        self.data_path = Path("data/keywords")
        self.role_data = {}
        self._load_role_data()
    
    def _load_role_data(self):
        """Role-specific keyword verilerini yükler"""
        role_files = {
            'data_scientist': 'data_scientist.json',
            'data_analyst': 'data_analyst.json', 
            'business_analyst': 'business_analyst.json'
        }
        
        for role, filename in role_files.items():
            try:
                file_path = self.data_path / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.role_data[role] = json.load(f)
                else:
                    print(f"Uyarı: {filename} dosyası bulunamadı")
            except Exception as e:
                print(f"Hata: {filename} yüklenirken hata: {e}")
    
    def analyze_keywords(self, cv_text: str, target_role: str) -> Dict[str, Any]:
        """CV metninde akıllı anahtar kelime analizi yapar"""
        
        if target_role not in self.role_data:
            return {
                'error': f"Desteklenmeyen rol: {target_role}",
                'total_score': 0
            }
        
        role_config = self.role_data[target_role]
        cv_text_lower = cv_text.lower()
        
        # Skill kategorilerini analiz et
        category_results = {}
        category_scores = {}
        found_keywords = {}
        missing_keywords = {}
        
        for category, config in role_config['critical_skills'].items():
            result = self._analyze_category(cv_text_lower, config)
            category_results[category] = result
            category_scores[category] = result['score']
            found_keywords[category] = result['total_found']
            missing_keywords[category] = result['missing_core'] + result['missing_bonus'][:3]  # Sadece ilk 3 bonus
        
        # Toplam skoru hesapla
        total_score = self._calculate_total_score(category_results, role_config)
        
        # Experience keywords analizi
        experience_analysis = self._analyze_experience_keywords(
            cv_text_lower, role_config.get('experience_keywords', [])
        )
        
        # Impact metrics analizi
        impact_analysis = self._analyze_impact_metrics(
            cv_text_lower, role_config.get('impact_metrics', [])
        )
        
        return {
            'total_score': round(total_score, 1),
            'category_scores': category_scores,
            'category_results': category_results,
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'experience_analysis': experience_analysis,
            'impact_analysis': impact_analysis,
            'recommendations': self._generate_smart_recommendations(
                category_results, target_role
            )
        }
    
    def _analyze_category(self, cv_text_lower: str, category_config: Dict) -> Dict[str, Any]:
        """Kategori skorunu yeni akıllı mantıkla hesapla"""
        
        core_keywords = category_config.get('core_keywords', [])
        bonus_keywords = category_config.get('bonus_keywords', [])
        minimum_required = category_config.get('minimum_required', 1)
        importance = category_config.get('category_importance', 'medium')
        
        # Core keywords'leri bul
        found_core = []
        for keyword in core_keywords:
            if self._keyword_exists(cv_text_lower, keyword):
                found_core.append(keyword)
        
        # Bonus keywords'leri bul
        found_bonus = []
        for keyword in bonus_keywords:
            if self._keyword_exists(cv_text_lower, keyword):
                found_bonus.append(keyword)
        
        # Akıllı skor hesaplama
        core_ratio = len(found_core) / len(core_keywords) if core_keywords else 0
        bonus_ratio = len(found_bonus) / len(bonus_keywords) if bonus_keywords else 0
        
        # Base score calculation
        core_score = core_ratio * 70  # Core skills = 70% max
        bonus_score = min(bonus_ratio * 30, 30)  # Bonus skills = 30% max
        
        base_score = core_score + bonus_score
        
        # Minimum requirement kontrolü
        meets_minimum = len(found_core) >= minimum_required
        if not meets_minimum:
            base_score *= 0.5  # %50 ceza if minimum not met
        
        # Excellence bonus (eğer core'un %80+'ı varsa)
        if core_ratio >= 0.8:
            base_score *= 1.1  # %10 bonus for excellence
        
        # Category importance adjustment
        importance_multiplier = {
            'high': 1.0,
            'medium': 1.0,
            'low': 1.0  # Önem seviyesi score'u etkilemez, sadece recommendations'da
        }
        
        final_score = min(100, base_score * importance_multiplier.get(importance, 1.0))
        
        return {
            'score': round(final_score, 1),
            'found_core': found_core,
            'found_bonus': found_bonus,
            'missing_core': [k for k in core_keywords if k not in found_core],
            'missing_bonus': [k for k in bonus_keywords if k not in found_bonus],
            'total_found': found_core + found_bonus,
            'meets_minimum': meets_minimum,
            'core_ratio': core_ratio,
            'bonus_ratio': bonus_ratio,
            'importance': importance
        }
    
    def _keyword_exists(self, text: str, keyword: str) -> bool:
        """Anahtar kelimenin metinde var olup olmadığını kontrol eder"""
        keyword_lower = keyword.lower()
        
        # Direkt eşleşme
        if keyword_lower in text:
            return True
        
        # Variation kontrolü
        variations = self._get_keyword_variations(keyword_lower)
        for variation in variations:
            if variation in text:
                return True
        
        return False
    
    def _get_keyword_variations(self, keyword: str) -> List[str]:
        """Anahtar kelimenin çeşitli varyasyonlarını döndürür"""
        variations = [keyword]
        
        # Yaygın varyasyonlar
        variation_map = {
            'power bi': ['powerbi', 'power-bi', 'microsoft power bi'],
            'tableau': ['tableau desktop', 'tableau server'],
            'excel': ['microsoft excel', 'ms excel', 'excel vba'],
            'sql': ['mysql', 'postgresql', 'sql server', 't-sql'],
            'python': ['python3', 'python 3'],
            'r': ['r programming', 'r language', 'r-programming'],
            'data cleaning': ['data cleansing', 'data preprocessing'],
            'data visualization': ['data viz', 'dataviz'],
            'business intelligence': ['bi', 'business-intelligence'],
            'etl': ['extract transform load', 'extract-transform-load'],
            'kpi': ['key performance indicator', 'key performance indicators'],
            'dashboard': ['dashboards', 'interactive dashboard']
        }
        
        if keyword in variation_map:
            variations.extend(variation_map[keyword])
        
        # Dash ve underscore varyasyonları
        if '-' in keyword:
            variations.append(keyword.replace('-', ' '))
            variations.append(keyword.replace('-', '_'))
        
        if '_' in keyword:
            variations.append(keyword.replace('_', ' '))
            variations.append(keyword.replace('_', '-'))
        
        return variations
    
    def _calculate_total_score(self, category_results: Dict[str, Dict], role_config: Dict[str, Any]) -> float:
        """Kategori sonuçlarından toplam skoru hesaplar"""
        total_score = 0
        total_weight = 0
        
        for category, result in category_results.items():
            if category in role_config['critical_skills']:
                weight = role_config['critical_skills'][category]['weight']
                score = result['score']
                
                total_score += score * weight
                total_weight += weight
        
        # Normalize score
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0
        
        return normalized_score
    
    def _analyze_experience_keywords(self, text: str, keywords: List[str]) -> Dict[str, Any]:
        """Experience keywords analizi"""
        found_keywords = []
        
        for keyword in keywords:
            if self._keyword_exists(text, keyword):
                found_keywords.append(keyword)
        
        # Experience için daha yumuşak puanlama
        score = min(100, len(found_keywords) * 8)  # Her keyword 8 puan
        
        return {
            'score': score,
            'found': found_keywords,
            'missing': [kw for kw in keywords if kw not in found_keywords][:5]
        }
    
    def _analyze_impact_metrics(self, text: str, metrics: List[str]) -> Dict[str, Any]:
        """Impact metrics analizi"""
        found_metrics = []
        
        for metric in metrics:
            if self._keyword_exists(text, metric):
                found_metrics.append(metric)
        
        # Sayısal değerlerin varlığını kontrol et
        number_patterns = [
            r'\d+%', r'\$\d+', r'\d+[KMB]', r'\d+x', r'\d+:\d+', r'\d{1,3}(?:,\d{3})*'
        ]
        
        quantified_results = 0
        for pattern in number_patterns:
            quantified_results += len(re.findall(pattern, text))
        
        # Impact için balanced puanlama
        metric_score = min(60, len(found_metrics) * 10)  # Metrics = 60% max
        quantified_score = min(40, quantified_results * 5)  # Numbers = 40% max
        
        total_score = metric_score + quantified_score
        
        return {
            'score': min(100, total_score),
            'found_metrics': found_metrics,
            'quantified_results': quantified_results
        }
    
    def _generate_smart_recommendations(self, category_results: Dict[str, Dict], target_role: str) -> List[Dict[str, Any]]:
        """Akıllı öneriler generate eder"""
        recommendations = []
        
        # Kategorileri önem ve skorlarına göre sırala
        sorted_categories = sorted(
            category_results.items(), 
            key=lambda x: (x[1]['importance'] == 'high', -x[1]['score'])
        )
        
        for category, result in sorted_categories:
            score = result['score']
            importance = result['importance']
            meets_minimum = result['meets_minimum']
            missing_core = result['missing_core']
            missing_bonus = result['missing_bonus']
            
            # High priority: Minimum requirement karşılanmadı
            if not meets_minimum and importance in ['high', 'medium']:
                recommendations.append({
                    'type': 'keyword',
                    'category': category,
                    'priority': 'HIGH',
                    'title': f"{category.replace('_', ' ').title()} - Temel Yetenekler Eksik",
                    'description': f"Bu kategoride minimum gereksinimler karşılanmıyor",
                    'recommendations': [
                        f"Bu temel yeteneklerden en az birini ekleyin: {', '.join(missing_core[:3])}",
                        f"CV'nizde bu yetenekleri kullandığınız projeleri belirtin",
                        f"Örnek: 'SQL kullanarak veri analizi yaptım' gibi açık ifadeler ekleyin"
                    ],
                    'impact': '+20-30 puan',
                    'examples': self._generate_usage_examples(missing_core[:2], category, target_role)
                })
            
            # Medium priority: Düşük skor ama minimum karşılanmış
            elif score < 60 and meets_minimum:
                recommendations.append({
                    'type': 'keyword',
                    'category': category,
                    'priority': 'MEDIUM',
                    'title': f"{category.replace('_', ' ').title()} Yeteneklerini Güçlendirin",
                    'description': f"Bu alanda ek yetenekler competitive advantage sağlar",
                    'recommendations': [
                        f"Bu ek yetenekleri değerlendirin: {', '.join(missing_bonus[:3])}",
                        f"Mevcut {category} projelerinizi daha detaylandırın",
                        f"Sertifikasyon veya kurs alarak bu alandaki bilginizi güçlendirin"
                    ],
                    'impact': '+10-15 puan',
                    'examples': self._generate_usage_examples(missing_bonus[:2], category, target_role)
                })
            
            # Low priority: İyi skor ama mükemmelleştirilebilir
            elif score >= 60 and score < 85 and missing_bonus:
                recommendations.append({
                    'type': 'keyword',
                    'category': category,
                    'priority': 'LOW',
                    'title': f"{category.replace('_', ' ').title()} - İleri Seviye İyileştirmeler",
                    'description': f"İyi seviyede, ileri seviye eklentilerle mükemmelleştirilebilir",
                    'recommendations': [
                        f"Bu advanced yetenekleri araştırın: {', '.join(missing_bonus[:2])}",
                        f"Industry trends'e göre bu araçları öğrenmeyi düşünün"
                    ],
                    'impact': '+5-10 puan'
                })
        
        return recommendations[:5]  # En fazla 5 öneri
    
    def _generate_usage_examples(self, keywords: List[str], category: str, role: str) -> List[str]:
        """Keyword kullanım örnekleri generate eder"""
        examples = []
        
        example_templates = {
            'data_analyst': {
                'programming': "• {keyword} kullanarak müşteri davranış analizi yaparak %15 satış artışı sağladım",
                'analytics_tools': "• {keyword} ile interaktif dashboard oluşturarak raporlama sürecini %40 hızlandırdım",
                'databases': "• {keyword} veritabanından günlük 100K+ kayıt analiz ederek KPI raporları hazırladım",
                'statistical_analysis': "• {keyword} metoduyla A/B test sonuçlarını değerlendirerek %12 conversion artışı sağladım",
                'data_processing': "• {keyword} süreçleriyle veri kalitesini %95'e çıkararak analiz güvenilirliğini artırdım",
                'business_intelligence': "• {keyword} çözümleriyle executive seviyede raporlar hazırlayarak karar süreçlerini destekledim"
            }
        }
        
        templates = example_templates.get(role, {}).get(category, {})
        
        for keyword in keywords:
            if templates:
                if isinstance(templates, dict):
                    template = templates.get(keyword, "• {keyword} kullanarak veri analizi projelerinde başarılı sonuçlar elde ettim")
                else:
                    template = templates
                
                examples.append(template.format(keyword=keyword))
        
        return examples