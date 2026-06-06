import streamlit as st
import tiktoken
import re
from google import genai
import json
import re

def aggressive_data_distiller(context_data):
    """
    CRUSHES data formats (JSON, Logs, Code) by removing structural tokens.
    Can achieve 60% - 85% token reduction instantly.
    """
    if not context_data.strip():
        return context_data
        
    # Attempt 1: If it's JSON, convert it to a hyper-dense CSV-style string
    try:
        parsed = json.loads(context_data)
        if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
            # Convert list of JSON objects to a pipe-delimited string (Massive savings)
            headers = parsed[0].keys()
            minified = "|".join(headers) + "\n"
            for item in parsed:
                minified += "|".join(str(item.get(k, "")) for k in headers) + "\n"
            return minified
        else:
            # Minify standard JSON by stripping all spaces
            return json.dumps(parsed, separators=(',', ':'))
    except ValueError:
        pass # Not JSON, move to raw text minification
        
    # Attempt 2: Aggressive Code/Log Minification
    # 1. Strip all leading/trailing whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', context_data)
    # 2. Strip spaces around programming operators (brackets, equals, commas)
    cleaned = re.sub(r'\s*([=+\-*/{}\[\](),:;<>|])\s*', r'\1', cleaned)
    
    return cleaned.strip()
# --- PAGE SETUP ---
st.set_page_config(
    page_title="PromptGym: Token Optimizer", 
    page_icon="🏋️‍♂️", 
    layout="wide"
)

st.title("🏋️‍♂️ PromptGym: Token Compression Engine")
st.markdown("Strip unnecessary words and conversational scaffolding from your prompts to save API costs and stretch your context window.")

# --- SIDEBAR: API KEY & CONTROLS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Needed for deep AI compression and live testing.")
    st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")
    st.divider()
    
    st.header("🎛️ The Token Gym")
    accuracy_slider = st.slider(
        "Accuracy Level", 
        min_value=0, 
        max_value=100, 
        value=80, 
        help="100% = No heavy word cutting. 0% = Aggressive keyword-only compression."
    )
    
    st.markdown("---")
    st.caption("🚀 PromptGym | Hackathon Edition")

# --- CORE UTILITIES & ENGINES ---
def count_mock_tokens(text):
    """Accurately calculates standard tokens using the common cl100k_base encoding."""
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception:
        # Fallback character length math if encoder hits an environment issue
        return len(text) // 4

def local_regex_compress(instructions, accuracy):
    """FAST PATH: Swift, zero-latency rule-based cleaning for short queries."""
    intensity = 1.0 - (accuracy / 100)
    
    # 1. Strip basic conversational scaffolding
    cleaned = instructions.lower()
    phrase_slasher = [
        r"\b(hello|hey|hi|greetings)\b,?\s*(there|gemini|chatgpt|ai)?\b",
        r"\bcan you (please|kindly|help me)\b",
        r"\bcould you (please|kindly)\b",
        r"\bi was wondering if you could\b",
        r"\bthank(s| you)?( so much| very much)?\b",
        r"\bthanks in advance\b",
        r"\bplease let me know\b",
        r"\bcan you\b",
        r"\btell me\b"
    ]
    for phrase in phrase_slasher:
        cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE)
        
    # 2. Slice standard stop words based on the intensity slider
    stop_words = ["the", "a", "an", "and", "of", "to", "in", "for", "with", "on", "at", "by", "from", "is", "are", "am", "what", "how"]
    num_to_remove = int(len(stop_words) * intensity)
    active_stops = stop_words[:num_to_remove]
    
    words = cleaned.split()
    words = [w for w in words if w not in active_stops]
    return " ".join(words).strip()

