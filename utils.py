import streamlit as st
import time
import json
import base64
import os
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_animated_progress(steps: List[str], current_step: int = 0):
    progress_html = f"""
    <div class="animated-progress">
        <div class="progress-container">
            <div class="progress-bar-animated">
                <div class="progress-fill-animated" style="width: {(current_step + 1) / len(steps) * 100}%"></div>
            </div>
        </div>
        <div class="progress-steps">
    """
    
    for i, step in enumerate(steps):
        status = "completed" if i < current_step else "active" if i == current_step else "pending"
        icon = "✓" if i < current_step else "⟳" if i == current_step else "○"
        
        progress_html += f"""
            <div class="progress-step {status}">
                <div class="step-icon">{icon}</div>
                <div class="step-text">{step}</div>
            </div>
        """
    
    progress_html += """
        </div>
    </div>
    <style>
    .animated-progress {
        margin: 2rem 0;
        padding: 1.5rem;
        background: var(--dark-card);
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    .progress-container {
        margin-bottom: 1.5rem;
    }
    
    .progress-bar-animated {
        background: var(--border-color);
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-fill-animated {
        background: var(--primary-gradient);
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        min-width: 120px;
    }
    
    .step-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .progress-step.completed .step-icon {
        background: var(--success-gradient);
        color: white;
    }
    
    .progress-step.active .step-icon {
        background: var(--primary-gradient);
        color: white;
        animation: spin 2s linear infinite;
    }
    
    .progress-step.pending .step-icon {
        background: var(--border-color);
        color: var(--text-secondary);
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .step-text {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    .progress-step.completed .step-text {
        color: var(--text-primary);
    }
    
    .progress-step.active .step-text {
        color: var(--text-primary);
        font-weight: 600;
    }
    </style>
    """
    
    return progress_html

def create_file_preview_card(filename: str, file_type: str, file_size: int, status: str = "ready"):
    size_mb = file_size / (1024 * 1024)
    
    icons = {
        'csv': 'fa-file-csv',
        'xlsx': 'fa-file-excel', 
        'xls': 'fa-file-excel',
        'pdf': 'fa-file-pdf',
        'txt': 'fa-file-alt'
    }
    
    colors = {
        'csv': '#28a745',
        'xlsx': '#17a2b8',
        'xls': '#17a2b8', 
        'pdf': '#dc3545',
        'txt': '#6c757d'
    }
    
    status_icons = {
        'ready': 'fa-clock',
        'processing': 'fa-spinner fa-spin',
        'completed': 'fa-check-circle',
        'error': 'fa-exclamation-circle'
    }
    
    status_colors = {
        'ready': '#ffc107',
        'processing': '#007bff',
        'completed': '#28a745',
        'error': '#dc3545'
    }
    
    icon = icons.get(file_type.lower(), 'fa-file')
    color = colors.get(file_type.lower(), '#6c757d')
    status_icon = status_icons.get(status, 'fa-clock')
    status_color = status_colors.get(status, '#ffc107')
    
    return f"""
    <div class="file-preview-card">
        <div class="file-icon" style="color: {color};">
            <i class="fas {icon}"></i>
        </div>
        <div class="file-details">
            <div class="file-name">{filename}</div>
            <div class="file-meta">
                <span class="file-size">{size_mb:.1f} MB</span>
                <span class="file-type">{file_type.upper()}</span>
            </div>
        </div>
        <div class="file-status" style="color: {status_color};">
            <i class="fas {status_icon}"></i>
        </div>
    </div>
    
    <style>
    .file-preview-card {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: var(--dark-surface);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }}
    
    .file-preview-card:hover {{
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }}
    
    .file-icon {{
        font-size: 2rem;
        width: 50px;
        text-align: center;
    }}
    
    .file-details {{
        flex: 1;
    }}
    
    .file-name {{
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        word-break: break-word;
    }}
    
    .file-meta {{
        display: flex;
        gap: 1rem;
        font-size: 0.8rem;
        color: var(--text-secondary);
    }}
    
    .file-status {{
        font-size: 1.2rem;
    }}
    </style>
    """

