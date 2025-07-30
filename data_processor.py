# data_processor.py
import pandas as pd
import PyPDF2
import re
from typing import List, Dict, Any
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def process_csv(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            df = pd.read_csv(file_path)
            return self._dataframe_to_documents(df, "CSV")
        except Exception as e:
            st.error(f"Error processing CSV: {str(e)}")
            return []
    
    def process_excel(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            all_documents = []
            with pd.ExcelFile(file_path) as excel_file:
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name)
                        documents = self._dataframe_to_documents(df, f"Excel-{sheet_name}")
                        all_documents.extend(documents)
                    except Exception as sheet_error:
                        continue
            return all_documents
        except Exception as e:
            st.error(f"Error processing Excel: {str(e)}")
            return []
    
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += f"\n--- Page {page_num + 1} ---\n" + page_text
                    except Exception:
                        continue
            
            if not text.strip():
                return []
            
            cleaned_text = self._clean_text(text)
            chunks = self._split_text_into_chunks(cleaned_text)
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    'content': chunk,
                    'metadata': {
                        'source': 'PDF',
                        'chunk_id': i,
                        'doc_type': 'guidelines'
                    }
                }
                documents.append(doc)
            return documents
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return []
    
    def _dataframe_to_documents(self, df: pd.DataFrame, source: str) -> List[Dict[str, Any]]:
        documents = []
        for index, row in df.iterrows():
            content_parts = []
            for column, value in row.items():
                if pd.notna(value):
                    content_parts.append(f"{column}: {value}")
            
            content = " | ".join(content_parts)
            metadata = {
                'source': source,
                'row_id': index,
                'doc_type': 'property'
            }
            
            common_fields = ['location', 'price', 'bhk', 'title', 'id']
            for field in common_fields:
                if field in row and pd.notna(row[field]):
                    metadata[field] = str(row[field])
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        return documents
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]₹]', '', text)
        text = re.sub(r'--- Page \d+ ---', '', text)
        return text.strip()
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk = ' '.join(chunk_words)
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks