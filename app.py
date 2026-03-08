import warnings

import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(
    page_title="Ask Your CSV",
    page_icon="📊",
    layout="wide",
)

# Initialize OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📊 Ask your CSV")
st.markdown("Upload your data and ask questions in plain English!")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

if "data_summary" not in st.session_state:
    st.session_state.data_summary = None


with st.sidebar:
    st.header("🗂️ Data upload")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(
                f"✅ Loaded {df.shape[0]} rows and {df.shape[1]} columns successfully!"
            )

            with st.expander("Preview Data"):
                st.dataframe(df.head())

            with st.expander("Preview Data"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Rows", df.shape[0])
                    st.metric("Total Columns", df.shape[1])
                with col2:
                    st.metric(
                        "Memory Usage",
                        f"{df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB",
                    )
                    st.metric("Missing Values", df.isnull().sum().sum())

        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure your file is a valid CS format.")

    else:
        st.info("👆 Upload a CSV file to start analyzing your data.")


# Main chat interface
if st.session_state.df is not None:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Re-display any saved figures
            if "figure" in msg:
                st.pyplot(msg["figure"])

    # Chat input
    user_input = st.chat_input("Ask a question about your data")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # Prepare data context with token optimization
        df = st.session_state.df
        if len(df) > 100:
            data_context = f"""
            Dataset shape: {st.session_state.data_summary['shape']}
            Columns: {', '.join(st.session_state.data_summary['columns'])}
            Data types: {st.session_state.data_summary['dtypes']}
            Sample rows: {st.session_state.data_summary['sample']}
            Basic statistics: {st.session_state.data_summary['stats']}
            """
        else:
            data_context = f"""
            Full dataset:
            {df.to_string()}
            """

        system_prompt = f""" You are a helpful data analyst assistant. 
        
        The user has uploaded a CSV file with the following information: {data_context}
        
        The data is loaded into a pandas Datafrom called 'df'. 
        
        Guidelines:
        - Answer the user's question clearly and concisely.
        - If the question requires analysis, write Python code using pandas, matplotlib, or seaborn
        - For visualizations, always use plt.figure() before plotting and include plt.tight_layout() after to ensure proper formatting.
        - Always validate data before operations (check for nulls, data types, etc.)
        - If you can't answer due to data limitations, explain why
        - Keep responses focused on the data and questions asked
        
        When writing code:
        - Import statements are already done (pandas as pd, matplotlib.pyplot as plt, seaborn as sns)
        - The dataframe is available as 'df'
        - For plots, use plt.figure(figsize=(10,6)) for better display
        - Always add titles and labels to plots
        """

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Analyzing your data..."):
                try:
                    messages = [{"role": "system", "content": system_prompt}]

                    for msg in st.session_state.messages[
                        -6:
                    ]:  # Include last 6 messages for context
                        # Truncate long message in history to save tokens
                        content = msg["content"]
                        if len(content) > 500:
                            content = content[:500] + "..."

                        messages.append({"role": msg["role"], "content": content})

                    messages.append({"role": "user", "content": user_input})
                    response = client.chat.completions.create(
                        model="gpt-4.1",
                        messages=messages,
                        temperature=0.1,
                        max_tokens=1500,
                    )
                    reply = response.choices[0].message.content
                    message_placeholder.markdown(reply)
                    # Save assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply}
                    )

                    # try to execute any code in the response
                    if "```python" in reply:
                        code_blocks = reply.split("```python")
                        for i in range(1, len(code_blocks)):
                            code = code_blocks[i].split("```")[0]
                    try:
                        # Display warnings if any
                        with warnings.catch_warnings(record=True) as w:
                            warnings.simplefilter("always")
                        # Create figure for potential plots
                        plt.figure(figsize=(10, 6))

                        exec_globals = {
                            "df": df,
                            "pd": pd,
                            "plt": plt,
                            "sns": sns,
                            "st": st,
                        }
                        exec(code.strip(), exec_globals)

                        # Display any warnings that were raised during code execution
                        if w:
                            for warning in w:
                                st.warning(
                                    f"Warning during code execution: {str(warning.message)}"
                                )

                        # Display plot if created
                        fig = plt.gcf()
                        if fig.get_axes():
                            st.pyplot(fig)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": reply, "figure": fig}
                            )
                        else:
                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": reply,
                                }
                            )
                        plt.close()
                    except Exception as code_e:
                        error_type = type(code_e).__name__
                        st.error(f"Code execution failed: {error_type}")

                        # Provide helpful context based on error type
                        if "NameError" in str(code_e):
                            st.info(
                                "This might mean a column name is misspelled or doesn't exist in the dataset."
                            )
                        elif "TypeError" in str(code_e):
                            st.info(
                                "This often happens when trying to plot non-numeric data"
                            )
                        elif "KeyError" in str(code_e):
                            st.info(
                                "The specific column might not exist in your dataset."
                            )
                        else:
                            st.info(
                                "Try rephrasing your question or check your data format."
                            )

                except openai.APIError as api_e:
                    st.error(f"OPENAI API error: {str(api_e)}")
                    st.info("Please check your API key and try again.")

                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    st.info("Please try again or rephrase your question.")
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 Please upload a CSV file to start")

        # Example questions
        st.markdown("### 💡 Example questions you can ask:")
        st.markdown(
            """
                    - What are the main trends in my data?
                    - Show me a correlation matrix
                    - Create a bar chart of the top 10 categories
                    - What's the average value by month?
                    - Are there any outliers in the piece column?
                    """
        )

# footer with tips
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray; font-size: 12px;'>
💡 Tip: Be specific with your questions for better results |
🔒 Your data stays private and is not stored
</div>
""",
    unsafe_allow_html=True,
)
