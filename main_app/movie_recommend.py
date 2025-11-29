import os
import pickle
import gzip
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Group 4 - Movie Recommender",
    layout="wide",
    page_icon="🎥"
)

# --- SESSION STATE INITIALIZATION ---
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'selected_movie_name' not in st.session_state:
    st.session_state.selected_movie_name = None
if 'last_method' not in st.session_state:
    st.session_state.last_method = None

# --- EXTERNAL LINKS DATA ---
external_links = {
    "Nkiri (Download)": "https://thenkiri.com",
    "Fzmovies (Download)": "https://fzmovie.co.za",
    "Netflix (Stream)": "https://www.netflix.com",
    "MovieBox (Stream)": "https://moviebox.ph"
}

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    # 1. Group 4 Logo
    st.markdown("""
        <div style="text-align: center; font-weight: 800; font-size: 2rem;
                    padding: 10px; border: 2px solid #FF4B4B; border-radius: 15px;
                    background: rgba(255, 75, 75, 0.1); backdrop-filter: blur(5px);
                    margin-bottom: 20px;">
            GROUP 4
        </div>
    """, unsafe_allow_html=True)

    # 2. Engine Selection
    st.markdown("### ⚙️ Engine")
    filter_method = st.radio(
        "Select Method:",
        ('Content-Based Filtering', 'Collaborative Filtering'),
        label_visibility="collapsed"
    )

    st.divider()

    # 3. Quick Links
    st.markdown("### 🚀 Quick Links")
    st.link_button("💬 Join WhatsApp Team", "https://chat.whatsapp.com/DsyWXB9DzG19CbTjK8dKhF?mode=hqrt2", use_container_width=True)
    st.link_button("📂 Access Notebook", "https://colab.research.google.com/drive/1XvRHy3z1cDWH51EuRegY_i-FWH2t2ypn?usp=drive_link", use_container_width=True)
    st.link_button("📚 Study With Thrive Africa", "https://thriveafrica.co/campus", use_container_width=True)

    st.divider()

    # 4. Team & About
    with st.expander("👥 Meet the Team"):
        team = [
            "1. Peter Agyekum", "2. Felicia I. Nduefuna", "3. Olivia Mawufemor Attipoe",
            "4. Donkor Promise Esi Rhoda", "5. Osborn Tulasi", "6. Onipayede John Kwaku",
            "7. Peter Agyekum Boateng", "8. Aning Jason", "9. Maxwell Adu",
            "10. Michael Nyarku", "11. Yeboah Eldad"
        ]
        for member in team:
            st.write(member)

    with st.expander("ℹ️ About"):
        st.write("**Group 4 Final Project**")
        st.write("Course: **Machine Learning & AI**")
        st.write("Provider: **Thrive Africa**")
        st.write("Mentor: **Big Tamara**")

    with st.expander("📞 Contact"):
        st.write("**Leader:** 0202381700")
        st.write("**Assis:** 0545451317")

    st.divider()

    # 5. Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode")

# --- THEME & CSS LOGIC ---
if dark_mode:
    # DARK MODE COLORS
    main_bg = "#0e1117"
    text_color = "#ffffff"
    label_color = "#FF4B4B" 
    input_label_color = "#ffffff" 
    header_bg = "#FF4B4B"
    header_text_color = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.05)"
    card_border = "rgba(255, 255, 255, 0.1)"
    btn_text_color = "#000000"
    btn_bg = "#f0f2f6"
    btn_hover_text = "#FF4B4B"
    sidebar_arrow_color = "#FF4B4B"
    sidebar_border = "none"
else:
    # LIGHT MODE COLORS
    main_bg = "#ffffff"
    text_color = "#000000"
    label_color = "#FF4B4B" 
    input_label_color = "#8B0000" 
    header_bg = "#ffffff"
    header_text_color = "#FF4B4B"
    card_bg = "rgba(0, 0, 0, 0.02)"
    card_border = "rgba(0, 0, 0, 0.05)"
    btn_text_color = "#000000"
    btn_bg = "#f0f2f6"
    btn_hover_text = "#FF4B4B"
    sidebar_arrow_color = "#000000"
    sidebar_border = "1px solid rgba(0, 0, 0, 0.1)"

