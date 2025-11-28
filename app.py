import streamlit as st
import random
import string
import time
import pandas as pd
from collections import Counter
from database import init_db, get_game_state, update_game_state
import base64
import os

# Initialize session state
if 'preloader_done' not in st.session_state:
    st.session_state.preloader_done = False
if 'profile_name' not in st.session_state:
    st.session_state.profile_name = None

# New helper function to embed local images using Base64
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        st.error(f"Error: Image file not found at {image_path}. Please check the file path.")
        return None
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# Path to your local image files
current_dir = os.path.dirname(os.path.abspath(__file__))
preloader_bg_path = os.path.join(current_dir, "preloder-backgrund.png")
preloader_logo_path = os.path.join(current_dir, "preloder_logo.png")
lobby_bg_path = os.path.join(current_dir, "advanced_lobby_background.png")

# Generate Base64 strings
preloader_bg_base64 = get_base64_image(preloader_bg_path)
preloader_logo_base64 = get_base64_image(preloader_logo_path)
lobby_bg_base64 = get_base64_image(lobby_bg_path)

# Custom CSS for Advanced UI with Animations, Transitions, and Game Theme
st.markdown(f"""
    <style>
    :root {{
        --primary-color: #4CAF50;
        --secondary-color: #2196F3;
        --text-color: #333;
        --beast-color: #8B4513; /* Brown for beasts */
    }}

    /* Target the main app container for the background image */
    [data-testid="stAppViewContainer"] {{
        background-image: var(--bg-image); /* Dynamic background set by apply_theme */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        transition: background-image 1s ease, background-color 1s ease;
    }}

    /* Ensure the main content block has a transparent background */
    .main {{
        background: transparent;
        color: var(--dynamic-text-color, #fff); /* Default text color, overridden by apply_theme */
    }}
    .stApp {{
        background-color: transparent;
        overflow: hidden;
    }}
    .st-emotion-cache-18ni7ap {{
        background-color: rgba(0,0,0,0); /* Sidebar color */
    }}
    .stButton>button {{
        background: #D9534F;
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: bold;
        transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
        border: 2px solid #D9534F;
        border-image-slice: 1;
        border-image-source: linear-gradient(45deg, #ff6b6b, #D9534F);
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(217, 83, 79, 0.7);
        background-color: #C94A46;
    }}
    .stButton>button:active {{
        transform: scale(0.95);
    }}
    /* New button for 'Join Game' */
    .st-emotion-cache-1c7y31u {{
        background: #2196F3 !important;
        color: white !important;
        border: 2px solid #2196F3 !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease !important;
    }}
    .st-emotion-cache-1c7y31u:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 0 15px rgba(33, 150, 243, 0.7) !important;
        background-color: #1A7BCB !important;
    }}
    .st-emotion-cache-1c7y31u:active {{
        transform: scale(0.95) !important;
    }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(5px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        padding: 24px;
        margin: 16px 0;
        animation: fadeInUp 0.5s ease;
        transition: transform 0.3s ease, opacity 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .glass-card:hover {{
        transform: translateY(-5px);
        opacity: 0.95;
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .stTextInput>div>div>input {{
        background-color: rgba(0, 0, 0, 0.5);
        border: 2px solid #D9534F;
        border-radius: 12px;
        padding: 12px;
        color: white;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }}
    .stTextInput>div>div>input:focus {{
        border-color: #2196F3;
        box-shadow: 0 0 10px #2196F3;
    }}
    .stSidebar {{ 
        background: rgba(0,0,0,0.5); 
        backdrop-filter: blur(10px); 
        transition: background 0.5s ease; 
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    .stSidebar:hover {{ background: rgba(0,0,0,0.7); }}
    .fade-in {{ animation: fadeIn 1s ease; }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .pulse {{ animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}

    /* Fireflies effect for preloader */
    .firefly {{
        position: absolute; /* Changed to absolute to be relative to preloader container */
        width: 5px;
        height: 5px;
        background-color: #ffd700;
        border-radius: 50%;
        opacity: 0.8;
        box-shadow: 0 0 5px #ffd700, 0 0 10px #ffd700;
        animation: moveFirefly 15s linear infinite;
        z-index: 1000;
    }}
    @keyframes moveFirefly {{
        0%, 100% {{ transform: translate(0, 0); opacity: 0.8; }}
        25% {{ transform: translate(100px, 50px) scale(1.2); opacity: 1; }}
        50% {{ transform: translate(200px, -100px) scale(1.1); opacity: 0.9; }}
        75% {{ transform: translate(-50px, -20px) scale(1.3); opacity: 1; }}
    }}
    /* Title Animations */
    .styled-h1 {{
        position: relative;
        text-align: center;
        color: white;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8), 0 0 15px rgba(255, 255, 255, 0.5);
        animation: neonGlow 2s infinite alternate, fadeInDown 1s ease;
        letter-spacing: 2px;
        font-family: 'Arial Black', sans-serif;
        margin-bottom: 20px;
    }}
    @keyframes neonGlow {{
        from {{ text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8), 0 0 15px rgba(255, 255, 255, 0.5); }}
        to {{ text-shadow: 2px 2px 10px rgba(0, 0, 0, 1), 0 0 20px rgba(255, 255, 255, 0.8); }}
    }}
    @keyframes fadeInDown {{
        from {{ opacity: 0; transform: translateY(-50px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    /* Preloader CSS */
    .preloader-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #212121;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        opacity: 1;
        transition: opacity 1s ease-in-out;
        background-image: url('{preloader_bg_base64}');
        background-size: cover;
        background-position: center;
    }}
    .preloader-container.hidden {{
        opacity: 0;
        pointer-events: none;
    }}
    .loader-content {{
        position: relative;
        width: 100%;
        max-width: 800px;
        text-align: center;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        animation: fadeInScale 1s ease-out forwards;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 20px;
    }}
    .loader-logo img {{
        width: 300px;
        height: auto;
        animation: pulseGlow 2s infinite;
        margin-bottom: 20px;
    }}
    @keyframes fadeInScale {{
        from {{ opacity: 0; transform: scale(0.8); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    @keyframes pulseGlow {{
        0% {{ transform: scale(1); filter: drop-shadow(0 0 5px rgba(255,200,0,0.5)); }}
        50% {{ transform: scale(1.05); filter: drop-shadow(0 0 15px rgba(255,220,0,0.8)); }}
        100% {{ transform: scale(1); filter: drop-shadow(0 0 5px rgba(255,200,0,0.5)); }}
    }}
    .villager, .beast {{
        font-size: 80px;
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
    }}
    .villager {{
        animation: villagerWalk 8s linear infinite alternate;
        left: 15%;
    }}
    .beast {{
        animation: beastProwl 10s linear infinite alternate;
        right: 15%;
    }}
    @keyframes villagerWalk {{
        0% {{ left: 15%; transform: translateY(-50%) scaleX(1); }}
        50% {{ left: 30%; transform: translateY(-50%) scaleX(1.1) rotate(5deg); }}
        100% {{ left: 15%; transform: translateY(-50%) scaleX(1); }}
    }}
    @keyframes beastProwl {{
        0% {{ right: 15%; transform: translateY(-50%) scaleX(1); }}
        50% {{ right: 30%; transform: translateY(-50%) scaleX(1.1) rotate(-5deg); }}
        100% {{ right: 15%; transform: translateY(-50%) scaleX(1); }}
    }}
    .loading-text {{
        font-size: 24px;
        margin-top: 30px;
        animation: pulseText 1.5s infinite;
    }}
    @keyframes pulseText {{
        0% {{ opacity: 0.7; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.7; }}
    }}
    .progress-bar-container {{
        width: 300px;
        height: 15px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        margin-top: 10px;
        overflow: hidden;
    }}
    .progress-bar {{
        width: 0;
        height: 100%;
        background: linear-gradient(to right, #4CAF50, #8BC34A);
        animation: fillProgress 3s ease-out forwards;
    }}
    @keyframes fillProgress {{
        to {{ width: 100%; }}
    }}
    </style>
""", unsafe_allow_html=True)

