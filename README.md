# 🏋️‍♂️ PromptGym: The Ultimate Token Compression Engine

**Slash API costs and stretch your context windows with intelligent, hybrid prompt minification.**

[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Powered by Gemini](https://img.shields.io/badge/Powered_by-Google_Gemini-4285F4.svg)](https://deepmind.google/technologies/gemini/)

## ⚠️ The Problem
In the era of pay-per-token LLMs and strict context windows, "Prompt Bloat" is an expensive problem. Humans naturally write with conversational scaffolding ("Hello AI, could you please tell me..."). This linguistic fluff accounts for roughly **15% to 30% of wasted tokens** in enterprise API calls, leading to higher costs, slower response times, and busted caching mechanisms.

## 💡 The Solution
**PromptGym** is a high-performance middleware dashboard that acts as a token slasher. It allows developers and users to compress their prompts down to their absolute bare-minimum token weight without losing the target AI's ability to understand the core technical intent.

### ✨ Key Features
* **🎛️ The Reverse Token Gym Slider:** Put the power in the user's hands. Slide between 100% (mild politeness stripping) down to 0% (aggressive, grammar-destroying keyword extraction).
* **🧠 The Hybrid Routing Architecture:** * **Fast Path:** Short prompts (< 150 words) are routed through a zero-latency, local regex engine to strip stop-words instantly.
  * **Heavy Path:** Massive documents and codebases trigger a Two-Stage Pipeline, utilizing `gemini-2.5-flash` as a heuristic parser to compress the payload *before* sending it to the target model.
* **📊 Real-Time ROI Metrics:** Instantly see your `[Original Tokens]` vs `[Optimized Tokens]` and calculate your exact percentage of limits saved.
* **🎯 Native Target Execution:** Plug in your API key to test the compressed payload directly against the Gemini API from within the app.

---

## 🚀 How to Run Locally

Want to test the token slasher on your own machine? It takes less than 2 minutes.

### Prerequisites
* Python 3.9+
* A free [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/promptgym.git](https://github.com/YourUsername/promptgym.git)
   cd promptgym
