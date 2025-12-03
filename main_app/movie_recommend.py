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
    if not os.path.exists(USER_DB_FILE):
        return {}
    try:
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def register_user(username, password):
    db = load_db()
    if username in db:
        return False, "Username already exists!"
    
    user_id = str(uuid.uuid4())[:8]
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
    db = load_db()
    if username in db:
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'selected_movie': selected_movie,
            'recommendations': [rec['title'] for rec in recommendations]
        }
        db[username]['history'].append(entry)
        save_db(db)

def delete_user_account(username):
    db = load_db()
    if username in db:
        del db[username]
        save_db(db)
        return True
    return False

def clear_user_history(username):
    db = load_db()
    if username in db:
        db[username]['history'] = []
        save_db(db)
        return True
    return False

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# --- EXTERNAL LINKS ---
external_links = {
    "Nkiri (Download)": "https://thenkiri.com",
    "Fzmovies (Download)": "https://fzmovie.co.za",
    "Netflix (Stream)": "https://www.netflix.com",
    "MovieBox (Stream)": "https://moviebox.ph"
}

# --- LOGIN / SIGNUP PAGE ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background-color: rgba(255, 75, 75, 0.05); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 75, 75, 0.2); text-align: center; margin-bottom: 20px;">
            <h1 style='color: #FF4B4B; margin:0;'>🍿 Group 4 Cinema</h1>
            <p style='margin:0; opacity: 0.7;'>Login to access your personalized AI recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        with tab1:
            st.markdown("##### Welcome Back")
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("🚀 Enter App", type="primary", use_container_width=True):
                if l_user and l_pass:
                    is_valid, user_data = authenticate_user(l_user, l_pass)
                    if is_valid:
                        st.session_state.logged_in = True
                        st.session_state.username = l_user
                        st.session_state.user_info = user_data
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.warning("Please fill all fields.")

        with tab2:
            st.markdown("##### New User?")
            s_user = st.text_input("Choose Username", key="s_user")
            s_pass = st.text_input("Choose Password", type="password", key="s_pass")
            
            if st.button("✨ Create Account", use_container_width=True):
                if s_user and s_pass:
                    success, msg = register_user(s_user, s_pass)
                    if success:
                        st.success(f"Account created! ID: {msg}. Please Login.")
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill all fields.")

