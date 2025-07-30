import requests
import json
from typing import List, Dict, Any, Tuple
import streamlit as st
import google.generativeai as genai

class RAGPipeline:
    def __init__(self):
        self.together_api_key = "b2189aaf5e6340cba775909d8910ca68293e55157b18d140d73f18a2137bc085"
        self.gemini_api_key = "AIzaSyCurxSC2G8A277WbODZmPqT0eRZmSlvO9o"
        self.together_base_url = "https://api.together.xyz/v1/chat/completions"
        self.together_model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                self.gemini_model = None
        else:
            self.gemini_model = None
    
    def _call_together_api(self, messages: List[Dict[str, str]]) -> str:
        if not self.together_api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.together_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.together_model,
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(self.together_base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return None
                
        except Exception as e:
            return None
    
    def _call_gemini_api(self, prompt: str) -> str:
        if not self.gemini_model:
            return None
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return None
    
    def generate_response(self, query: str, vector_store) -> str:
        try:
            filters = vector_store.extract_context_keywords(query)
            
            if filters:
                relevant_docs = vector_store.hybrid_search(query, filters, k=6)
            else:
                relevant_docs = vector_store.similarity_search(query, k=6)
            
            if not relevant_docs:
                return self._handle_no_results(query)
            
            context = self._prepare_context(relevant_docs)
            response = self._generate_contextual_response(query, context, relevant_docs)
            
            return response
            
        except Exception as e:
            return f"🔧 **System Error:** I encountered an issue while processing your request: {str(e)}\n\n💡 **Try:** Rephrasing your question or uploading additional data files."
    
    def _prepare_context(self, relevant_docs: List[Tuple[Dict[str, Any], float]]) -> str:
        context_parts = []
        
        for doc, score in relevant_docs:
            content = doc['content']
            metadata = doc.get('metadata', {})
            
            if len(content) > 400:
                content = content[:400] + "..."
            
            source_type = "📊 Property Data" if metadata.get('doc_type') == 'property' else "📋 Guidelines"
            context_part = f"{source_type}: {content}"
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _generate_contextual_response(self, query: str, context: str, relevant_docs: List[Tuple[Dict[str, Any], float]]) -> str:
        enhanced_prompt = f"""You are PropertyAI, an advanced real estate assistant. Analyze the query and provide a comprehensive, well-structured response using the context provided.

**User Query:** {query}

**Available Context:**
{context}

**Instructions:**
1. Provide a clear, professional response based ONLY on the context provided
2. If listing properties, format them in a structured, easy-to-read manner with key details
3. Include relevant details like price, location, BHK, amenities where available
4. For guideline questions, provide specific, accurate information from the documents
5. Use emojis and formatting to make the response visually appealing
6. Be specific and cite the information from the context
7. If information is missing, clearly state what's not available
8. End with a helpful suggestion for follow-up questions

**Response Format:**
- Use bullet points and clear headings
- Include relevant emojis for better readability
- Provide specific numbers and details when available
- Make it professional yet conversational

**Response:**"""

        if self.together_api_key:
            messages = [
                {"role": "system", "content": "You are PropertyAI, a professional real estate assistant. Provide accurate, well-formatted responses based on the given context."},
                {"role": "user", "content": enhanced_prompt}
            ]
            
            together_response = self._call_together_api(messages)
            if together_response and len(together_response.strip()) > 50:
                return together_response
        
        if self.gemini_model:
            gemini_response = self._call_gemini_api(enhanced_prompt)
            if gemini_response and len(gemini_response.strip()) > 50:
                return gemini_response
        
        return self._enhanced_local_processing(query, relevant_docs)
    
    def _enhanced_local_processing(self, query: str, relevant_docs: List[Tuple[Dict[str, Any], float]]) -> str:
        properties = []
        guidelines = []
        
        for doc, score in relevant_docs:
            metadata = doc.get('metadata', {})
            if metadata.get('doc_type') == 'property':
                properties.append((doc, score))
            else:
                guidelines.append((doc, score))
        
        response_parts = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['property', 'flat', 'apartment', 'bhk', 'price', 'location', 'rent', 'buy']):
            if properties:
                response_parts.append("🏠 **Property Search Results**\n")
                response_parts.append("Found the following matching properties:\n")
                
                for i, (doc, score) in enumerate(properties[:4], 1):
                    content = doc['content']
                    metadata = doc.get('metadata', {})
                    
                    details = self._parse_property_details(content)
                    
                    response_parts.append(f"**🏢 Property {i}:**")
                    if details.get('title'):
                        response_parts.append(f"   📍 **{details['title']}**")
                    if details.get('price'):
                        response_parts.append(f"   💰 **Price:** {details['price']}")
                    if details.get('location'):
                        response_parts.append(f"   📍 **Location:** {details['location']}")
                    if details.get('bhk'):
                        response_parts.append(f"   🏠 **Type:** {details['bhk']}")
                    if details.get('amenities'):
                        response_parts.append(f"   🏊 **Amenities:** {details['amenities']}")
                    
                    response_parts.append(f"   ⭐ **Match Score:** {score:.1%}")
                    response_parts.append("")
                
                response_parts.append("💡 **Need more specific results?** Try adding filters like price range, location, or amenities.")
            else:
                response_parts.append("❌ **No Properties Found**")
                response_parts.append("\nI couldn't find any properties matching your criteria in the uploaded data.")
                response_parts.append("\n🔍 **Suggestions:**")
                response_parts.append("• Check if property data files are uploaded")
                response_parts.append("• Try broader search terms")
                response_parts.append("• Verify the spelling of location names")
        
        elif any(word in query_lower for word in ['rule', 'guideline', 'policy', 'regulation', 'law', 'legal', 'compliance']):
            if guidelines:
                response_parts.append("📋 **Guidelines & Regulations**\n")
                
                for i, (doc, score) in enumerate(guidelines[:3], 1):
                    content = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                    
                    response_parts.append(f"**📝 Guideline {i}:**")
                    response_parts.append(f"{content}")
                    response_parts.append(f"⭐ **Relevance:** {score:.1%}")
                    response_parts.append("")
                
                response_parts.append("📞 **Need clarification?** Ask more specific questions about particular regulations or procedures.")
            else:
                response_parts.append("❌ **No Guidelines Found**")
                response_parts.append("\nI couldn't find relevant guidelines for your query.")
                response_parts.append("\n📋 **Suggestions:**")
                response_parts.append("• Ensure PDF guideline documents are uploaded")
                response_parts.append("• Try different keywords related to your query")
                response_parts.append("• Ask about specific topics like 'construction rules' or 'noise policies'")
        

        else:
            response_parts.append(f"🔍 **Search Results for: '{query}'**\n")
            
            for i, (doc, score) in enumerate(relevant_docs[:3], 1):
                content = doc['content'][:350] + "..." if len(doc['content']) > 350 else doc['content']
                metadata = doc.get('metadata', {})
                source_type = "Property Data" if metadata.get('doc_type') == 'property' else "Guidelines"
                
                response_parts.append(f"**📊 Result {i} - {source_type}:**")
                response_parts.append(f"{content}")
                response_parts.append(f"⭐ **Relevance:** {score:.1%}")
                response_parts.append("")
        
        response_parts.append("---")
        response_parts.append("🤖 **PropertyAI Assistant** • Powered by Advanced Vector Search")
        response_parts.append("💬 **Ask me about:** Property searches, price ranges, locations, amenities, or guidelines")
        
        return "\n".join(response_parts)
    
    def _parse_property_details(self, content: str) -> Dict[str, str]:
        details = {}

        if '|' in content:
            pairs = content.split('|')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    details[key.strip().lower()] = value.strip()
        
        return details
    
    def _handle_no_results(self, query: str) -> str:
        return f"""🔍 **No Results Found**

I couldn't find any relevant information for: **"{query}"**

🤔 **This might be because:**
• The uploaded files don't contain information related to your query
• Try using different keywords or phrases
• Check if the relevant data files have been uploaded and processed

💡 **Try asking about:**
• **Properties:** "2BHK apartments under 50L", "properties in Adyar with parking"
• **Guidelines:** "construction rules", "noise policies", "building regulations"
• **Amenities:** "properties with gym", "furnished apartments", "metro nearby"

📤 **Need better results?** Upload more comprehensive property data or guideline documents."""