import os
import pickle
import gzip
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import json
import hashlib
import uuid
import re
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="G4 SOLUTION - Movie Recommender",
    layout="wide",
    page_icon="🎥"
)

# --- FILE PATHS ---
USER_DB_FILE = 'user_database.json'

# --- EMAIL CREDENTIALS ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "agyekumpeter123@gmail.com"
APP_PASSWORD = "lftr wrba rwsq blst"

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

# --- PASSWORD STRENGTH CHECK ---
def check_password_strength(password):
    if len(password) < 6:
        return False, "⚠️ Password must be at least 6 characters."
    if not re.search(r"\d", password):
        return False, "⚠️ Password must contain at least one number."
    if not re.search(r"[A-Z]", password):
        return False, "⚠️ Password must contain at least one uppercase letter."
    return True, "Valid"

# --- EMAIL OTP FUNCTION ---
def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "🔐 G4 SOLUTION: Password Reset OTP"

        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #FF4B4B;">G4 Solution Movie Recommender</h2>
            <p>You requested a password reset.</p>
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; display: inline-block;">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 2px;">{otp}</span>
            </div>
            <p>If you did not request this, please ignore this email.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- REGISTRATION ---
def register_user(username, email, password):
    # 1. Check Strength
    is_strong, msg = check_password_strength(password)
    if not is_strong:
        return False, msg

    db = load_db()
    if username in db:
        return False, "⚠️ Username already exists!"
    
    # 2. Check if email exists
    for user, data in db.items():
        if data.get('email') == email:
            return False, "⚠️ Email already registered!"

    user_id = str(uuid.uuid4())[:8]
    db[username] = {
        'email': email,
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

def reset_password(username, new_password):
    db = load_db()
    if username in db:
        db[username]['password'] = hash_password(new_password)
        save_db(db)
        return True
    return False

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

# Forgot Password States
if 'fp_step' not in st.session_state:
    st.session_state.fp_step = 1
if 'fp_otp' not in st.session_state:
    st.session_state.fp_otp = None
if 'fp_username' not in st.session_state:
    st.session_state.fp_username = None

# --- EXTERNAL LINKS ---
external_links = {
    "Nkiri (Download)": "https://thenkiri.com",
    "Fzmovies (Download)": "https://fzmovie.co.za",
    "Netflix (Stream)": "https://www.netflix.com",
    "MovieBox (Stream)": "https://moviebox.ph"
}

# --- LOGIN / SIGNUP PAGE ---
def login_page():
    # === ANIMATION INJECTION START ===
    st.markdown("""
    <style>
        /* Container for the background animation */
        .animation-wrapper {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 0; /* Behind the form */
            pointer-events: none;
            overflow: hidden;
        }

        .anim-text {
            font-size: 8rem; 
            font-weight: 900;
            color: rgba(255, 255, 255, 0.4); 
            text-shadow: 0 0 20px rgba(255, 75, 75, 0.5); /* Red Glow */
            text-transform: uppercase;
            white-space: nowrap;
        }

        .g4-part {
            animation: moveFromLeft 12s ease-in-out infinite; 
            margin-right: 20px; 
        }

        .solution-part {
            animation: moveFromRight 12s ease-in-out infinite; 
        }

        /* --- UPDATED KEYFRAMES FOR SLOW ENTRY / FAST EXIT --- */
        @keyframes moveFromLeft {
            0% { transform: translateX(-100vw); opacity: 0; }
            35% { transform: translateX(0); opacity: 1; } /* Slow Entry (takes 35% of time) */
            90% { transform: translateX(0); opacity: 1; } /* Stay Visible until 90% */
            95% { transform: translateX(0); opacity: 0; } /* VERY QUICK FADE OFF */
            100% { transform: translateX(-100vw); opacity: 0; }
        }

        @keyframes moveFromRight {
            0% { transform: translateX(100vw); opacity: 0; }
            35% { transform: translateX(0); opacity: 1; } /* Slow Entry */
            90% { transform: translateX(0); opacity: 1; } /* Stay Visible */
            95% { transform: translateX(0); opacity: 0; } /* VERY QUICK FADE OFF */
            100% { transform: translateX(100vw); opacity: 0; }
        }
        
        div[data-testid="stVerticalBlock"] > div {
            z-index: 2; 
            position: relative;
        }

        /* === 🔥 FIXED GLASSMORPHISM (UPDATED SELECTOR) === */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2),
        div[data-testid="column"] > div:nth-child(2) {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            
            border-radius: 20px;
            border: 1px solid rgba(255, 75, 75, 0.5);
            box-shadow:
                0 8px 32px rgba(0, 0, 0, 0.5),
                0 0 15px rgba(255, 75, 75, 0.2),
                0 0 30px rgba(255, 75, 75, 0.1);
            
            padding: 2rem;
            animation: neon-pulse 4s ease-in-out infinite alternate;
        }

        @keyframes neon-pulse {
            0% {
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.5),
                    0 0 10px rgba(255, 75, 75, 0.1),
                    0 0 20px rgba(255, 75, 75, 0.05);
                border-color: rgba(255, 75, 75, 0.3);
            }
            100% {
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.6),
                    0 0 20px rgba(255, 75, 75, 0.4),
                    0 0 45px rgba(255, 75, 75, 0.2);
                border-color: rgba(255, 75, 75, 0.8);
            }
        }

    </style>

    <div class="animation-wrapper">
        <div class="anim-text g4-part">G4</div>
        <div class="anim-text solution-part">SOLUTION</div>
    </div>
    """, unsafe_allow_html=True)
    # === ANIMATION INJECTION END ===

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # === TYPEWRITER COMPONENT ===
        typewriter_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    background-color: transparent;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-family: 'Source Sans Pro', sans-serif;
                }
                .glass-card {
                    background-color: transparent; 
                    padding: 10px;
                    border-radius: 20px;
                    border: none;
                    text-align: center;
                    width: 100%;
                    max-width: 600px;
                    box-sizing: border-box;
                }
                .typewriter-container {
                    font-family: 'Courier New', monospace;
                    font-size: 1.5rem;
                    font-weight: 900;
                    color: #FF4B4B;
                    text-shadow: 0 0 5px rgba(255, 75, 75, 0.5);
                    text-align: center;
                    min-height: 40px;
                }
                .cursor {
                    display: inline-block;
                    width: 3px;
                    background: #FF4B4B;
                    margin-left: 3px;
                    animation: blink 0.6s infinite;
                    box-shadow: 0 0 5px #FF4B4B;
                }
                .subtitle {
                    margin: 0;
                    margin-top: 10px;
                    opacity: 0.8;
                    color: white;
                    font-size: 0.9rem;
                }
                @media (prefers-color-scheme: light) {
                    .subtitle { color: black; }
                }
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0; }
                }
            </style>
        </head>
        <body>
            <div class="glass-card">
                <div class="typewriter-container">
                    <span id="typewriter"></span><span class="cursor">&nbsp;</span>
                </div>
                <p class="subtitle">Login to access your personalized AI recommendations</p>
            </div>

            <script>
            const phrases = [
                "G4 SOLUTION CINEMA",
                "YOUR BEST AI MOVIE RECOMMENDER",
                "BY G4 SOLUTION",
                "PROUDLY FROM THRIVE AFRICA"
            ];

            let i = 0;
            let j = 0;
            let deleting = false;
            let speed = 80;
            let deleteSpeed = 40;
            let pause = 1500;

            function typeEffect() {
                const textElement = document.getElementById("typewriter");
                
                if (!textElement) return;

                if (!deleting) {
                    textElement.textContent = phrases[i].substring(0, j++);
                    if (j > phrases[i].length) {
                        deleting = true;
                        setTimeout(typeEffect, pause);
                        return;
                    }
                } else {
                    textElement.textContent = phrases[i].substring(0, j--);
                    if (j < 0) {
                        deleting = false;
                        i = (i + 1) % phrases.length;
                    }
                }
                setTimeout(typeEffect, deleting ? deleteSpeed : speed);
            }
            typeEffect();
            </script>
        </body>
        </html>
        """
        components.html(typewriter_html, height=130, scrolling=False)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        # --- LOGIN TAB ---
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

            # --- FORGOT PASSWORD SECTION ---
            with st.expander("❓ Forgot Password?"):
                if st.session_state.fp_step == 1:
                    fp_user = st.text_input("Enter Username to Reset", key="fp_user_in")
                    if st.button("Send OTP"):
                        db = load_db()
                        if fp_user in db:
                            user_email = db[fp_user].get('email')
                            if user_email:
                                otp_code = ''.join(random.choices(string.digits, k=6))
                                
                                with st.spinner("Sending OTP via Email..."):
                                    if send_otp_email(user_email, otp_code):
                                        st.session_state.fp_otp = otp_code
                                        st.session_state.fp_username = fp_user
                                        st.session_state.fp_step = 2
                                        st.toast(f"📧 OTP sent to {user_email}!", icon="✅")
                                        st.rerun()
                                    else:
                                        st.error("Failed to send email. Check credentials.")
                            else:
                                st.error("No email associated with this account.")
                        else:
                            st.error("Username not found.")

                elif st.session_state.fp_step == 2:
                    st.info(f"Enter the 6-digit code sent to the email for **{st.session_state.fp_username}**")
                    otp_input = st.text_input("OTP Code", key="otp_input")
                    
                    st.markdown("""
                    <div style="font-size: 0.8rem; color: gray; background: rgba(0,0,0,0.05); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #FF4B4B;">
                        <strong>Password Rules:</strong><br>
                        • Minimum 6 characters<br>
                        • At least 1 Number (0-9)<br>
                        • At least 1 Uppercase Letter (A-Z)
                    </div>
                    """, unsafe_allow_html=True)

                    new_pass = st.text_input("New Password", type="password", key="np_input")
                    conf_pass = st.text_input("Confirm Password", type="password", key="cp_input")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Reset Password", type="primary"):
                            if otp_input == st.session_state.fp_otp:
                                if new_pass == conf_pass:
                                    is_strong, msg = check_password_strength(new_pass)
                                    if is_strong:
                                        reset_password(st.session_state.fp_username, new_pass)
                                        st.success("✅ Password Reset Successfully! Login now.")
                                        st.session_state.fp_step = 1
                                        st.session_state.fp_otp = None
                                        st.session_state.fp_username = None
                                        st.rerun()
                                    else:
                                        st.error(msg)
                                else:
                                    st.error("Passwords do not match.")
                            else:
                                st.error("Invalid OTP.")
                    with c2:
                        if st.button("Cancel"):
                            st.session_state.fp_step = 1
                            st.session_state.fp_otp = None
                            st.rerun()

        # --- SIGN UP TAB ---
        with tab2:
            st.markdown("##### New User?")
            s_user = st.text_input("Choose Username", key="s_user")
            s_email = st.text_input("Enter Email", key="s_email")
            s_pass = st.text_input("Choose Password", type="password", key="s_pass")
            
            st.markdown("""
            <div style="font-size: 0.8rem; color: gray; background: rgba(0,0,0,0.05); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #FF4B4B;">
                <strong>Password Rules:</strong><br>
                • Minimum 6 characters<br>
                • At least 1 Number (0-9)<br>
                • At least 1 Uppercase Letter (A-Z)
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Create Account", use_container_width=True):
                if s_user and s_pass and s_email:
                    success, msg = register_user(s_user, s_email, s_pass)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = s_user
                        st.session_state.user_info = {
                            'email': s_email,
                            'password': hash_password(s_pass),
                            'user_id': msg, 
                            'history': []
                        }
                        st.success("Account created! Logging you in...")
                        st.rerun()
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

    # --- HELPER FUNCTION ---
    def find_movie_row(df, title):
        match = df[df['title'].str.lower().str.strip() == title.lower().strip()]
        if not match.empty:
            return match.iloc[0]
        match = df[df['title'].str.contains(title, case=False, na=False, regex=False)]
        if not match.empty:
            return match.iloc[0]
        return None

    # --- HISTORY POPUP DIALOG ---
    @st.dialog("📜 Historical Record")
    def show_history_popup(selected_movie, date, rec_titles):
        st.subheader(f"Source: {selected_movie}")
        st.caption(f"📅 Searched on: {date}")
        st.divider()
        
        display_text = ""
        for i, title in enumerate(rec_titles, 1):
            st.markdown(f"**{i}. {title}**")
            display_text += f"{i}. {title}\n"
            
        st.divider()
        
        export_string = f"History Export (G4 SOLUTION)\n\nMovie Searched: {selected_movie}\nDate: {date}\n\nRecommendations:\n{display_text}"
        
        st.download_button(
            label="💾 Download Record",
            data=export_string,
            file_name=f"History_{selected_movie.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # --- SESSION STATE ---
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'selected_movie_name' not in st.session_state:
        st.session_state.selected_movie_name = None
    if 'last_method' not in st.session_state:
        st.session_state.last_method = None

    # --- SIDEBAR ---
    with st.sidebar:
        # 1. Logo
        st.markdown("""
            <div style="text-align: center; font-weight: 800; font-size: 2rem;
                        padding: 10px; border: 2px solid #FF4B4B; border-radius: 15px;
                        background: rgba(255, 75, 75, 0.1); backdrop-filter: blur(5px);
                        margin-bottom: 20px; color: black;">
                G4 SOLUTION
            </div>
        """, unsafe_allow_html=True)

        # 2. User Info & Logout
        st.success(f"👤 **{st.session_state.username}**")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

        st.divider()

        # 3. Engine Selection
        filter_method = st.radio(
            " ", 
            ('Content-Based Filtering', 'Collaborative Filtering'),
            label_visibility="collapsed"
        )

        st.divider()

        # 4. History with Mini Buttons
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown("### 📜 History")
        with h_col2:
            if st.button("🗑️", help="Clear History"):
                clear_user_history(st.session_state.username)
                st.rerun()

        with st.expander("View Recent", expanded=False):
            db = load_db()
            history = db.get(st.session_state.username, {}).get('history', [])
            if not history:
                st.caption("No history.")
            else:
                for i, h in enumerate(reversed(history[-5:])):
                    hc1, hc2 = st.columns([4, 1])
                    with hc1:
                        st.markdown(f"**🎬 {h['selected_movie']}**")
                        st.caption(f"{h['timestamp']}")
                    with hc2:
                        if st.button("👁️", key=f"hist_btn_{i}", help="View & Download"):
                            show_history_popup(h['selected_movie'], h['timestamp'], h['recommendations'])
                    st.markdown("---")

        st.divider()

        # 5. Quick Links
        st.markdown("### 🚀 Quick Links")
        st.link_button("💬 Join WhatsApp Team", "https://chat.whatsapp.com/DsyWXB9DzG19CbTjK8dKhF?mode=hqrt2", use_container_width=True)
        st.link_button("📂 Access Notebook", "https://colab.research.google.com/drive/1XvRHy3z1cDWH51EuRegY_i-FWH2t2ypn?usp=drive_link", use_container_width=True)
        st.link_button("📚 Study With Thrive Africa", "https://thriveafrica.co/campus", use_container_width=True)

        st.divider()

        # 6. Team & About
        with st.expander("👥 Meet the Team"):
            team = [
                "1. Peter Agyekum", "2. Felicia I. Nduefuna", "3. Olivia Mawufemor Attipoe",
                "4. Donkor Promise Esi Rhoda", "5. Osborn Tulasi", "6. Onipayede John Kwaku",
                "7. Peter Agyekum Boateng", "8. Aning Jason", "9. Maxwell Adu",
                "10. Michael Nyarku", "11. Yeboah Eldad"
            ]
            for member in team:
                st.write(member)

        with st.expander("ℹ️ Details"):
            st.write("**Group 4 Final Project**")
            st.write("Course: **Machine Learning & AI**")
            st.write("Provider: **Thrive Africa**")
            st.write("Mentor: **Big Tamara**")

        st.divider()

        # 7. Delete Account
        @st.dialog("⚠️ Delete Account")
        def delete_account_dialog():
            st.warning("Permanently delete account?")
            if st.button("Yes, Delete", type="primary"):
                if delete_user_account(st.session_state.username):
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.rerun()

        if st.button("❌ Delete Account", type="primary", use_container_width=True):
            delete_account_dialog()

        st.divider()
        
        # 8. Dark Mode Toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=True)

    # --- THEME LOGIC ---
    if dark_mode:
        main_bg = "#0e1117"
        text_color = "#ffffff"
        label_color = "#FF4B4B"
        input_label_color = "#ffffff"
    else:
        main_bg = "#ffffff"
        text_color = "#000000"
        label_color = "#FF4B4B"
        input_label_color = "#8B0000"

    # --- CSS INJECTION ---
    st.markdown(f"""
        <style>
        /* MAIN APP COLORS */
        .stApp {{ background-color: {main_bg}; color: {text_color}; }}
        
        /* 1. RESTORE RED APP BAR & G4 SOLUTION */
        header[data-testid="stHeader"] {{
            background-color: #FF4B4B !important;
            height: 60px;
        }}
        header[data-testid="stHeader"]::after {{
            content: 'G4 SOLUTION';
            color: white;
            font-size: 20px;
            font-weight: 900;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 999;
            pointer-events: none;
        }}

        /* 2. FIX: CENTER EYE ICON & ALL SIDEBAR BUTTONS */
        [data-testid="stSidebar"] button div[data-testid="stButton"] {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        [data-testid="stSidebar"] button {{
            text-align: center !important;
            padding-right: 0 !important;
            padding-left: 0 !important;
        }}
        [data-testid="stSidebar"] button p {{
            width: 100%;
            text-align: center !important;
            margin: 0 auto !important;
        }}

        /* 3. MINIMIZED IMAGE WITH SHADOW */
        [data-testid="stImage"] img {{
            max-height: 200px;
            object-fit: cover;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(255, 75, 75, 0.3);
            transition: transform 0.3s ease;
        }}
        [data-testid="stImage"] img:hover {{
            transform: scale(1.02);
        }}

        /* 4. BUTTON ANIMATION ON HOVER */
        .stButton button, .stLinkButton a, div[data-testid="stDownloadButton"] button {{
            background-color: #f0f2f6 !important;
            color: #000000 !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }}
        .stButton button:hover, .stLinkButton a:hover, div[data-testid="stDownloadButton"] button:hover {{
            transform: scale(1.05) !important;
            background-color: #FF4B4B !important;
            color: white !important;
            border-color: #FF4B4B !important;
            box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4) !important;
        }}

        /* FORCE SIDEBAR WHITE */
        [data-testid="stSidebar"] {{
            background-color: #ffffff !important;
            border-right: 1px solid rgba(0,0,0,0.1) !important;
        }}
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] .stMarkdown {{
            color: #000000 !important;
        }}
        [data-testid="stSidebarCollapsedControl"] svg, [data-testid="stSidebarExpandedControl"] svg {{
            fill: #000000 !important;
            color: #000000 !important;
        }}

        /* MODERN RADIO BUTTON */
        div.row-widget.stRadio > label {{
            display: none !important;
        }}
        [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {{
            flex-direction: row;
            gap: 10px;
            margin-top: -20px !important;
        }}
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
            background-color: #f0f2f6 !important;
            padding: 10px 15px !important;
            border-radius: 8px !important;
            border: 1px solid #ddd !important;
            color: black !important;
            font-weight: 600 !important;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            text-align: center;
            display: flex;
            justify-content: center;
        }}
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] div[aria-checked="true"] + div label,
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] div[aria-checked="true"] label {{
            background-color: #FF4B4B !important;
            color: white !important;
            border-color: #FF4B4B !important;
        }}

        /* --- NEW PRO CARD STYLING (TEXT ONLY) --- */
        .rec-card {{
            /* Replaced image background with professional gradient */
            background: linear-gradient(135deg, #2b2b2b, #1a1a1a);
            border: 1px solid rgba(255, 75, 75, 0.2);
            border-radius: 15px;
            height: 350px; 
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }}
        
        .rec-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(255, 75, 75, 0.4);
            border-color: #FF4B4B;
        }}
        .card-content {{
            padding: 20px;
            z-index: 2;
            width: 100%;
            background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
        }}
        .movie-title {{
            font-size: 1.2rem;
            font-weight: 900;
            color: white;
            text-shadow: 0 0 10px rgba(255, 75, 75, 0.5);
            margin-bottom: 10px;
            line-height: 1.2;
        }}
        .movie-overview {{
            font-size: 0.8rem;
            color: #ccc;
            display: -webkit-box;
            -webkit-line-clamp: 6; 
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-top: 5px;
        }}

        /* INPUT LABELS */
        div[data-testid="stSelectbox"] > label {{
            color: {input_label_color} !important;
            font-weight: 900 !important;
            font-size: 1.2rem !important;
            animation: glow 1.5s ease-in-out infinite alternate;
        }}
        @keyframes glow {{ from {{ text-shadow: 0 0 2px {input_label_color}; }} to {{ text-shadow: 0 0 10px #FF4B4B; }} }}
        
        /* CONSTANT PULSE ANIMATION FOR HEADER */
        @keyframes breathing {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.03); text-shadow: 0 0 10px rgba(255, 75, 75, 0.3); }}
            100% {{ transform: scale(1); }}
        }}
        
        .main-header {{
            animation: breathing 3s infinite ease-in-out; 
            display: inline-block; 
        }}

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
            recommended_titles = []

            # 1. ENGINE SELECTION
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

            # 2. FETCH DETAILS (UPDATED: REMOVED IMAGES & META)
            result = []
            for title in recommended_titles:
                row = find_movie_row(movies_df, title)
                
                # Defaults
                overview = "No details available."

                if row is not None:
                    # Overview
                    if method == 'Content-Based Filtering':
                        overview = row.get("overview", "")
                        if pd.isna(overview): overview = "No details available."

                result.append({
                    'title': title,
                    'info': overview
                })

            return result

        except Exception as e:
            return []

    def clear_results():
        st.session_state.recommendations = None
        st.session_state.selected_movie_name = None

    # --- UI BODY ---
    st.image("https://preview.redd.it/can-i-see-all-the-movies-i-watched-in-2024-in-the-grid-view-v0-cog8js189l9e1.png?format=png&auto=webp&s=cb06477a6c7f54a331593c5a145d7023595d4d47", use_container_width=True)

    # HEADER WITH ANIMATION
    st.markdown('<h2 class="main-header" style="text-align: center; color: #FF4B4B; font-size: 3rem; font-weight: 800;">RECOMMEND WITH AI</h2>', unsafe_allow_html=True)

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
        
        cols = st.columns(5)
        
        for i, movie in enumerate(st.session_state.recommendations):
            with cols[i]:
                # Show overview only if it exists
                overview_html = f'<div class="movie-overview">{movie["info"]}</div>' if movie["info"] else ""
                
                # Render New Card HTML (Text Only)
                st.markdown(f"""
                <div class="rec-card">
                    <div class="card-content">
                        <div class="movie-title">{movie['title']}</div>
                        {overview_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.header("📥 Save & Watch")
        col_export, col_watch = st.columns([1, 2])
        
        with col_export:
            export_text = f"G4 SOLUTION Recommendations\nSource: {st.session_state.selected_movie_name}\n\n"
            for i, m in enumerate(st.session_state.recommendations, 1):
                export_text += f"{i}. {m['title']}\n"
                if m['info']: export_text += f"   {m['info']}\n"
                export_text += "\n"
            
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