import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Ask Your CSV",
    page_icon="📊",
    layout="wide",
)

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

    # Chat input
    user_input = st.chat_input("Ask a question about your data")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)
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
