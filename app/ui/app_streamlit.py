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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .agent-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
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

# Main content
st.markdown("""
<div class="main-header">
    <h1>🚀 Crypto Insight Agent</h1>
    <p>Your AI-powered cryptocurrency analysis assistant</p>
</div>
""", unsafe_allow_html=True)

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
    # Default to Chat Agent page
    # Example queries section
    if st.session_state.show_examples and not st.session_state.history:
        st.markdown("### 💡 Try These Example Queries:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Market Analysis**
            - "Show me the top 5 movers over 7 days"
            - "What are the biggest gainers this week?"
            - "Compare Bitcoin and Ethereum performance"
            """)
        
        with col2:
            st.markdown("""
            **📈 Price Charts**
            - "Plot Bitcoin price for 30 days"
            - "Show me Ethereum's price trend"
            - "Chart Solana's performance this month"
            """)
        
        with col3:
            st.markdown("""
            **🔍 Insights**
            - "Analyze the crypto market trends"
            - "What's driving Bitcoin's price?"
            - "Give me investment insights"
            """)

    # Chat interface
    st.markdown("### 💬 Chat with the Agent")

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input("Ask me anything about crypto...", placeholder="e.g., Show me the top movers this week")
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

    # Display chat history
    if st.session_state.history:
        st.markdown("---")
        
        for i, (user_msg, bot_msg) in enumerate(reversed(st.session_state.history)):
            # User message
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong><br>
                {user_msg}
            </div>
            """, unsafe_allow_html=True)
            
            # Agent response
            if bot_msg:
                if isinstance(bot_msg, dict):
                    # Handle tool calls
                    st.markdown(f"""
                    <div class="chat-message agent-message">
                        <strong>🤖 Agent:</strong><br>
                        Executing function: <code>{bot_msg.get('function', 'unknown')}</code>
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
                            st.markdown(result)
                        elif bot_msg.get('function') == 'plot_price':
                            params = bot_msg.get('parameters', {})
                            result = plot_price(
                                coin=params.get('coin', 'BTC'),
                                days=params.get('days', 30)
                            )
                            st.markdown(result)
                    except Exception as e:
                        st.error(f"Error executing tool: {e}")
                else:
                    # Handle text responses
                    st.markdown(f"""
                    <div class="chat-message agent-message">
                        <strong>🤖 Agent:</strong><br>
                        {bot_msg}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Loading state
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🤖 Agent:</strong><br>
                    <em>Thinking... 🤔</em>
                </div>
                """, unsafe_allow_html=True)
            
            if i < len(st.session_state.history) - 1:
                st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🚀 Crypto Insight Agent | Powered by AI & Real-time Data</p>
    <p><small>Built with Streamlit, LangChain, and OpenAI</small></p>
</div>
""", unsafe_allow_html=True)