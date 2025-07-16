# app/ui/app_streamlit.py
# app/ui/app_streamlit.py

import os, sys

# 0️⃣ Add project root to Python’s import path (must run before any 'app.' imports)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import streamlit as st
from app.agents.insight_agent import ask  # now Python can find 'app'
from app.db import init_db     # ← run migrations/bootstrap
init_db()

from app.agents.insight_agent import ask

st.set_page_config(page_title="Crypto Insight Agent", page_icon="🤖")

# rest of your code…


# Initialize session state for chat history
if "history" not in st.session_state:
    st.session_state.history = []  # list of (user, bot) tuples

st.title("🤖 Crypto Insight Agent")
st.write("Ask me about crypto prices, top movers, or tool arguments.")

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", "")
    submit = st.form_submit_button("Send")

if submit and user_input:
    # Append the user message
    st.session_state.history.append( (user_input, None) )
    # Call your ask() function
    try:
        response = ask(user_input)
    except Exception as e:
        response = f"Error: {e}"
    # Update the last chat with bot response
    st.session_state.history[-1] = (user_input, response)

# Render the chat
for user_msg, bot_msg in st.session_state.history:
    st.markdown(f"**You:** {user_msg}")
    if bot_msg:
        # If it's an inline image (data:image/png;base64...), it will render
        st.markdown(f"**Agent:**\n\n{bot_msg}")
    else:
        st.markdown("**Agent is typing…**")
