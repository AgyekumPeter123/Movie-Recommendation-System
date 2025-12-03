import os
import pickle
import gzip
import pandas as pd
import streamlit as st
import json
import hashlib
import uuid
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Group 4 - Movie Recommender",
    layout="wide",
    page_icon="🎥"
)

# --- FILE PATHS ---
USER_DB_FILE = 'user_database.json'

# --- AUTHENTICATION & DATA FUNCTIONS ---

def load_db():
    """Load user data from JSON file."""
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    """Save user data to JSON file."""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    """Simple hash for security."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def register_user(username, password):
    db = load_db()
    if username in db:
        return False, "Username already exists!"
    
    user_id = str(uuid.uuid4())[:8] # Simple 8-char User ID
    db[username] = {
        'password': hash_password(password),
        'user_id': user_id,
        'history': []
    }
    save_db(db)
    return True, user_id

def authenticate_user(username, password):
    db = load_db()
    if username not in db:
        return False, None
    
    if db[username]['password'] == hash_password(password):
        return True, db[username]
    return False, None

def save_user_history(username, selected_movie, recommendations):
    """Saves the search result to the user's specific history."""
    db = load_db()
    if username in db:
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'selected_movie': selected_movie,
            'recommendations': [rec['title'] for rec in recommendations]
        }
        db[username]['history'].append(entry)
        save_db(db)

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- EXTERNAL LINKS DATA ---
external_links = {
    "Nkiri (Download)": "https://thenkiri.com",
    "Fzmovies (Download)": "https://fzmovie.co.za",
    "Netflix (Stream)": "https://www.netflix.com",
    "MovieBox (Stream)": "https://moviebox.ph"
}

# --- LOGIN / SIGNUP PAGE ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🔐 Group 4 Access</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Welcome Back")
        l_user = st.text_input("Username", key="l_user")
        l_pass = st.text_input("Password", type="password", key="l_pass")
        
        if st.button("Login", type="primary", use_container_width=True):
            if l_user and l_pass:
                is_valid, user_data = authenticate_user(l_user, l_pass)
                if is_valid:
                    st.session_state.logged_in = True
                    st.session_state.username = l_user
                    st.session_state.user_info = user_data
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
            else:
                st.warning("Please enter all fields")

    with tab2:
        st.subheader("Create an Account")
        s_user = st.text_input("Choose Username", key="s_user")
        s_pass = st.text_input("Choose Password", type="password", key="s_pass")
        
        if st.button("Sign Up", use_container_width=True):
            if s_user and s_pass:
                success, msg = register_user(s_user, s_pass)
                if success:
                    st.success(f"Account created! Your User ID is: {msg}. Please Login.")
                else:
                    st.error(msg)
            else:
                st.warning("Please enter all fields")

