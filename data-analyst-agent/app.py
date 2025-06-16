import streamlit as st
import pandas as pd
import os
from utils import read_file
from together import Together

# 🌐 Set Together API key
os.environ["TOGETHER_API_KEY"] = "Your_API_KeY"
client = Together()

# 🚀 Streamlit config
st.set_page_config(page_title="📊 Real-time Data Analyst Agent", layout="wide", page_icon="🧠")

# 🎨 Optional CSS
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        color: white !important;
        background-color: #1c1c1e !important;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #2d60ec;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# 🧭 Sidebar
with st.sidebar:
    st.title("📁 Upload Your Dataset")
    uploaded_file = st.file_uploader("Choose file", type=["csv", "xlsx", "xls", "pdf", "txt", "docx", "png", "jpg", "jpeg"])
    st.caption("Built by Logeshkumar ✨")

# 📁 Ensure temp dir exists
if not os.path.exists("temp"):
    os.makedirs("temp")

# 🧠 Title
st.markdown("<h1 style='text-align: center;'>📈 Real-time Data Analyst Agent 🤖</h1>", unsafe_allow_html=True)

# 📄 Handle Upload
if uploaded_file:
    file_path = os.path.join("temp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    df = read_file(file_path)

    if isinstance(df, pd.DataFrame):
        st.success(f"Loaded `{uploaded_file.name}` successfully!")

        # 🎯 Dataset Overview
        with st.expander("🔍 Data Preview", expanded=True):
            st.dataframe(df.head(15), use_container_width=True)

        with st.expander("📊 Dataset Overview", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", df.shape[0])
            col2.metric("Columns", df.shape[1])
            col3.metric("Missing", df.isnull().sum().sum())

            st.markdown("#### 🧬 Column Types")
            st.dataframe(df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Type"}))

            missing_df = df.isnull().sum()
            missing_df = missing_df[missing_df > 0].sort_values(ascending=False).reset_index()
            missing_df.columns = ["Column", "Missing Count"]
            if not missing_df.empty:
                st.markdown("#### ❗ Missing Values")
                st.dataframe(missing_df)

        with st.expander("📺 Type & Country Analysis"):
            if 'type' in df.columns:
                st.markdown("##### Content Type Distribution")
                st.bar_chart(df['type'].value_counts())

            if 'country' in df.columns:
                st.markdown("##### Top 10 Countries")
                st.bar_chart(df['country'].value_counts().head(10))

        with st.expander("🕰️ Time Trends"):
            if 'release_year' in df.columns:
                st.markdown("##### Release Year Distribution")
                st.line_chart(df['release_year'].value_counts().sort_index())

            if 'date_added' in df.columns:
                try:
                    df['date_added'] = pd.to_datetime(df['date_added'])
                    st.markdown("##### Entries Over Time")
                    st.line_chart(df['date_added'].dt.date.value_counts().sort_index())
                except:
                    st.warning("Could not parse `date_added` column.")

        # 📈 Interactive Column Chart
        with st.expander("📌 Custom Column Analysis"):
            col_to_plot = st.selectbox("Choose a column", df.columns)
            if pd.api.types.is_numeric_dtype(df[col_to_plot]):
                st.line_chart(df[col_to_plot])
            else:
                st.bar_chart(df[col_to_plot].value_counts().head(20))

        # 💬 Chatbot Section
        with st.expander("🤖 Ask the Analyst Agent"):
            col1, col2 = st.columns([2, 3])

            with col1:
                st.markdown("**📝 Ask a question about your data:**")
                user_question = st.text_area(" ", placeholder="E.g., What is the most common country?", label_visibility="collapsed")
                ask_button = st.button("🔍 Ask")

            def ask_llm_together(question, df):
                preview = df.head(10).to_markdown()
                summary = df.describe().to_markdown()
                cols = ", ".join(df.columns)

                prompt = f"""
You are a helpful data analyst. The dataset has the following columns: {cols}

Summary:
{summary}

Sample rows:
{preview}

Now answer the user's question:
{question}
"""
                response = client.chat.completions.create(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()

            with col2:
                if ask_button and user_question:
                    with st.spinner("Asking your AI Analyst..."):
                        answer = ask_llm_together(user_question, df)
                        st.markdown("#### ✅ Answer:")
                        st.success(answer)

    else:
        st.subheader("📄 Extracted Text from Document/Image")
        st.text(df)

else:
    # 🌟 Welcome screen
    st.markdown("### 👋 Welcome to your Real-time Data Analyst Agent!")
    st.markdown("""
This AI-powered tool allows you to:
- 🧠 Analyze tabular datasets (CSV, Excel, XLS, etc.)
- 📊 Automatically detect insights, trends, and missing data
- 💬 Ask natural language questions like "What are the top 5 genres?"
- 🖼️ Supports PDF, DOCX, TXT and even images

**Upload your file using the sidebar to get started!**
""")
    st.image("https://cdn.dribbble.com/users/1894426/screenshots/14324049/media/32b004160e5e2cf71a16d0165e7f3b26.gif", width=600)

# 🔚 Footer
st.markdown("---")
st.caption("© 2025 | Built by Logeshkumar • Streamlit + LLaMA + Together AI")