def create_metric_card(title: str, value: str, icon: str, color: str = "primary", trend: str = None):
    gradient_map = {
        "primary": "var(--primary-gradient)",
        "success": "var(--success-gradient)", 
        "warning": "var(--warning-gradient)",
        "info": "var(--accent-gradient)"
    }
    
    gradient = gradient_map.get(color, "var(--primary-gradient)")
    
    trend_html = ""
    if trend:
        trend_icon = "fa-arrow-up" if "+" in trend else "fa-arrow-down"
        trend_color = "#4CAF50" if "+" in trend else "#F44336"
        trend_html = f"""
        <div class="metric-trend" style="color: {trend_color};">
            <i class="fas {trend_icon}"></i> {trend}
        </div>
        """
    
    return f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: {gradient};">
            <i class="fas {icon}"></i>
        </div>
        <div class="metric-content">
            <div class="metric-value">{value}</div>
            <div class="metric-title">{title}</div>
            {trend_html}
        </div>
    </div>
    
    <style>
    .metric-card {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        background: var(--dark-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: {gradient};
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border-color: rgba(102, 126, 234, 0.5);
    }}
    
    .metric-icon {{
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: white;
    }}
    
    .metric-content {{
        flex: 1;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }}
    
    .metric-title {{
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }}
    
    .metric-trend {{
        font-size: 0.8rem;
        font-weight: 600;
    }}
    </style>
    """

def create_notification(message: str, type: str = "info", duration: int = 5000):
    type_config = {
        "success": {"icon": "fa-check-circle", "color": "#4CAF50"},
        "error": {"icon": "fa-exclamation-circle", "color": "#F44336"},
        "warning": {"icon": "fa-exclamation-triangle", "color": "#FF9800"},
        "info": {"icon": "fa-info-circle", "color": "#2196F3"}
    }
    
    config = type_config.get(type, type_config["info"])
    
    return f"""
    <div class="notification notification-{type}" id="notification-{int(time.time() * 1000)}">
        <div class="notification-icon">
            <i class="fas {config['icon']}"></i>
        </div>
        <div class="notification-content">
            {message}
        </div>
        <div class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </div>
    </div>
    
    <style>
    .notification {{
        position: fixed;
        top: 100px;
        right: 20px;
        background: var(--dark-card);
        border: 1px solid {config['color']};
        border-left: 4px solid {config['color']};
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        max-width: 400px;
        z-index: 1001;
        animation: slideInRight 0.3s ease, fadeOut 0.3s ease {duration}ms forwards;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}
    
    .notification-icon {{
        color: {config['color']};
        font-size: 1.2rem;
    }}
    
    .notification-content {{
        flex: 1;
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.4;
    }}
    
    .notification-close {{
        color: var(--text-secondary);
        cursor: pointer;
        font-size: 0.9rem;
        transition: color 0.3s ease;
    }}
    
    .notification-close:hover {{
        color: var(--text-primary);
    }}
    
    @keyframes slideInRight {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    @keyframes fadeOut {{
        from {{
            opacity: 1;
            transform: translateX(0);
        }}
        to {{
            opacity: 0;
            transform: translateX(100%);
        }}
    }}
    </style>
    
    <script>
    setTimeout(() => {{
        const notification = document.getElementById('notification-{int(time.time() * 1000)}');
        if (notification) {{
            notification.remove();
        }}
    }}, {duration});
    </script>
    """

def create_data_visualization(data: List[Dict], chart_type: str = "bar"):
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    if chart_type == "bar":
        fig = px.bar(
            df, 
            x=df.columns[0], 
            y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
            color_discrete_sequence=['#667eea']
        )
    elif chart_type == "pie":
        fig = px.pie(
            df,
            values=df.columns[1] if len(df.columns) > 1 else df.columns[0],
            names=df.columns[0],
            color_discrete_sequence=px.colors.qualitative.Set3
        )
    elif chart_type == "line":
        fig = px.line(
            df,
            x=df.columns[0],
            y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
            color_discrete_sequence=['#667eea']
        )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=16,
        title_font_color='white'
    )
    
    return fig

def create_search_filters():
    return """
    <div class="search-filters">
        <div class="filter-section">
            <div class="filter-title">
                <i class="fas fa-filter"></i> Quick Filters
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">
                    <i class="fas fa-globe"></i> All Properties
                </button>
                <button class="filter-btn" data-filter="2bhk">
                    <i class="fas fa-home"></i> 2 BHK
                </button>
                <button class="filter-btn" data-filter="3bhk">
                    <i class="fas fa-building"></i> 3 BHK
                </button>
                <button class="filter-btn" data-filter="furnished">
                    <i class="fas fa-couch"></i> Furnished
                </button>
                <button class="filter-btn" data-filter="parking">
                    <i class="fas fa-car"></i> Parking
                </button>
            </div>
        </div>
    </div>
    
    <style>
    .search-filters {
        background: var(--dark-card);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .filter-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    
    .filter-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .filter-btn {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .filter-btn:hover, .filter-btn.active {
        background: var(--primary-gradient);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .filter-btn i {
        font-size: 0.8rem;
    }
    </style>
    
    <script>
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    </script>
    """

def create_chat_suggestions():
    suggestions = [
        {"text": "Show me 2BHK properties under ₹80L", "icon": "fa-home"},
        {"text": "Properties near metro stations", "icon": "fa-subway"},
        {"text": "Furnished apartments with gym", "icon": "fa-dumbbell"},
        {"text": "Construction guidelines for residential", "icon": "fa-book"},
        {"text": "Properties in Adyar with parking", "icon": "fa-map-marker-alt"}
    ]
    
    suggestions_html = """
    <div class="chat-suggestions">
        <div class="suggestions-title">
            <i class="fas fa-lightbulb"></i> Suggested Queries
        </div>
        <div class="suggestions-grid">
    """
    
    for suggestion in suggestions:
        suggestions_html += f"""
        <div class="suggestion-item" onclick="sendSuggestion('{suggestion['text']}')">
            <div class="suggestion-icon">
                <i class="fas {suggestion['icon']}"></i>
            </div>
            <div class="suggestion-text">{suggestion['text']}</div>
        </div>
        """
    
    suggestions_html += """
        </div>
    </div>
    
    <style>
    .chat-suggestions {
        margin: 1rem 0;
    }
    
    .suggestions-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    
    .suggestions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 0.75rem;
    }
    
    .suggestion-item {
        background: rgba(102, 126, 234, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .suggestion-item:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .suggestion-icon {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        background: var(--primary-gradient);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.9rem;
    }
    
    .suggestion-text {
        flex: 1;
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.3;
    }
    </style>
    
    <script>
    function sendSuggestion(text) {
        const chatInput = document.querySelector('.stChatInput input');
        if (chatInput) {
            chatInput.value = text;
            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    </script>
    """
    
    return suggestions_html

def create_loading_skeleton():
    return """
    <div class="loading-skeleton">
        <div class="skeleton-header">
            <div class="skeleton-avatar"></div>
            <div class="skeleton-lines">
                <div class="skeleton-line skeleton-line-title"></div>
                <div class="skeleton-line skeleton-line-subtitle"></div>
            </div>
        </div>
        <div class="skeleton-content">
            <div class="skeleton-line"></div>
            <div class="skeleton-line"></div>
            <div class="skeleton-line skeleton-line-short"></div>
        </div>
    </div>
    
    <style>
    .loading-skeleton {
        background: var(--dark-card);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .skeleton-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .skeleton-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(90deg, #2a2d3a 25%, #3a3d4a 50%, #2a2d3a 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
    }
    
    .skeleton-lines {
        flex: 1;
    }
    
    .skeleton-line {
        height: 12px;
        background: linear-gradient(90deg, #2a2d3a 25%, #3a3d4a 50%, #2a2d3a 75%);
        background-size: 200% 100%;
        border-radius: 6px;
        margin: 0.5rem 0;
        animation: loading 1.5s infinite;
    }
    
    .skeleton-line-title {
        width: 60%;
        height: 16px;
    }
    
    .skeleton-line-subtitle {
        width: 40%;
        height: 12px;
    }
    
    .skeleton-line-short {
        width: 70%;
    }
    
    @keyframes loading {
        0% {
            background-position: 200% 0;
        }
        100% {
            background-position: -200% 0;
        }
    }
    </style>
    """

def create_property_card(property_data: Dict[str, Any]):
    title = property_data.get('title', 'Property')
    location = property_data.get('location', 'Location not specified')
    price = property_data.get('price', 'Price on request')
    bhk = property_data.get('bhk', 'N/A')
    amenities = property_data.get('amenities', '').split(',')[:3]
    
    amenity_icons = {
        'gym': 'fa-dumbbell',
        'pool': 'fa-swimming-pool',
        'parking': 'fa-car',
        'security': 'fa-shield-alt',
        'garden': 'fa-leaf',
        'metro': 'fa-subway',
        'school': 'fa-graduation-cap'
    }
    
    amenity_html = ""
    for amenity in amenities:
        amenity = amenity.strip().lower()
        icon = amenity_icons.get(amenity, 'fa-check')
        amenity_html += f"""
        <div class="amenity-tag">
            <i class="fas {icon}"></i>
            <span>{amenity.title()}</span>
        </div>
        """
    
    return f"""
    <div class="property-card">
        <div class="property-header">
            <div class="property-title">{title}</div>
            <div class="property-price">{price}</div>
        </div>
        <div class="property-details">
            <div class="property-location">
                <i class="fas fa-map-marker-alt"></i>
                {location}
            </div>
            <div class="property-bhk">
                <i class="fas fa-home"></i>
                {bhk}
            </div>
        </div>
        <div class="property-amenities">
            {amenity_html}
        </div>
        <div class="property-actions">
            <button class="btn-primary">
                <i class="fas fa-eye"></i> View Details
            </button>
            <button class="btn-secondary">
                <i class="fas fa-heart"></i> Save
            </button>
        </div>
    </div>
    
    <style>
    .property-card {{
        background: var(--dark-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .property-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
    }}
    
    .property-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }}
    
    .property-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }}
    
    .property-title {{
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        flex: 1;
        margin-right: 1rem;
    }}
    
    .property-price {{
        background: var(--success-gradient);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        white-space: nowrap;
    }}
    
    .property-details {{
        display: flex;
        gap: 1.5rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }}
    
    .property-location, .property-bhk {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }}
    
    .property-amenities {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }}
    
    .amenity-tag {{
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: var(--text-primary);
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    
    .property-actions {{
        display: flex;
        gap: 1rem;
    }}
    
    .btn-primary {{
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }}
    
    .btn-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }}
    
    .btn-secondary {{
        background: transparent;
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }}
    
    .btn-secondary:hover {{
        color: var(--text-primary);
        border-color: rgba(102, 126, 234, 0.5);
        background: rgba(102, 126, 234, 0.05);
    }}
    </style>
    """

def format_response_with_highlighting(text: str, query: str) -> str:
    import re
    
    query_words = query.lower().split()
    highlighted_text = text
    
    for word in query_words:
        if len(word) > 2:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted_text = pattern.sub(
                f'<mark style="background: rgba(102, 126, 234, 0.3); color: white; padding: 2px 4px; border-radius: 3px;">{word}</mark>',
                highlighted_text
            )
    
    return highlighted_text

def create_export_options():
    return """
    <div class="export-options">
        <div class="export-title">
            <i class="fas fa-download"></i> Export Options
        </div>
        <div class="export-buttons">
            <button class="export-btn" onclick="exportChat('json')">
                <i class="fas fa-file-code"></i>
                <span>JSON</span>
            </button>
            <button class="export-btn" onclick="exportChat('csv')">
                <i class="fas fa-file-csv"></i>
                <span>CSV</span>
            </button>
            <button class="export-btn" onclick="exportChat('pdf')">
                <i class="fas fa-file-pdf"></i>
                <span>PDF</span>
            </button>
            <button class="export-btn" onclick="exportChat('txt')">
                <i class="fas fa-file-alt"></i>
                <span>Text</span>
            </button>
        </div>
    </div>
    
    <style>
    .export-options {
        background: var(--dark-card);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .export-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    
    .export-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 0.75rem;
    }
    
    .export-btn {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        color: var(--text-primary);
        padding: 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    
    .export-btn:hover {
        background: var(--primary-gradient);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .export-btn i {
        font-size: 1.2rem;
    }
    </style>
    
    <script>
    function exportChat(format) {
        console.log('Exporting chat in', format, 'format');
    }
    </script>
    """

def validate_api_keys():
    together_key = os.getenv("TOGETHER_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    return {
        "together_ai": {
            "status": "connected" if together_key else "disconnected",
            "key_present": bool(together_key)
        },
        "gemini": {
            "status": "connected" if gemini_key else "disconnected", 
            "key_present": bool(gemini_key)
        }
    }

def get_system_stats():
    import psutil
    import platform
    
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }

def create_animated_counter(target_value: int, duration: int = 2000):
    return f"""
    <div class="animated-counter" data-target="{target_value}">0</div>
    
    <style>
    .animated-counter {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        transition: all 0.3s ease;
    }}
    </style>
    
    <script>
    function animateCounter(element, target, duration) {{
        let start = 0;
        let increment = target / (duration / 16);
        let current = start;
        
        function updateCounter() {{
            current += increment;
            if (current >= target) {{
                element.textContent = target.toLocaleString();
                return;
            }}
            element.textContent = Math.floor(current).toLocaleString();
            requestAnimationFrame(updateCounter);
        }}
        
        updateCounter();
    }}
    
    document.addEventListener('DOMContentLoaded', function() {{
        const counter = document.querySelector('.animated-counter');
        const target = parseInt(counter.dataset.target);
        animateCounter(counter, target, {duration});
    }});
    </script>
    """