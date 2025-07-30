
# vector_store.py
import chromadb
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Any, Tuple
import streamlit as st
import os
import tempfile

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "real_estate_documents"
        self.is_fitted = False
        self.embedding_model = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.persist_directory = tempfile.mkdtemp(prefix="chroma_db_")
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Real estate properties and guidelines"},
                embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
        except Exception as e:
            st.error(f"Error initializing ChromaDB: {str(e)}")
    
    def create_vector_store(self, documents: List[Dict[str, Any]]) -> bool:
        try:
            if not self.collection:
                return False
            
            try:
                existing_docs = self.collection.get()
                if existing_docs['ids']:
                    self.collection.delete(ids=existing_docs['ids'])
            except:
                pass
            
            doc_ids = []
            doc_texts = []
            doc_metadatas = []
            
            for i, doc in enumerate(documents):
                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                doc_texts.append(doc['content'])
                
                metadata = doc.get('metadata', {})
                clean_metadata = {}
                for key, value in metadata.items():
                    if value is not None:
                        clean_metadata[key] = str(value)
                clean_metadata['doc_index'] = str(i)
                doc_metadatas.append(clean_metadata)
            
            batch_size = 100
            for i in range(0, len(doc_ids), batch_size):
                end_idx = min(i + batch_size, len(doc_ids))
                self.collection.add(
                    documents=doc_texts[i:end_idx],
                    metadatas=doc_metadatas[i:end_idx],
                    ids=doc_ids[i:end_idx]
                )
            
            self.is_fitted = True
            return True
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if not self.is_fitted or not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(k, 10)
            )
            
            documents = []
            if results['documents'] and len(results['documents']) > 0:
                for doc_text, metadata, distance in zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                ):
                    similarity = max(0, 1.0 - distance)
                    doc = {
                        'content': doc_text,
                        'metadata': metadata
                    }
                    documents.append((doc, similarity))
            return documents
        except Exception as e:
            return []
    
    def extract_context_keywords(self, query: str) -> Dict[str, Any]:
        filters = {}
        query_lower = query.lower()
        
        import re
        
        price_patterns = [
            r'under ₹(\d+)([lc]r?)',
            r'below ₹(\d+)([lc]r?)',
            r'less than ₹(\d+)([lc]r?)',
            r'under (\d+)([lc]r?)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2) if len(match.groups()) > 1 else ''
                if 'l' in unit.lower():
                    amount *= 100000
                elif 'c' in unit.lower():
                    amount *= 10000000
                filters['price'] = {'min': 0, 'max': amount}
                break
        
        bhk_patterns = [r'(\d+)bhk', r'(\d+) bhk', r'(\d+)-bhk']
        for pattern in bhk_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filters['bhk'] = match.group(1)
                break
        
        locations = ['adyar', 'velachery', 'anna nagar', 'nungambakkam', 'besant nagar']
        for location in locations:
            if location in query_lower:
                filters['location'] = location
                break
        
        return filters
    
    def hybrid_search(self, query: str, filters: Dict[str, Any] = None, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        return self.similarity_search(query, k)
    
    def get_document_stats(self) -> Dict[str, Any]:
        if not self.collection:
            return {}
        
        try:
            results = self.collection.get()
            stats = {
                'total_documents': len(results['documents']) if results['documents'] else 0,
                'doc_types': {},
                'sources': {}
            }
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    doc_type = metadata.get('doc_type', 'unknown')
                    stats['doc_types'][doc_type] = stats['doc_types'].get(doc_type, 0) + 1
                    source = metadata.get('source', 'unknown')
                    stats['sources'][source] = stats['sources'].get(source, 0) + 1
            return stats
        except Exception:
            return {}
    
    def cleanup(self):
        try:
            if hasattr(self, 'persist_directory') and os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory, ignore_errors=True)
        except Exception:
            pass