# app/ui/app_streamlit.py
import os, sys
import json
import pandas as pd
from datetime import datetime, timedelta
import time

# Add project root to Python's import path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import streamlit as st
from app.agents.insight_agent import ask
from app.agents.tools import get_top_movers, plot_price
from app.db import init_db, engine
from sqlalchemy import text

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Crypto Insight Agent",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean dark theme
st.markdown("""
<style>
    /* Hide Streamlit branding */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stDecoration {display:none;}
    
    /* Dark theme */
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    
    /* Welcome message styling */
    .welcome-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 300;
        margin: 3rem 0;
        color: #ffffff;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #2a2a2a;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        margin-left: 20%;
    }
    
    .agent-message {
        background-color: #1a1a1a;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        margin-right: 20%;
        border-left: 3px solid #667eea;
    }
    
    /* Example cards */
    .example-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: border-color 0.2s;
    }
    
    .example-card:hover {
        border-color: #667eea;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #2a2a2a !important;
        border: 1px solid #404040 !important;
        border-radius: 25px !important;
        color: #ffffff !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .stButton > button {
        background-color: #667eea !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "show_examples" not in st.session_state:
    st.session_state.show_examples = True

# Import dashboard functions
try:
    from app.ui.dashboard import show_dashboard, show_analytics
except ImportError:
    show_dashboard = None
    show_analytics = None

# Sidebar
with st.sidebar:
    st.markdown("### 🚀 Crypto Insight Agent")
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    page = st.selectbox(
        "Choose a page:",
        ["💬 Chat Agent", "📊 Dashboard", "🔍 Analytics"],
        index=0
    )
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(DISTINCT coin_id) as coins, COUNT(*) as total_records FROM prices"))
            stats = result.fetchone()
            if stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Coins Tracked", stats[0])
                with col2:
                    st.metric("Data Points", stats[1])
    except Exception as e:
        st.warning("Database not ready")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔥 Top Movers (7d)", use_container_width=True):
        st.session_state.history.append(("Show me the top 5 movers over 7 days", None))
        try:
            response = ask("Show me the top 5 movers over 7 days")
            st.session_state.history[-1] = ("Show me the top 5 movers over 7 days", response)
        except Exception as e:
            st.session_state.history[-1] = ("Show me the top 5 movers over 7 days", f"Error: {e}")
        st.rerun()
    
    if st.button("📈 Bitcoin Chart", use_container_width=True):
        st.session_state.history.append(("Plot Bitcoin price for the last 30 days", None))
        try:
            response = ask("Plot Bitcoin price for the last 30 days")
            st.session_state.history[-1] = ("Plot Bitcoin price for the last 30 days", response)
        except Exception as e:
            st.session_state.history[-1] = ("Plot Bitcoin price for the last 30 days", f"Error: {e}")
        st.rerun()
    
    if st.button("🔍 Market Analysis", use_container_width=True):
        st.session_state.history.append(("Give me a market analysis of the top cryptocurrencies", None))
        try:
            response = ask("Give me a market analysis of the top cryptocurrencies")
            st.session_state.history[-1] = ("Give me a market analysis of the top cryptocurrencies", response)
        except Exception as e:
            st.session_state.history[-1] = ("Give me a market analysis of the top cryptocurrencies", f"Error: {e}")
        st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    
    show_examples = st.checkbox("Show Example Queries", value=st.session_state.show_examples)
    st.session_state.show_examples = show_examples

# Page routing based on selection
if page == "📊 Dashboard":
    if show_dashboard:
        show_dashboard()
    else:
        st.error("Dashboard module not available")
elif page == "🔍 Analytics":
    if show_analytics:
        show_analytics()
    else:
        st.error("Analytics module not available")
else:
    # Chat Agent page - Clean and Simple
    
    # Show welcome message if no chat history
    if not st.session_state.history:
        st.markdown('<h1 class="welcome-title">Ready when you are.</h1>', unsafe_allow_html=True)
        
        # Example queries section
        if st.session_state.show_examples:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="example-card">
                    <h4>📊 Market Analysis</h4>
                    <p>• "Show me the top 5 movers over 7 days"<br>
                    • "What are the biggest gainers this week?"<br>
                    • "Compare Bitcoin and Ethereum performance"</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="example-card">
                    <h4>📈 Price Charts</h4>
                    <p>• "Plot Bitcoin price for 30 days"<br>
                    • "Show me Ethereum's price trend"<br>
                    • "Chart Solana's performance this month"</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="example-card">
                    <h4>🔍 Insights</h4>
                    <p>• "Analyze the crypto market trends"<br>
                    • "What's driving Bitcoin's price?"<br>
                    • "Give me investment insights"</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Display chat history
    for i, (user_msg, bot_msg) in enumerate(st.session_state.history):
        # User message
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong><br>
            {user_msg}
        </div>
        """, unsafe_allow_html=True)
        
        # Agent response
        if bot_msg:
            if isinstance(bot_msg, dict):
                # Handle tool calls
                st.markdown(f"""
                <div class="agent-message">
                    <strong>🤖 Crypto Insight Agent:</strong><br>
                    Let me get that information for you using {bot_msg.get('function', 'tools')}...
                </div>
                """, unsafe_allow_html=True)
                
                # Execute the tool and show results
                try:
                    if bot_msg.get('function') == 'get_top_movers':
                        params = bot_msg.get('parameters', {})
                        result = get_top_movers(
                            period=params.get('period', '7d'),
                            limit=params.get('limit', 5)
                        )
                        st.markdown(f"""
                        <div class="agent-message">
                            <strong>📊 Market Analysis Results:</strong><br>
                            {result}
                        </div>
                        """, unsafe_allow_html=True)
                    elif bot_msg.get('function') == 'plot_price':
                        params = bot_msg.get('parameters', {})
                        result = plot_price(
                            coin=params.get('coin', 'bitcoin'),
                            days=params.get('days', 30)
                        )
                        st.markdown(f"""
                        <div class="agent-message">
                            <strong>📈 Price Chart:</strong><br>
                            {result}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="agent-message">
                        <strong>❌ Error:</strong><br>
                        Sorry, I encountered an issue: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Handle text responses
                st.markdown(f"""
                <div class="agent-message">
                    <strong>🤖 Crypto Insight Agent:</strong><br>
                    {bot_msg}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Loading state
            st.markdown("""
            <div class="agent-message">
                <strong>🤖 Crypto Insight Agent:</strong><br>
                <em>Thinking... 🤔</em>
            </div>
            """, unsafe_allow_html=True)

# Chat input at the bottom
st.markdown("---")
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", placeholder="Ask me anything about crypto...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Send 🚀", use_container_width=True)

# Handle form submission
if submit and user_input:
    # Add user message
    st.session_state.history.append((user_input, None))
    
    # Show loading state
    with st.spinner("🤖 Agent is thinking..."):
        try:
            response = ask(user_input)
            st.session_state.history[-1] = (user_input, response)
        except Exception as e:
            st.session_state.history[-1] = (user_input, f"❌ Error: {str(e)}")
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 Crypto Insight Agent | Powered by AI & Real-time Data</p>
    <p><small>Built with Streamlit, LangChain, and OpenAI</small></p>
</div>
""", unsafe_allow_html=True)