# --- MAIN APP LOGIC (Your Original Code Wrapped) ---
def main_app():
    # --- LOAD DATA ---
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

    # --- SESSION STATE FOR APP ---
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'selected_movie_name' not in st.session_state:
        st.session_state.selected_movie_name = None
    if 'last_method' not in st.session_state:
        st.session_state.last_method = None

    # --- SIDEBAR ---
    with st.sidebar:
        # USER INFO DISPLAY
        st.success(f"👤 **User:** {st.session_state.username}")
        st.caption(f"ID: {st.session_state.user_info.get('user_id', 'N/A')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
            
        st.divider()
        
        # Original Sidebar Content
        st.markdown("""
            <div style="text-align: center; font-weight: 800; font-size: 2rem;
                        padding: 10px; border: 2px solid #FF4B4B; border-radius: 15px;
                        background: rgba(255, 75, 75, 0.1); backdrop-filter: blur(5px);
                        margin-bottom: 20px;">
                GROUP 4
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### ⚙️ Engine")
        filter_method = st.radio(
            "Select Method:",
            ('Content-Based Filtering', 'Collaborative Filtering'),
            label_visibility="collapsed"
        )

        st.divider()
        
        # VIEW HISTORY BUTTON
        with st.expander("📜 Your History"):
            db = load_db()
            history = db[st.session_state.username].get('history', [])
            if not history:
                st.write("No history yet.")
            else:
                for h in reversed(history[-5:]): # Show last 5
                    st.write(f"**{h['selected_movie']}**")
                    st.caption(f"{h['timestamp']}")
                    st.markdown("---")

        st.divider()

        st.markdown("### 🚀 Quick Links")
        st.link_button("💬 Join WhatsApp Team", "https://chat.whatsapp.com/DsyWXB9DzG19CbTjK8dKhF?mode=hqrt2", use_container_width=True)
        st.link_button("📂 Access Notebook", "https://colab.research.google.com/drive/1XvRHy3z1cDWH51EuRegY_i-FWH2t2ypn?usp=drive_link", use_container_width=True)
        st.link_button("📚 Study With Thrive Africa", "https://thriveafrica.co/campus", use_container_width=True)

        st.divider()

        with st.expander("👥 Meet the Team"):
            team = [
                "1. Peter Agyekum", "2. Felicia I. Nduefuna", "3. Olivia Mawufemor Attipoe",
                "4. Donkor Promise Esi Rhoda", "5. Osborn Tulasi", "6. Onipayede John Kwaku",
                "7. Peter Agyekum Boateng", "8. Aning Jason", "9. Maxwell Adu",
                "10. Michael Nyarku", "11. Yeboah Eldad"
            ]
            for member in team:
                st.write(member)

        dark_mode = st.toggle("🌙 Dark Mode")

    # --- THEME LOGIC ---
    if dark_mode:
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

    # --- CSS ---
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .rec-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(255, 75, 75, 0.3);
            border-color: #FF4B4B;
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

    # --- APP LOGIC ---
    if st.session_state.last_method != filter_method:
        st.session_state.recommendations = None
        st.session_state.selected_movie_name = None
        st.session_state.last_method = filter_method

    @st.dialog("🎬 Movie Overview")
    def show_movie_details(title, overview):
        st.header(title)
        st.write(overview)
        st.caption("Plot summary from TMDB Database.")

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
                    try:
                        movie_info = titles.iloc[i[0]].overview
                    except:
                        movie_info = "No overview available."
                else:
                    movie_title = collab_titles[i[0]]
                    try:
                        movie_info = movies_df[movies_df['title'] == movie_title]['overview'].values[0]
                    except:
                        movie_info = "No overview available for this title."
                
                result.append({'title': movie_title, 'info': movie_info})
                
            return result
        except:
            return []

    def clear_results():
        st.session_state.recommendations = None
        st.session_state.selected_movie_name = None

    # --- UI LAYOUT ---
    st.image("https://preview.redd.it/can-i-see-all-the-movies-i-watched-in-2024-in-the-grid-view-v0-cog8js189l9e1.png?format=png&auto=webp&s=cb06477a6c7f54a331593c5a145d7023595d4d47", use_container_width=True)

    st.markdown('<h2 class="main-header" style="text-align: center; color: #FF4B4B; font-size: 3rem; font-weight: 800;">RECOMMEND WITH AI</h2>', unsafe_allow_html=True)
    st.write("<div style='text-align: center; margin-bottom: 30px; opacity: 0.8;'>Discover your next favorite film using Group 4's AI Engine.</div>", unsafe_allow_html=True)

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
                recs = get_recommendations(selected_movie, filter_method)
                st.session_state.recommendations = recs
                st.session_state.selected_movie_name = selected_movie
                # --- SAVE TO USER HISTORY ---
                save_user_history(st.session_state.username, selected_movie, recs)
                st.toast(f"Saved to history for {st.session_state.username}!")

        with col2:
            if st.session_state.recommendations:
                if st.button('🗑️ Clear Results', use_container_width=True):
                    clear_results()
                    st.rerun()

    if st.session_state.recommendations:
        st.markdown("---")
        st.subheader(f"Because you liked '{st.session_state.selected_movie_name}':")

        for movie_data in st.session_state.recommendations:
            c_card, c_btn = st.columns([5, 1])
            with c_card:
                st.markdown(f'<div class="rec-card">🎬 {movie_data["title"]}</div>', unsafe_allow_html=True)
            with c_btn:
                st.write("") 
                if st.button("ℹ️ About", key=f"btn_{movie_data['title']}", help="Read Plot"):
                    show_movie_details(movie_data['title'], movie_data['info'])

        st.markdown("---")
        st.header("📥 Save & Watch")
        col_export, col_watch = st.columns([1, 2])

        with col_export:
            export_text = f"Movie Recommender Results (Group 4)\nSelected Movie: {st.session_state.selected_movie_name}\n\nRecommendations:\n"
            for i, movie_data in enumerate(st.session_state.recommendations, 1):
                export_text += f"{i}. {movie_data['title']}\n   Plot: {movie_data['info']}\n"
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

# --- CONTROL FLOW ---
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