# Dynamic Theme for Day/Night and Lobbies
def apply_theme(phase):
    bg_image_url = ""
    text_color = '#fff' # Default to white for dark backgrounds
    
    if phase == 'lobby':
        bg_image_url = f"url('{lobby_bg_base64}')"
        text_color = '#fff' 
    elif phase == 'night':
        bg_image_url = "url('https://t4.ftcdn.net/jpg/06/33/60/05/360_F_633600526_edh4jh26g6EPOS3vTand9qJoHCce0FdZ.jpg')"
        text_color = '#fff'
    else: # Day
        bg_image_url = "url('https://t4.ftcdn.net/jpg/06/33/60/05/360_F_633600526_edh4jh26g6EPOS3vTand9qJoHCce0FdZ.jpg')"
        text_color = '#333' # Darker text for lighter day background
    
    # Apply CSS variables to the root element for dynamic changes
    st.markdown(f"""
        <style>
        :root {{
            --bg-image: {bg_image_url};
            --dynamic-text-color: {text_color};
        }}
        .st-emotion-cache-183s8p6 {{ /* Targets header/title specifically if needed */
            color: {text_color};
        }}
        </style>
    """, unsafe_allow_html=True)

    # Particles are no longer generated here; they are in the preloader or specific containers if needed.
    return "" 

