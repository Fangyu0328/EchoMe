import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import get_personality_json, get_topics_list, get_reaction

# --- PAGE CONFIG ---
st.set_page_config(page_title="PersonaScope", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("🧠 Persona Scope")
page = st.sidebar.radio("Navigate", ["Home", "Personality", "Topics", "Persona Reaction"])

# --- SESSION STATE INIT ---
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.personality_json = None
    st.session_state.topics = None

# --- HOME PAGE ---
if page == "Home":
    st.title("📄 Upload Tweets CSV")
    uploaded_file = st.file_uploader("Upload CSV file with columns: text, favorite_count, view_count", type=["csv"])
    
    if uploaded_file:
        with st.spinner("Analyzing data..."):
            df = pd.read_csv(uploaded_file)

            if not all(col in df.columns for col in ["text", "favorite_count", "view_count"]):
                st.error("CSV must contain 'text', 'favorite_count', and 'view_count' columns.")
            else:
                df["engagement"] = df["favorite_count"] / df["view_count"]
                print("DF Loaded:")
                print(df.head())

                # Save dataframe in session state
                st.session_state.df = df

                personality_json = get_personality_json(df)
                print("Personality JSON:")
                print(personality_json)
                st.session_state.personality_json = personality_json

                topics = get_topics_list(df)
                print("Topics:")
                print(topics)
                st.session_state.topics = topics

                st.success("✅ Analysis complete!")

# --- PERSONALITY PAGE ---
elif page == "Personality":
    st.title("🧬 Personality Analysis")

    if st.session_state.personality_json:
        traits = st.session_state.personality_json["traits_json"]
        normalized_values = [v / 10 for v in traits.values()]
        categories = list(traits.keys())

        # Close radar
        normalized_values.append(normalized_values[0])
        categories.append(categories[0])

        fig = go.Figure(data=go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            line=dict(color='skyblue')
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1]),
            ),
            showlegend=False,
            font=dict(family="sans-serif")
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown(
            f"<div style='background-color:#111;padding:20px;border-radius:10px;color:white;font-size:18px;'>"
            f"{st.session_state.personality_json['personality_summary']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.warning("Upload tweets on the Home page first.")

# --- TOPICS PAGE ---
elif page == "Topics":
    st.title("🗂️ Detected Topics")

    if st.session_state.topics:
        df_topics = pd.DataFrame(st.session_state.topics)
        st.markdown(
            df_topics.to_html(index=False, escape=False),
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <style>
            table {
                font-size: 18px;
                background-color: #111;
                color: white;
                border-collapse: collapse;
                width: 100%;
            }
            td, th {
                border: 1px solid #444;
                padding: 10px;
                word-wrap: break-word;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Upload tweets on the Home page first.")

# --- PERSONA REACTION PAGE ---
elif page == "Persona Reaction":
    st.title("🤖 Simulated Persona Reaction")

    if st.session_state.df is None or st.session_state.personality_json is None or st.session_state.topics is None:
        st.warning("Upload tweets on the Home page first.")
    else:
        content = st.text_area("📰 Content", placeholder="Paste an article excerpt or topic summary here...", height=200)

        if st.button("React"):
            with st.spinner("Reacting..."):
                df = st.session_state.df
                radar_json = st.session_state.personality_json["traits_json"]
                topics_html = st.session_state.topics

                result = get_reaction(content, df, radar_json, topics_html)
                reaction_text = result["reaction_text"]
                reaction_score = result["reaction_score"]

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"<div style='background-color:#222;padding:20px;border-radius:10px;color:white;font-size:18px;'>"
                        f"{reaction_text}</div>",
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown("### 🔥 Reaction Score")
                    st.markdown(f"<div style='font-size:24px;font-weight:bold;'>{reaction_score}/100</div>", unsafe_allow_html=True)

                    st.progress(reaction_score / 100)

