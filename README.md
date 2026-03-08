# Chat Canvas - Ask Your CSV

An AI-powered data analysis app built with Python, Streamlit, and the OpenAI API. Upload a CSV file and ask questions about your data in plain English — the app generates and runs Python code to return insights and visualizations.

## Features

- **CSV Upload** — Load any CSV and instantly preview rows, columns, memory usage, and missing values.
- **Natural Language Queries** — Ask questions in plain English; the app converts them into pandas/matplotlib/seaborn code and executes it.
- **Interactive Visualizations** — Automatically generates and displays charts from your data.
- **Conversational Context** — Maintains chat history so you can ask follow-up questions.

## Tech Stack

- **Streamlit** — UI and chat interface
- **OpenAI API (GPT-4.1)** — Natural language to code generation
- **pandas** — Data manipulation
- **matplotlib / seaborn** — Data visualization

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your OpenAI API key to `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
