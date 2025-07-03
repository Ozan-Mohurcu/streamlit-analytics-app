# utils/file_processor.py
import fitz  # PyMuPDF
import docx
import streamlit as st
from typing import Optional, Dict, Any

class FileProcessor:
    """CV dosyalarını işleyen sınıf"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']
    
    def extract_text(self, uploaded_file) -> Optional[str]:
        """
        Yüklenen dosyadan metin çıkarır
        
        Args:
            uploaded_file: Streamlit file uploader'dan gelen dosya
            
        Returns:
            str: Çıkarılan metin veya None
        """
        try:
            file_type = uploaded_file.type
            
            if file_type == "application/pdf":
                return self._extract_from_pdf(uploaded_file)
            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                              "application/msword"]:
                return self._extract_from_docx(uploaded_file)
            else:
                st.error(f"Desteklenmeyen dosya formatı: {file_type}")
                return None
                
        except Exception as e:
            st.error(f"Dosya işleme hatası: {str(e)}")
            return None
    
    def _extract_from_pdf(self, uploaded_file) -> str:
        """PDF'den metin çıkarır"""
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
            
        doc.close()
        return text.strip()
    
    def _extract_from_docx(self, uploaded_file) -> str:
        """DOCX'den metin çıkarır"""
        doc = docx.Document(uploaded_file)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            
        return text.strip()
    
    def get_file_info(self, uploaded_file) -> Dict[str, Any]:
        """
        Dosya hakkında bilgi döndürür
        
        Returns:
            dict: Dosya bilgileri
        """
        return {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'size': uploaded_file.size,
            'size_mb': round(uploaded_file.size / (1024 * 1024), 2)
        }
    
    def validate_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Dosyanın geçerli olup olmadığını kontrol eder
        
        Returns:
            dict: Doğrulama sonuçları
        """
        file_info = self.get_file_info(uploaded_file)
        errors = []
        warnings = []
        
        # Dosya boyutu kontrolü
        if file_info['size'] > 10 * 1024 * 1024:  # 10MB
            errors.append("Dosya boyutu 10MB'dan büyük olamaz")
        
        # Dosya formatı kontrolü
        if uploaded_file.type not in [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]:
            errors.append(f"Desteklenmeyen dosya formatı: {uploaded_file.type}")
        
        # Dosya boyutu uyarısı
        if file_info['size'] > 5 * 1024 * 1024:  # 5MB
            warnings.append("Büyük dosyalar işleme daha uzun sürebilir")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'file_info': file_info
        }