# --- CSS INJECTION ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {main_bg}; color: {text_color}; }}
    header[data-testid="stHeader"] {{ background-color: {header_bg} !important; border-bottom: 1px solid {card_border}; }}
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] .stRadio label {{ color: #000000 !important; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff !important; border-right: {sidebar_border}; }}
    [data-testid="stSidebar"] .stLinkButton a {{ color: {btn_text_color} !important; }}

    .stButton button, .stLinkButton a, div[data-testid="stDownloadButton"] button {{
        background-color: {btn_bg} !important;
        color: {btn_text_color} !important;
        border: 1px solid {card_border} !important;
        border-radius: 8px !important;
    }}
    .stButton button:hover, .stLinkButton a:hover, div[data-testid="stDownloadButton"] button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important;
        color: {btn_hover_text} !important;
        border-color: #FF4B4B !important;
    }}

    .main label {{ color: {label_color} !important; }}

    @keyframes glow {{ from {{ text-shadow: 0 0 2px {input_label_color}; }} to {{ text-shadow: 0 0 10px #FF4B4B; }} }}
    div[data-testid="stSelectbox"] > label {{
        color: {input_label_color} !important; 
        font-weight: 900 !important;
        font-size: 1.2rem !important;
        animation: glow 1.5s ease-in-out infinite alternate;
        transition: all 0.3s ease;
    }}

    @keyframes pulse-header {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); text-shadow: 0 0 15px rgba(255, 75, 75, 0.6); }} 100% {{ transform: scale(1); }} }}
    .main-header {{ transition: transform 0.3s ease; cursor: pointer; }}
    .main-header:hover {{ animation: pulse-header 1s infinite ease-in-out; }}

    /* CARD STYLING */
    .rec-card {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        border: 1px solid {card_border};
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #FF4B4B;
        color: {text_color};
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        height: 100%;
    }}

    header[data-testid="stHeader"]::after {{
        content: 'G4 SOLUTION';
        color: {header_text_color};
        font-size: 20px;
        font-weight: 900;
        position: absolute;
        left: 50%; top: 50%; transform: translate(-50%, -50%);
        z-index: 999; pointer-events: none;
    }}
    
    .stDeployButton {{ visibility: hidden; }}
    [data-testid="stImage"] img {{
        max-height: 200px; object-fit: cover; border-radius: 20px;
        box-shadow: 0 12px 24px rgba(255, 75, 75, 0.4); margin-bottom: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    BASE_PATH = os.path.dirname(__file__)
    movie_dict_path = os.path.join(BASE_PATH, 'movie_dict.pkl')
    collab_titles_path = os.path.join(BASE_PATH, 'collab_titles.pkl')
    content_sim_path = os.path.join(BASE_PATH, 'similarity.pkl.gz')
    collab_sim_path = os.path.join(BASE_PATH, 'collab_similarity.pkl.gz')

    movie_dict = pickle.load(open(movie_dict_path, 'rb'))
    collab_titles = pickle.load(open(collab_titles_path, 'rb'))

    with gzip.open(content_sim_path, 'rb') as f:
        content_sim = pickle.load(f)

    with gzip.open(collab_sim_path, 'rb') as f:
        collab_sim = pickle.load(f)

    movies_df = pd.DataFrame(movie_dict)
    return movies_df, content_sim, collab_sim, collab_titles

movies_df, content_similarity, collab_similarity, collab_titles = load_data()


# --- LOGIC ---
if st.session_state.last_method != filter_method:
    st.session_state.recommendations = None
    st.session_state.selected_movie_name = None
    st.session_state.last_method = filter_method

# NEW: Dialog Function for "About"
@st.dialog("🎬 Movie Details")
def show_movie_details(title, tags):
    st.header(title)
    st.markdown("**Tags & Keywords:**")
    st.info(tags)
    st.caption("These tags are used by the AI to find similarities.")

# UPDATED: get_recommendations now returns dictionary with Title AND Tags
def get_recommendations(movie, method):
    try:
        if method == 'Content-Based Filtering':
            idx = movies_df[movies_df['title'] == movie].index[0]
            sim = content_similarity[idx]
            titles = movies_df
        else:
            idx = list(collab_titles).index(movie)
            sim = collab_similarity[idx]
            titles = None
        
        scores = sorted(list(enumerate(sim)), key=lambda x: x[1], reverse=True)[1:6]
        
        result = []
        for i in scores:
            if method == 'Content-Based Filtering':
                movie_title = titles.iloc[i[0]].title
                # Fetch tags directly
                movie_tags = titles.iloc[i[0]].tags
            else:
                movie_title = collab_titles[i[0]]
                # Try to find tags in the main DF even for collaborative results
                try:
                    movie_tags = movies_df[movies_df['title'] == movie_title]['tags'].values[0]
                except:
                    movie_tags = "No details available for this title."
            
            # Append dictionary instead of just string
            result.append({'title': movie_title, 'tags': movie_tags})
            
        return result
    except:
        return []

def clear_results():
    st.session_state.recommendations = None
    st.session_state.selected_movie_name = None

# --- MAIN PAGE ---
st.image("https://preview.redd.it/can-i-see-all-the-movies-i-watched-in-2024-in-the-grid-view-v0-cog8js189l9e1.png?format=png&auto=webp&s=cb06477a6c7f54a331593c5a145d7023595d4d47", use_container_width=True)

st.markdown('<h2 class="main-header" style="text-align: center; color: #FF4B4B; font-size: 3rem; font-weight: 800;">RECOMMEND WITH AI</h2>', unsafe_allow_html=True)
st.write("<div style='text-align: center; margin-bottom: 30px; opacity: 0.8;'>Discover your next favorite film using Group 4's AI Engine.</div>", unsafe_allow_html=True)

# Controls
with st.container():
    if filter_method == 'Content-Based Filtering':
        st.markdown("##### 🎭 Content Mode (Plot & Genre)")
        movie_list = movies_df['title'].values
    else:
        st.markdown("##### 👥 Collaborative Mode (User Ratings)")
        movie_list = collab_titles

    selected_movie = st.selectbox("Select a movie you love:", movie_list)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button('✨ Find Recommendations', type="primary", use_container_width=True):
            st.session_state.recommendations = get_recommendations(selected_movie, filter_method)
            st.session_state.selected_movie_name = selected_movie

    with col2:
        if st.session_state.recommendations:
            if st.button('🗑️ Clear Results', use_container_width=True):
                clear_results()
                st.rerun()

# Results
if st.session_state.recommendations:
    st.markdown("---")
    st.subheader(f"Because you liked '{st.session_state.selected_movie_name}':")

    # UPDATED: Loop through dictionaries and show buttons
    for movie_data in st.session_state.recommendations:
        c_card, c_btn = st.columns([5, 1]) # Layout: Card takes 5 parts, Button takes 1 part
        
        with c_card:
            st.markdown(f'<div class="rec-card">🎬 {movie_data["title"]}</div>', unsafe_allow_html=True)
        
        with c_btn:
            # Vertical alignment spacer
            st.write("") 
            if st.button("ℹ️ About", key=f"btn_{movie_data['title']}", help="See tags"):
                show_movie_details(movie_data['title'], movie_data['tags'])

    st.markdown("---")
    st.header("📥 Save & Watch")
    col_export, col_watch = st.columns([1, 2])

    with col_export:
        # UPDATED: Export text to include Tags
        export_text = f"Movie Recommender Results (Group 4)\nSelected Movie: {st.session_state.selected_movie_name}\n\nRecommendations:\n"
        for i, movie_data in enumerate(st.session_state.recommendations, 1):
            export_text += f"{i}. {movie_data['title']}\n   Details: {movie_data['tags'][:100]}...\n" # Truncated tags for neatness
            
        export_text += f"\nWhere to Watch:\n"
        for name, url in external_links.items():
            export_text += f"- {name}: {url}\n"

        st.download_button(
            label="📄 Export Recommendations",
            data=export_text,
            file_name="group4_recommendations.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col_watch:
        st.write("**Where to Watch & Download:**")
        link_cols = st.columns(2)
        i = 0
        for name, url in external_links.items():
            with link_cols[i % 2]:
                st.link_button(f"🌐 {name}", url, use_container_width=True)
            i += 1
