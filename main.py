import streamlit as st
import pandas as pd
import os
from pathlib import Path
import time
from data_processor import DataProcessor
from vector_store import VectorStore
from rag_pipeline import RAGPipeline
import json

st.set_page_config(
    page_title="PropertyAI - Real Estate Assistant",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = VectorStore()
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = RAGPipeline()
    if 'files_processed' not in st.session_state:
        st.session_state.files_processed = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 3rem 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 25px 45px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: rotate 10s linear infinite;
        z-index: 0;
    }
    
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        color: white;
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.4rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
        text-shadow: 1px 1px 10px rgba(0,0,0,0.2);
    }
    
    .glass-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    .feature-showcase {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-15px) scale(1.05);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
        background: rgba(255, 255, 255, 0.3);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 0 20px rgba(255,255,255,0.5));
    }
    
    .feature-title {
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 10px rgba(0,0,0,0.3);
    }
    
    .feature-desc {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        line-height: 1.6;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.2);
    }
    
    .welcome-hero {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        padding: 4rem 3rem;
        text-align: center;
        margin: 3rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-hero::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
        50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.7; }
    }
    
    .welcome-icon {
        font-size: 6rem;
        margin-bottom: 2rem;
        filter: drop-shadow(0 0 30px rgba(255,255,255,0.6));
        position: relative;
        z-index: 1;
    }
    
    .welcome-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 15px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .welcome-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.3rem;
        font-weight: 400;
        margin-bottom: 3rem;
        line-height: 1.8;
        position: relative;
        z-index: 1;
        text-shadow: 1px 1px 8px rgba(0,0,0,0.2);
    }
    
    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin-top: 3rem;
    }
    
    .step-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .step-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .step-number {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.5rem;
        margin: 0 auto 1.5rem auto;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    .step-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 8px rgba(0,0,0,0.3);
    }
    
    .step-desc {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        line-height: 1.5;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.2);
    }
    
    .chat-interface {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 25px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    .chat-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .chat-title {
        color: #2d3748;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .chat-subtitle {
        color: #718096;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .sample-questions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .sample-question-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1rem;
        font-weight: 500;
        text-align: left;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .sample-question-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .sample-question-btn:hover::before {
        left: 100%;
    }
    
    .sample-question-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .sidebar-glass {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    }
    
    .status-indicator {
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .status-success {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
        box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #ed8936, #dd6b20);
        color: white;
        box-shadow: 0 8px 25px rgba(237, 137, 54, 0.3);
    }
    
    .status-processing {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        color: white;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.3);
    }
    
    .upload-zone {
        border: 3px dashed rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: white;
    }
    
    .upload-zone:hover {
        border-color: rgba(255, 255, 255, 0.8);
        background: rgba(255, 255, 255, 0.15);
        transform: scale(1.02);
    }
    
    .file-item {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        font-size: 0.9rem;
    }
    
    .progress-container {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stChatMessage {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 15px !important;
        margin: 1rem 0 !important;
        padding: 1.5rem !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1) !important;
        color: #000000 !important;
    }
    
    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span,
    .stChatMessage .markdown-text-container,
    .stChatMessage .stMarkdown,
    .stChatMessage .stMarkdown > div,
    .stChatMessage .stMarkdown > div > div,
    .stChatMessage .stMarkdown p {
        color: #000000 !important;
    }
    
    .stChatMessage[data-testid="user-message"],
    .stChatMessage[data-testid="user-message"] *,
    .stChatMessage[data-testid="user-message"] p,
    .stChatMessage[data-testid="user-message"] div {
        color: #000000 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"],
    .stChatMessage[data-testid="assistant-message"] *,
    .stChatMessage[data-testid="assistant-message"] p,
    .stChatMessage[data-testid="assistant-message"] div {
        color: #000000 !important;
    }
    
    .stChatInput > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 25px !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    
    .stChatInput textarea,
    .stChatInput input,
    .stChatInput > div > div > textarea,
    .stChatInput > div > div > input,
    .stChatInput textarea::placeholder,
    .stChatInput input::placeholder {
        color: #000000 !important;
        background: transparent !important;
    }
    
    .stChatInput textarea:focus,
    .stChatInput input:focus {
        color: #000000 !important;
        background: transparent !important;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4ecdc4;
        text-shadow: 0 0 20px rgba(78, 205, 196, 0.5);
    }
    
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    .spinning {
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        100% { transform: rotate(360deg); }
    }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2.5rem; }
        .welcome-title { font-size: 2.5rem; }
        .chat-title { font-size: 2rem; }
        .feature-showcase { grid-template-columns: 1fr; }
        .sample-questions-grid { grid-template-columns: 1fr; }
        .steps-grid { grid-template-columns: 1fr; }
    }
    </style>
    """, unsafe_allow_html=True)

def process_uploaded_files(uploaded_files):
    if not uploaded_files:
        return False
    
    st.session_state.processing = True
    
    progress_container = st.empty()
    
    with progress_container.container():
        st.markdown("""
        <div class="progress-container">
            <div style="font-size: 1.5rem; margin-bottom: 1rem;">
                <span class="spinning">⚙️</span> Processing Your Files...
            </div>
            <div>Please wait while we analyze and index your documents</div>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    all_documents = []
    total_files = len(uploaded_files)
    
    for i, uploaded_file in enumerate(uploaded_files):
        progress = (i + 1) / total_files
        status_text.text(f"📄 Processing {uploaded_file.name}...")
        progress_bar.progress(progress * 0.7)
        
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        import tempfile
        import uuid
        temp_dir = tempfile.gettempdir()
        safe_filename = f"rag_temp_{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
        temp_path = os.path.join(temp_dir, safe_filename)
        
        try:
            file_content = uploaded_file.read()
            uploaded_file.seek(0)
            
            with open(temp_path, "wb") as f:
                f.write(file_content)
            
            if file_extension in ['.csv']:
                documents = st.session_state.data_processor.process_csv(temp_path)
            elif file_extension in ['.xlsx', '.xls']:
                documents = st.session_state.data_processor.process_excel(temp_path)
            elif file_extension == '.pdf':
                documents = st.session_state.data_processor.process_pdf(temp_path)
            else:
                st.error(f"❌ Unsupported file format: {file_extension}")
                continue
            
            all_documents.extend(documents)
            
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
    
    if all_documents:
        status_text.text("🧠 Creating intelligent vector embeddings...")
        progress_bar.progress(0.9)
        
        success = st.session_state.vector_store.create_vector_store(all_documents)
        
        if success:
            progress_bar.progress(1.0)
            status_text.text("✅ Processing complete! Ready for queries.")
            time.sleep(2)
            st.session_state.processing = False
            progress_container.empty()
            return True
    
    st.session_state.processing = False
    progress_container.empty()
    return False

def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>🏠 PropertyAI Assistant</h1>
        <p>Advanced Real Estate Intelligence • Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

def render_features():
    st.markdown("""
    <div class="feature-showcase">
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI-Powered Analysis</div>
            <div class="feature-desc">Advanced natural language processing for intelligent property search and analysis</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Multi-Format Processing</div>
            <div class="feature-desc">Seamlessly process CSV, Excel, and PDF documents with automatic data extraction</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Lightning Speed</div>
            <div class="feature-desc">Vector-based search technology for instant results and real-time recommendations</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Filtering</div>
            <div class="feature-desc">Automatic extraction of price ranges, locations, and amenity preferences</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_welcome_screen():
    st.markdown("""
    <div class="welcome-hero">
        <div class="welcome-icon">🚀</div>
        <div class="welcome-title">Welcome to the Future</div>
        <div class="welcome-subtitle">
            Transform your real estate data into actionable insights with our cutting-edge AI assistant.
            Upload your property listings and policy documents to unlock intelligent search capabilities.
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sample_questions():
    sample_questions = [
        "🏠 Which 2BHK properties under ₹80L have parking facilities?",
        "📋 What are the construction rules for buildings near rivers?",
        "🏢 Show me furnished apartments with gym access in Adyar",
        "🚇 List properties within 1km of metro stations under ₹1Cr",
        "🔊 What are the noise control guidelines for residential areas?",
        "🌳 Find 3BHK villas with gardens in premium locations"
    ]
    
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">💡 Try These Smart Queries</div>
        <div class="chat-subtitle">Click any question below to see PropertyAI in action</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sample-questions-grid">', unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, question in enumerate(sample_questions):
        with cols[i % 2]:
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                clean_question = question[2:]
                st.session_state.chat_history.append({"role": "user", "content": clean_question})
                
                with st.spinner("🧠 Analyzing your query..."):
                    try:
                        response = st.session_state.rag_pipeline.generate_response(
                            clean_question, 
                            st.session_state.vector_store
                        )
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"I encountered an error: {str(e)}"
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-glass">', unsafe_allow_html=True)
        
        together_key = "b2189aaf5e6340cba775909d8910ca68293e55157b18d140d73f18a2137bc085"
        gemini_key = "AIzaSyCurxSC2G8A277WbODZmPqT0eRZmSlvO9o"
        
        if together_key:
            st.markdown('<div class="status-indicator status-success">✅ Together AI Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-warning">⚠️ Together AI Disconnected</div>', unsafe_allow_html=True)
            
        if gemini_key:
            st.markdown('<div class="status-indicator status-success">✅ Gemini AI Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-warning">⚠️ Gemini AI Disconnected</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📁 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose your files",
            type=['csv', 'xlsx', 'xls', 'pdf'],
            accept_multiple_files=True,
            help="Upload property data (CSV/Excel) and guidelines (PDF)",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown("#### 📋 Selected Files")
            for file in uploaded_files:
                file_size = len(file.read()) / 1024
                file.seek(0)
                file_icons = {"csv": "📊", "xlsx": "📈", "xls": "📈", "pdf": "📄"}
                icon = file_icons.get(file.name.split('.')[-1].lower(), "📁")
                st.markdown(f'<div class="file-item">{icon} {file.name} • {file_size:.1f} KB</div>', 
                          unsafe_allow_html=True)
        
        if uploaded_files and not st.session_state.processing:
            if st.button("🚀 Process Files", type="primary", use_container_width=True):
                if process_uploaded_files(uploaded_files):
                    st.session_state.files_processed = True
                    st.rerun()
        
        if st.session_state.processing:
            st.markdown("""
            <div class="status-indicator status-processing">
                <span class="spinning">⚙️</span> Processing Files...
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.files_processed and not st.session_state.processing:
            st.markdown("""
            <div class="status-indicator status-success">
                ✅ Ready for Intelligent Queries!
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 Document Statistics")
        
        if st.session_state.files_processed:
            try:
                stats = st.session_state.vector_store.get_document_stats()
                st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('total_documents', 0)}</div>
                    <div class="metric-label">Total Documents</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('doc_types', {}).get('property', 0)}</div>
                    <div class="metric-label">Properties</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('doc_types', {}).get('guidelines', 0)}</div>
                    <div class="metric-label">Guidelines</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            except:
                pass
        else:
            st.markdown("""
            <div class="upload-zone">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📤</div>
                <div style="font-weight: 600;">Upload files to see statistics</div>
                <div style="opacity: 0.8; margin-top: 0.5rem;">CSV • Excel • PDF</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    inject_custom_css()
    initialize_session_state()
    
    render_header()
    render_sidebar()
    
    if not st.session_state.files_processed:
        render_features()
        render_welcome_screen()
    else:
        st.markdown('<div class="chat-interface">', unsafe_allow_html=True)
        
        render_sample_questions()
        
        st.markdown("---")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        user_question = st.chat_input(
            "💭 Ask me anything about your properties or guidelines...",
            key="chat_input"
        )
        
        if user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            with st.chat_message("assistant"):
                with st.spinner("🧠 Analyzing your query with AI..."):
                    try:
                        response = st.session_state.rag_pipeline.generate_response(
                            user_question, 
                            st.session_state.vector_store
                        )
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()