def ai_driven_compress(client, instructions, context, accuracy):
    """HEAVY PATH: Employs an LLM-driven prompt minification pipeline for heavy payloads."""
    full_payload = f"Instructions: {instructions}\n\nContext Data:\n{context}" if context else instructions
    
    # Define compression target dynamically via slider
    if accuracy >= 80:
        style = "Remove politeness and obvious conversational padding. Maintain readable sentence structure."
    elif accuracy >= 40:
        style = "Remove conversational filler, prepositions, and non-essential verbs. Use a highly compact, telegraphic style."
    else:
        style = "MAXIMUM TOKEN SAVINGS. Extractive compression. Output only the absolute bare minimum keywords needed. Disregard all grammar rules entirely."
        
    system_instruction = f"""
    You are an advanced extractive prompt compressor operating like LLMLingua.
    Your sole task is to rewrite the input to consume the minimum number of tokens possible while fully preserving the core technical instructions and underlying data intent.
    COMPRESSION TARGET: {style}
    CRITICAL: Output ONLY the resulting compressed text payload. No introductions, no explanations, no formatting markers.
    """
    
    # Fire the compression API request using the cheap, hyper-fast flash model
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=full_payload,
        config={'system_instruction': system_instruction, 'temperature': 0.1}
    )
    return response.text.strip()

# --- HYBRID ROUTER LOGIC ---
def process_hybrid_pipeline(instructions, context, accuracy, api_key):
    combined_text = instructions + " " + context
    word_count = len(combined_text.split())
    
    # Decision threshold: 150 words
    if word_count < 150:
        st.toast("🏎️ Fast Path: Executing zero-latency local compression.", icon="⚡")
        compressed_text = local_regex_compress(instructions, accuracy)
        
        # Apply standard structural Attention Chunking if context exists
        if context:
            compressed_text = f"=== CRITICAL INSTRUCTIONS ===\n{compressed_text}\n\n=== DATA ===\n{context}"
        return compressed_text
    else:
        if not api_key:
            st.error("⚠️ Heavy payload detected! Please provide a Gemini API Key in the sidebar to run deep AI compression.")
            return None
            
        st.toast("🤖 Heavy Path: Activating Deep AI Prompt Minification...", icon="🧠")
        client = genai.Client(api_key=api_key)
        return ai_driven_compress(client, instructions, context, accuracy)

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Prompt Setup")
    raw_instructions = st.text_area(
        "Main Instructions (What you want the AI to do)", 
        height=160, 
        placeholder="Hello Gemini! Could you please tell me what is the essence of pointers in C++? Thank you so much!"
    )
    raw_context = st.text_area(
        "Data / Background Context (Logs, Codebases, Text Documents)", 
        height=160, 
        placeholder="Paste large system data strings here if your instructions refer to them..."
    )
    
    if st.button("🚀 Optimize & Slash Tokens", use_container_width=True, type="primary"):
        if not raw_instructions.strip():
            st.warning("Please type a core instruction prompt first.")
        else:
            with st.spinner("Processing through the Hybrid Routing Engine..."):
                optimized_output = process_hybrid_pipeline(raw_instructions, raw_context, accuracy_slider, api_key)
                
                if optimized_output:
                    orig_tokens = count_mock_tokens(raw_instructions + " " + raw_context)
                    new_tokens = count_mock_tokens(optimized_output)
                    savings = round(((orig_tokens - new_tokens) / orig_tokens * 100) if orig_tokens > 0 else 0)
                    
                    # Store variables in session state to protect them during UI refreshes
                    st.session_state['optimized'] = optimized_output
                    st.session_state['orig_tokens'] = orig_tokens
                    st.session_state['new_tokens'] = new_tokens
                    st.session_state['savings'] = savings

with col2:
    st.subheader("2. Efficiency & ROI Analysis")
    
    if 'optimized' in st.session_state:
        # Display the custom token gym metrics scoreboard
        m1, m2, m3 = st.columns(3)
        m1.metric("Original Token Volume", st.session_state['orig_tokens'])
        m2.metric("Optimized Payload Size", st.session_state['new_tokens'])
        m3.metric("Context Limits Saved", f"{st.session_state['savings']}%")
        
        st.text_area("Compressed Data Output", value=st.session_state['optimized'], height=180)
        
        st.subheader("3. Live Execution Test")
        if st.button("💥 Run Live Request with Compressed Payload", use_container_width=True):
            if not api_key:
                st.error("Please insert your Gemini API Key in the sidebar configuration layout to execute live tests.")
            else:
                with st.spinner("Streaming response from Gemini..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=st.session_state['optimized']
                        )
                        st.success("Target AI Evaluation Complete!")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Execution Error: {e}")
    else:
        st.info("Input your prompt on the left and click 'Optimize & Slash Tokens' to see the metrics interface.")