# --- MAIN APP LOGIC ---
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

    # --- SESSION STATE ---
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'selected_movie_name' not in st.session_state:
        st.session_state.selected_movie_name = None
    if 'last_method' not in st.session_state:
        st.session_state.last_method = None

    # --- SIDEBAR ---
    with st.sidebar:
        st.success(f"👤 **{st.session_state.username}**")
        st.caption(f"ID: {st.session_state.user_info.get('user_id', 'N/A')}")
        
        col_logout, col_del = st.columns([1, 1])
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()

        @st.dialog("⚠️ Delete Account")
        def delete_account_dialog():
            st.warning("Permanently delete account and history?")
            if st.button("Yes, Delete", type="primary"):
                if delete_user_account(st.session_state.username):
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.rerun()

        with col_del:
            if st.button("❌ Delete", type="primary", use_container_width=True):
                delete_account_dialog()

        st.divider()
        st.markdown("### ⚙️ Engine")
        filter_method = st.radio("Method:", ('Content-Based Filtering', 'Collaborative Filtering'), label_visibility="collapsed")
        
        st.divider()
        
        # --- HISTORY & CLEAR BUTTON ---
        h_col1, h_col2 = st.columns([3, 2])
        with h_col1:
            st.markdown("### 📜 History")
        with h_col2:
            if st.button("🗑️ Clear", help="Clear History"):
                clear_user_history(st.session_state.username)
                st.rerun()

        with st.expander("Recent Activity", expanded=True):
            db = load_db()
            history = db.get(st.session_state.username, {}).get('history', [])
            if not history:
                st.caption("No history found.")
            else:
                for h in reversed(history[-5:]):
                    st.markdown(f"**🎬 {h['selected_movie']}**")
                    st.caption(f"{h['timestamp']}")
                    st.markdown("---")

        st.divider()
        st.markdown("### 🚀 Links")
        st.link_button("💬 WhatsApp", "https://chat.whatsapp.com/DsyWXB9DzG19CbTjK8dKhF?mode=hqrt2", use_container_width=True)
        st.link_button("📚 Thrive Africa", "https://thriveafrica.co/campus", use_container_width=True)
        st.divider()
        
        # --- DARK MODE TOGGLE ---
        # Note: We read this value immediately to apply CSS
        dark_mode = st.toggle("🌙 Dark Mode", value=True)

    # --- THEME COLORS & LOGIC ---
    if dark_mode:
        main_bg = "#0e1117"
        text_color = "#ffffff"
        label_color = "#FF4B4B"
        input_label_color = "#ffffff"
        card_bg = "rgba(255, 255, 255, 0.05)"
        card_border = "rgba(255, 255, 255, 0.1)"
        # Button specific colors for Dark Mode
        btn_text_color = "#ffffff" 
        btn_bg = "#262730"
    else:
        main_bg = "#ffffff"
        text_color = "#000000"
        label_color = "#FF4B4B"
        input_label_color = "#8B0000"
        card_bg = "rgba(0, 0, 0, 0.02)"
        card_border = "rgba(0, 0, 0, 0.05)"
        # Button specific colors for Light Mode
        btn_text_color = "#000000"
        btn_bg = "#f0f2f6"

    # --- CSS ---
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {main_bg}; color: {text_color}; }}
        
        /* FORCE Button Text Colors based on mode */
        .stButton button {{
            color: {btn_text_color} !important;
            background-color: {btn_bg} !important;
            border: 1px solid {card_border} !important;
        }}
        
        /* Ensure Hover Text is visible (White on Red) */
        .stButton button:hover {{
            color: #ffffff !important;
            border-color: #FF4B4B !important;
            background-color: #FF4B4B !important;
        }}
        
        /* Fix Sidebar Text Colors */
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
            color: {text_color} !important; 
        }}
        
        /* Modern Cards */
        .rec-card {{
            background: {card_bg};
            backdrop-filter: blur(10px);
            border: 1px solid {card_border};
            padding: 20px;
            border-radius: 15px;
            border-top: 5px solid #FF4B4B; 
            color: {text_color};
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 400px; /* Increased height for content */
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            overflow: hidden;
        }}
        
        .rec-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(255, 75, 75, 0.25);
            border-color: #FF4B4B;
        }}

        .movie-title {{
            font-size: 1.1rem;
            font-weight: 800;
            margin-bottom: 5px;
            color: {text_color};
            min-height: 50px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .movie-genre {{
            font-size: 0.75rem;
            color: #FF4B4B;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            min-height: 20px;
        }}

        .movie-overview {{
            font-size: 0.85rem;
            opacity: 0.8;
            display: -webkit-box;
            -webkit-line-clamp: 9; 
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.5;
            color: {text_color};
        }}

        /* Input Labels */
        div[data-testid="stSelectbox"] > label {{
            color: {input_label_color} !important;
            font-weight: 900 !important;
            font-size: 1.2rem !important;
            animation: glow 1.5s ease-in-out infinite alternate;
        }}
        @keyframes glow {{ from {{ text-shadow: 0 0 2px {input_label_color}; }} to {{ text-shadow: 0 0 10px #FF4B4B; }} }}
        
        header[data-testid="stHeader"] {{ background: transparent !important; }}
        .stDeployButton {{ visibility: hidden; }}
        </style>
    """, unsafe_allow_html=True)

    # --- LOGIC ---
    if st.session_state.last_method != filter_method:
        st.session_state.recommendations = None
        st.session_state.selected_movie_name = None
        st.session_state.last_method = filter_method

    def get_recommendations(movie, method):
        try:
            # 1. Get List of Recommended Titles based on Method
            recommended_titles = []
            
            if method == 'Content-Based Filtering':
                idx = movies_df[movies_df['title'] == movie].index[0]
                sim = content_similarity[idx]
                scores = sorted(list(enumerate(sim)), key=lambda x: x[1], reverse=True)[1:6]
                for i in scores:
                    recommended_titles.append(movies_df.iloc[i[0]].title)
            else:
                # Collaborative
                idx = list(collab_titles).index(movie)
                sim = collab_similarity[idx]
                scores = sorted(list(enumerate(sim)), key=lambda x: x[1], reverse=True)[1:6]
                for i in scores:
                    recommended_titles.append(collab_titles[i[0]])

            # 2. Fetch Details for each Title from the Main DataFrame
            result = []
            for title in recommended_titles:
                # Find the row in movies_df that matches the title
                match = movies_df[movies_df['title'] == title]
                
                if not match.empty:
                    row = match.iloc[0]
                    
                    # Get Overview
                    try: 
                        movie_info = row.overview if pd.notna(row.overview) else "No overview available."
                    except: 
                        movie_info = "No overview available."
                    
                    # Get Genre
                    try:
                        # Check for 'genres' first, then 'genre'
                        if 'genres' in row.index:
                            raw_genre = row.genres
                        elif 'genre' in row.index:
                            raw_genre = row.genre
                        else:
                            raw_genre = "Unknown"
                            
                        # Clean up list string formatting e.g. "['Action', 'Comedy']" -> "Action, Comedy"
                        movie_genre = str(raw_genre).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                    except:
                        movie_genre = "Genre: N/A"
                else:
                    movie_info = "No details found in database."
                    movie_genre = "Genre: N/A"

                result.append({'title': title, 'info': movie_info, 'genre': movie_genre})
                
            return result
        except Exception as e:
            st.error(f"Error: {e}")
            return []

    def clear_results():
        st.session_state.recommendations = None
        st.session_state.selected_movie_name = None

    # --- UI BODY ---
    st.image("https://preview.redd.it/can-i-see-all-the-movies-i-watched-in-2024-in-the-grid-view-v0-cog8js189l9e1.png?format=png&auto=webp&s=cb06477a6c7f54a331593c5a145d7023595d4d47", use_container_width=True)

    st.markdown('<h2 style="text-align: center; color: #FF4B4B; font-size: 3rem; font-weight: 800;">RECOMMEND WITH AI</h2>', unsafe_allow_html=True)

    with st.container():
        if filter_method == 'Content-Based Filtering':
            st.markdown("##### 🎭 Content Mode")
            movie_list = movies_df['title'].values
        else:
            st.markdown("##### 👥 Collaborative Mode")
            movie_list = collab_titles

        selected_movie = st.selectbox("Select a movie you love:", movie_list)

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button('✨ Find Recommendations', type="primary", use_container_width=True):
                recs = get_recommendations(selected_movie, filter_method)
                st.session_state.recommendations = recs
                st.session_state.selected_movie_name = selected_movie
                save_user_history(st.session_state.username, selected_movie, recs)
        
        with c2:
            if st.session_state.recommendations:
                if st.button('🗑️ Clear Results', use_container_width=True):
                    clear_results()
                    st.rerun()

    # --- RESULTS DISPLAY (CARDS) ---
    if st.session_state.recommendations:
        st.markdown("---")
        st.subheader(f"Because you liked '{st.session_state.selected_movie_name}':")
        
        # DISPLAY IN 5 COLUMNS
        cols = st.columns(5)
        
        for i, movie in enumerate(st.session_state.recommendations):
            with cols[i]:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="movie-title">{movie['title']}</div>
                    <div class="movie-genre">{movie['genre']}</div>
                    <div class="movie-overview">{movie['info']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.header("📥 Save & Watch")
        col_export, col_watch = st.columns([1, 2])
        
        with col_export:
            export_text = f"Group 4 Recommendations\nSource: {st.session_state.selected_movie_name}\n\n"
            for i, m in enumerate(st.session_state.recommendations, 1):
                export_text += f"{i}. {m['title']} ({m['genre']})\n   {m['info']}\n\n"
            
            st.download_button("📄 Export Results", data=export_text, file_name="g4_recs.txt", use_container_width=True)

        with col_watch:
            st.write("**Where to Watch:**")
            l_cols = st.columns(2)
            for i, (name, url) in enumerate(external_links.items()):
                with l_cols[i % 2]:
                    st.link_button(f"🌐 {name}", url, use_container_width=True)

# --- CONTROL FLOW ---
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
