import streamlit as st
import tiktoken
import re
from google import genai

# --- PAGE SETUP ---
st.set_page_config(page_title="PromptGym", page_icon="🏋️‍♂️", layout="wide")

st.title("🏋️‍♂️ PromptGym: Token Compression Engine")
st.markdown("Strip unnecessary words from your prompts to save API costs and context limits.")

# --- SIDEBAR: API KEY SETUP ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")
    st.divider()
    
    st.header("🎛️ The Token Gym")
    accuracy_slider = st.slider("Accuracy Level", min_value=0, max_value=100, value=80, 
                                help="100 = Exact Prompt. 0 = Aggressive Stop-Word Removal.")
    
    st.markdown("---")
    st.caption("Built with Streamlit & Gemini API for the Hackathon.")

# --- HELPER FUNCTIONS ---
def count_mock_tokens(text):
    # Approximation since tiktoken is for OpenAI, but it gives a good relative metric
    encoder = tiktoken.get_encoding("cl100k_base")
    return len(encoder.encode(text))

def compress_prompt(instructions, context, accuracy):
    intensity = 1.0 - (accuracy / 100)
    
    # Step 1: Strip Politeness
    cleaned = instructions
    fillers = [r"\b(hello|hey|hi)\b", r"\bplease\b", r"\bthank you\b", r"\bthanks\b"]
    for f in fillers:
        cleaned = re.sub(f, "", cleaned, flags=re.IGNORECASE)
        
    # Step 2: Strip Stop Words based on slider
    stop_words = ["the", "a", "an", "and", "of", "to", "in", "for", "with", "on", "at", "by", "from"]
    num_to_remove = int(len(stop_words) * intensity)
    active_stops = stop_words[:num_to_remove]
    
    words = cleaned.split()
    words = [w for w in words if w.lower() not in active_stops]
    final_instructions = " ".join(words)
    
    # Step 3: Attention Chunking
    if context:
        lines = final_instructions.split(". ")
        mid = len(lines) // 2
        top = ". ".join(lines[:mid])
        bottom = ". ".join(lines[mid:])
        
        return f"=== INSTRUCTIONS (START) ===\n{top}\n\n=== CONTEXT ===\n{context}\n\n=== INSTRUCTIONS (END) ===\n{bottom}"
    
    return final_instructions

# --- MAIN UI LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Input")
    raw_instructions = st.text_area("What do you want the AI to do?", height=150, 
                                    placeholder="Hello AI, could you please summarize this log? Thank you!")
    raw_context = st.text_area("Heavy Background Data / Context (Optional)", height=150, 
                               placeholder="Paste code or data here...")
    
    if st.button("⚡ Compress Prompt", use_container_width=True, type="primary"):
        if not raw_instructions:
            st.warning("Please enter some instructions first.")
        else:
            optimized = compress_prompt(raw_instructions, raw_context, accuracy_slider)
            
            orig_tokens = count_mock_tokens(raw_instructions + " " + raw_context)
            new_tokens = count_mock_tokens(optimized)
            savings = round(((orig_tokens - new_tokens) / orig_tokens * 100) if orig_tokens > 0 else 0)
            
            # Save to session state so we don't lose it on reload
            st.session_state['optimized'] = optimized
            st.session_state['orig_tokens'] = orig_tokens
            st.session_state['new_tokens'] = new_tokens
            st.session_state['savings'] = savings

with col2:
    st.subheader("2. Optimization Results")
    
    if 'optimized' in st.session_state:
        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Original Tokens", st.session_state['orig_tokens'])
        m2.metric("Optimized Tokens", st.session_state['new_tokens'])
        m3.metric("Tokens Saved", f"{st.session_state['savings']}%")
        
        st.text_area("Final Compressed Payload", value=st.session_state['optimized'], height=150)
        
        st.subheader("3. Test Live with Gemini")
        if st.button("🚀 Send to Gemini", use_container_width=True):
            if not api_key:
                st.error("Please enter your Gemini API Key in the sidebar.")
            else:
                with st.spinner("Asking Gemini..."):
                    try:
                        # Initialize the current google-genai client
                        client = genai.Client(api_key=api_key)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=st.session_state['optimized']
                        )
                        st.success("Response Received!")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("Click 'Compress Prompt' to see results here.")