# Game Logic (Unchanged)
def generate_room_id(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def start_game(game_state: dict, num_beasts: int, include_hunter: bool):
    player_ids = [p['id'] for p in game_state['players']]
    num_players = len(player_ids)
    roles = ["Beast"] * num_beasts
    if include_hunter: roles.append("Hunter")
    roles.extend(["Villager"] * (num_players - len(roles)))
    random.shuffle(roles)
    
    people = []
    for i, player in enumerate(game_state['players']):
        people.append({
            "id": player['id'],
            "role": roles[i],
            "alive": True,
            "name": player['name']
        })
    
    game_state.update({
        'people': people,
        'status': 'in_game',
        'phase': 'night',
        'current_round': 1,
        'votes': {},
        'hunter_votes': {},
        'round_results': ["The first night falls. A nervous silence blankets the village..."],
        'graveyard': [],
        'winner': None
    })
    return game_state

def check_win_conditions(game_state: dict):
    alive_people = [p for p in game_state['people'] if p['alive']]
    beasts = [p for p in alive_people if p['role'] == 'Beast']
    villagers = [p for p in alive_people if p['role'] != 'Beast']
    if len(beasts) == 0:
        game_state['winner'] = "Villagers Win! 🎉"
    elif len(beasts) >= len(villagers):
        game_state['winner'] = "Beasts Win! 🐺"
    return game_state

def process_night_phase(game_state: dict):
    votes = game_state.get('votes', {})
    hunter_votes = game_state.get('hunter_votes', {})
    
    if not votes:
        game_state['round_results'].append("The Beasts were indecisive and no one was eliminated.")
        eliminated_id = None
    else:
        vote_counts = Counter(votes.values())
        max_votes = max(vote_counts.values())
        targets = [p for p, v in vote_counts.items() if v == max_votes]
        eliminated_id = random.choice(targets)
        
        if hunter_votes and eliminated_id in hunter_votes.values():
            eliminated_name = next(p['name'] for p in game_state['people'] if p['id'] == eliminated_id)
            game_state['round_results'].append(f"The Hunter protected **{eliminated_name}** from the Beasts' attack! No one was eliminated.")
            eliminated_id = None
    
    if eliminated_id:
        for p in game_state['people']:
            if p['id'] == eliminated_id:
                p['alive'] = False
                role = p['role']
                name = p['name']
                break
        game_state['graveyard'].append(f"**{name}** ({role}) - Eliminated in Night {game_state['current_round']}")
        game_state['round_results'].append(f"Dawn breaks. The village discovers that **{name}** has been eliminated!")

    game_state['phase'] = 'day'
    game_state['votes'] = {}
    game_state['hunter_votes'] = {}
    return check_win_conditions(game_state)

def process_day_phase(game_state: dict):
    votes = game_state.get('votes', {})
    if not votes:
        game_state['round_results'].append("The village could not reach a consensus. No one was banished.")
    else:
        vote_counts = Counter(votes.values())
        max_votes = max(vote_counts.values())
        targets = [p for p, v in vote_counts.items() if v == max_votes]
        if len(targets) > 1:
            game_state['round_results'].append(f"The vote was tied between {', '.join([next(p['name'] for p in game_state['people'] if p['id'] == t) for t in targets])}. No one is banished.")
        else:
            banished_id = targets[0]
            for p in game_state['people']:
                if p['id'] == banished_id:
                    p['alive'] = False
                    name = p['name']
                    game_state['round_results'].append(f"The village has spoken. **{name}** has been banished, revealing they were a **{p['role']}**!")
                    game_state['graveyard'].append(f"**{name}** ({p['role']}) - Banished in Day {game_state['current_round']}")
                    break
    
    game_state['phase'] = 'night'
    game_state['current_round'] += 1
    game_state['votes'] = {}
    return check_win_conditions(game_state)

# UI Helpers
def display_sidebar(game_state):
    st.sidebar.header(f"Room: `{st.session_state.room_id}`", divider='blue')
    with st.sidebar.expander("🪦 Graveyard", expanded=True):
        if not game_state['graveyard']:
            st.write("Empty for now...")
        else:
            df = pd.DataFrame(game_state['graveyard'], columns=["Graveyard"])
            st.dataframe(df.style.set_properties(**{'background-color': 'rgba(255,255,255,0.1)', 'color': 'inherit'}), use_container_width=True)
    
    with st.sidebar.expander("📜 Game Log", expanded=True):
        for result in reversed(game_state['round_results']):
            st.markdown(f"<p class='fade-in' style='color: inherit;'>{result}</p>", unsafe_allow_html=True)

def display_spectator_view(game_state):
    st.header("You have been eliminated.", divider='red')
    st.subheader("Spectator View")
    st.info("You can now see everyone's roles.")
    
    player_data = [[p['id'], p['name'], p['role'], "Alive 🟢" if p['alive'] else "Eliminated ❌"] for p in game_state['people']]
    df = pd.DataFrame(player_data, columns=['Player ID', 'Name', 'Secret Role', 'Status'])
    st.dataframe(df.style.set_properties(**{'background-color': 'rgba(255,255,255,0.1)', 'color': 'inherit'}), hide_index=True, use_container_width=True)
    
    display_sidebar(game_state)
    time.sleep(5)
    st.rerun()

# Main App
init_db()
st.set_page_config(layout="wide", page_title="Village Survival: Epic Edition", page_icon="🐺")

# Themed Preloader with Moving Beasts and Villagers and now Fireflies
if not st.session_state.preloader_done:
    # Generate fireflies for the preloader
    firefly_particles_html = ""
    for i in range(25):
        size = random.randint(2, 6)
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        delay = random.uniform(0, 15)
        firefly_particles_html += f"""
            <div class="firefly" style="width:{size}px; height:{size}px; left:{left}%; top:{top}%; animation-delay:{delay}s; animation-duration:{random.uniform(10, 20)}s;"></div>
        """

    if preloader_bg_base64 and preloader_logo_base64:
        st.markdown(f"""
            <div class="preloader-container">
                {firefly_particles_html} <div class="loader-content">
                    <div class="villager">🧑‍🌾</div>
                    <img class="loader-logo" src="{preloader_logo_base64}" alt="Village Survival Logo">
                    <div class="beast">🐺</div>
                    <div class="loading-text">Loading the Village...</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar"></div>
                    </div>
                </div>
            </div>
            <script>
                setTimeout(function() {{
                    document.querySelector('.preloader-container').classList.add('hidden');
                }}, 3000); // 3-second delay for the preloader
            </script>
        """, unsafe_allow_html=True)
        
        st.audio("https://assets.mixkit.co/sfx/preview/mixkit-wolf-howl-1365.mp3", format="audio/mp3", start_time=0)
        time.sleep(3)
        st.session_state.preloader_done = True
        st.rerun()
    else:
        st.warning("Preloader assets not found. Check the file paths and names.")
        time.sleep(3)
        st.session_state.preloader_done = True
        st.rerun()

# Title with Animation
st.markdown("<h1 class='styled-h1'>🐺 Village Survival: Epic Edition 🧑‍🌾</h1>", unsafe_allow_html=True)

# Main Menu
if 'room_id' not in st.session_state or st.session_state.profile_name is None:
    apply_theme('lobby') # Apply lobby background
    
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card fade-in'>", unsafe_allow_html=True)
        st.header("Create or Join a Game Room", divider='green')
        with st.form("room_form"):
            input_name = st.text_input("Your Name", placeholder="Enter your profile name", key="input_name")
            col1, col2 = st.columns([3, 1])
            with col1:
                join_room_id = st.text_input("Enter Room Code:", placeholder="e.g., AB12").upper()
            with col2:
                st.write("")  # Spacer
                join_submitted = st.form_submit_button("Join Game", help="Join an existing game room")
            create_submitted = st.form_submit_button("Create New Game", type="primary", help="Create a new room and become the host")
            
            if create_submitted:
                if not input_name:
                    st.error("Please enter your name.")
                else:
                    room_id = generate_room_id()
                    player_id = "P1"
                    initial_state = {
                        "status": "lobby",
                        "players": [{"id": player_id, "name": input_name}],
                        "host_id": player_id,
                        "game_config": {"num_beasts": 1, "include_hunter": True}
                    }
                    update_game_state(room_id, initial_state)
                    st.session_state.room_id = room_id
                    st.session_state.player_id = player_id
                    st.session_state.profile_name = input_name
                    st.rerun()
            if join_submitted:
                if not input_name:
                    st.error("Please enter your name.")
                elif not join_room_id:
                    st.error("Please enter a room code.")
                else:
                    game_state = get_game_state(join_room_id)
                    if game_state is None:
                        st.error("Room not found.")
                    elif game_state["status"] != "lobby":
                        st.error("Game has already started.")
                    else:
                        player_count = len(game_state["players"])
                        player_id = f"P{player_count + 1}"
                        game_state["players"].append({"id": player_id, "name": input_name})
                        update_game_state(join_room_id, game_state)
                        st.session_state.room_id = join_room_id
                        st.session_state.player_id = player_id
                        st.session_state.profile_name = input_name
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    room_id = st.session_state.room_id
    player_id = st.session_state.player_id
    player_name = st.session_state.profile_name or "Guest"
    game_state = get_game_state(room_id)

    if game_state is None:
        st.error("Game room not found. Returning to main menu.")
        for key in list(st.session_state.keys()): del st.session_state[key]
        time.sleep(2); st.rerun()

    apply_theme(game_state.get('phase', 'lobby')) # Apply theme based on game phase

    if game_state["status"] == "lobby":
        st.markdown("<div class='glass-card fade-in'>", unsafe_allow_html=True)
        st.header(f"Lobby: `{room_id}`", divider='blue')
        st.write(f"You are **{player_name}** ({player_id}).")
        st.subheader("Players in Lobby:")
        for p in game_state["players"]:
            st.write(f"- {p['name']} ({p['id']}) {'(Host)' if p['id'] == game_state['host_id'] else ''}")
        
        if player_id == game_state["host_id"]:
            num_players = len(game_state["players"])
            if num_players < 3:
                st.warning("A minimum of 3 players is required to start.")
                st.button("Start Game", type="primary", disabled=True)
            else:
                with st.expander("Game Configuration", expanded=True):
                    max_beasts = (num_players - 1) // 2 or 1
                    if max_beasts == 1:
                        st.write("Number of Beasts 🐺: 1 (Only one beast possible with few players)")
                        num_beasts = 1
                    else:
                        num_beasts = st.slider("Number of Beasts 🐺", 1, max_beasts, 1, help="Beasts eliminate one player each night.")
                    include_hunter = st.checkbox("Include Hunter? 🎯", value=True, help="Hunter protects one player per night.")
                    game_state["game_config"] = {"num_beasts": num_beasts, "include_hunter": include_hunter}
                    update_game_state(room_id, game_state)
                    if st.button("Start Game", type="primary"):
                        config = game_state["game_config"]
                        new_game_state = start_game(game_state, config['num_beasts'], config['include_hunter'])
                        update_game_state(room_id, new_game_state)
                        st.rerun()
        else:
            st.info("Waiting for the host to configure and start the game...")
        time.sleep(3); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif game_state["status"] == "in_game":
        if game_state.get('phase') == 'night':
            st.audio("https://assets.mixkit.co/sfx/preview/mixkit-wolf-howl-1365.mp3", format="audio/mp3", start_time=0)
        elif game_state.get('phase') == 'day':
            st.audio("https://audio-previews.elements.envatousercontent.com/files/15696615/preview.mp3", format="audio/mp3", start_time=0)
        
        if game_state.get('winner'):
            st.markdown("<div class='glass-card fade-in'>", unsafe_allow_html=True)
            st.header("Game Over!", divider='red')
            winner_color = 'green' if 'Villagers' in game_state['winner'] else 'red'
            st.markdown(f"<h2 class='pulse' style='color: {winner_color}; text-align: center;'>{game_state['winner']}</h2>", unsafe_allow_html=True)
            st.balloons()
            display_spectator_view(game_state)
            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()

        my_player_obj = next((p for p in game_state['people'] if p['id'] == player_id), None)
        if not my_player_obj or not my_player_obj['alive']:
            st.markdown("<div class='glass-card fade-in'>", unsafe_allow_html=True)
            display_spectator_view(game_state)
            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()

        st.markdown("<div class='glass-card fade-in'>", unsafe_allow_html=True)
        display_sidebar(game_state)
        st.header(f"Round {game_state['current_round']} - {game_state['phase'].title()} Phase", divider='violet')
        st.info(f"Your secret role is: **{my_player_obj['role']}**")
        if my_player_obj['role'] == "Beast":
            beast_team = [p['name'] for p in game_state['people'] if p['role'] == "Beast" and p['alive']]
            st.warning(f"Your fellow Beasts: {', '.join(beast_team)}")
        elif my_player_obj['role'] == "Hunter":
            st.success("As Hunter, protect one player from the Beasts each night!")

        tab1, tab2, tab3 = st.tabs(["Current Phase", "Game Log", "Graveyard"])
        with tab1:
            if game_state['phase'] == 'night':
                alive_beasts = {p['id'] for p in game_state['people'] if p['alive'] and p['role'] == 'Beast'}
                voted_beasts = {pid for pid in game_state.get('votes', {})}
                alive_hunters = {p['id'] for p in game_state['people'] if p['alive'] and p['role'] == 'Hunter'}
                voted_hunters = {pid for pid in game_state.get('hunter_votes', {})}
                
                if my_player_obj['role'] == 'Beast':
                    alive_villagers = [p['name'] for p in game_state['people'] if p['alive'] and p['role'] != 'Beast']
                    if not alive_villagers:
                        st.warning("No targets left.")
                    else:
                        target = st.selectbox("Vote to eliminate:", alive_villagers, index=None, key=f"beast_vote_{game_state['current_round']}")
                        if st.button("Submit Attack Vote"):
                            if not target:
                                st.error("Select a target.")
                            else:
                                target_id = next(p['id'] for p in game_state['people'] if p['name'] == target)
                                game_state.setdefault('votes', {})[player_id] = target_id
                                update_game_state(room_id, game_state)
                                st.rerun()
                        if player_id in game_state.get('votes', {}):
                            st.write(f"You voted for: **{next(p['name'] for p in game_state['people'] if p['id'] == game_state['votes'][player_id])}**")
                
                elif my_player_obj['role'] == 'Hunter':
                    alive_players = [p['name'] for p in game_state['people'] if p['alive']]
                    protect_target = st.selectbox("Protect a player:", alive_players, index=None, key=f"hunter_protect_{game_state['current_round']}")
                    if st.button("Submit Protection"):
                        if not protect_target:
                            st.error("Select a player to protect.")
                        else:
                            target_id = next(p['id'] for p in game_state['people'] if p['name'] == protect_target)
                            game_state.setdefault('hunter_votes', {})[player_id] = target_id
                            update_game_state(room_id, game_state)
                            st.rerun()
                    if player_id in game_state.get('hunter_votes', {}):
                        st.write(f"You are protecting: **{next(p['name'] for p in game_state['people'] if p['id'] == game_state['hunter_votes'][player_id])}**")
                
                else:
                    st.info("The village sleeps... Await dawn.")
                
                if alive_beasts.issubset(voted_beasts) and alive_hunters.issubset(voted_hunters):
                    st.info("All votes in. Processing night...")
                    with st.spinner("Night falls..."):
                        time.sleep(2)
                    new_game_state = process_night_phase(game_state)
                    update_game_state(room_id, new_game_state)
                    st.rerun()
            
            elif game_state['phase'] == 'day':
                st.info(game_state['round_results'][-1])
                st.subheader("Vote to Banish")
                alive_players = {p['id']: p['name'] for p in game_state['people'] if p['alive']}
                voted_players = {pid for pid in game_state.get('votes', {})}
                
                target = st.selectbox("Your vote:", [name for pid, name in alive_players.items() if pid != player_id], index=None, key=f"day_vote_{game_state['current_round']}")
                if st.button("Submit Banish Vote"):
                    if not target:
                        st.error("Select a target.")
                    else:
                        target_id = next(pid for pid, name in alive_players.items() if name == target)
                        game_state.setdefault('votes', {})[player_id] = target_id
                        update_game_state(room_id, game_state)
                        st.rerun()
                if player_id in game_state.get('votes', {}):
                    st.write(f"You voted for: **{alive_players.get(game_state['votes'][player_id], 'Unknown')}**")
                
                if set(alive_players.keys()) == voted_players:
                    st.info("All votes in. Processing day...")
                    with st.spinner("Day deliberations..."):
                        time.sleep(2)
                    new_game_state = process_day_phase(game_state)
                    update_game_state(room_id, new_game_state)
                    st.rerun()
        
        with tab2:
            for result in reversed(game_state['round_results']):
                st.markdown(f"<p class='fade-in' style='color: inherit;'>{result}</p>", unsafe_allow_html=True)
        
        with tab3:
            if not game_state['graveyard']:
                st.write("Empty for now...")
            else:
                df = pd.DataFrame(game_state['graveyard'], columns=["Graveyard"])
                st.dataframe(df.style.set_properties(**{'background-color': 'rgba(255,255,255,0.1)', 'color': 'inherit'}), use_container_width=True)
        
        time.sleep(5); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)