# app.py
import streamlit as st
import random
import string
import time
import pandas as pd
from collections import Counter
from database import init_db, get_game_state, update_game_state

# --- Game Logic Helper Functions ---

def generate_room_id(length=4):
    """Generate a random, short, all-caps room ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def start_game(game_state: dict, num_beasts: int, include_hunter: bool):
    """Initializes the game state, assigning roles and setting the first round."""
    player_ids = [p['id'] for p in game_state['players']]
    num_players = len(player_ids)
    roles = ["Beast"] * num_beasts
    if include_hunter: roles.append("Hunter")
    roles.extend(["Villager"] * (num_players - len(roles)))
    random.shuffle(roles)
    
    game_state.update({
        'people': [{"id": pid, "role": role, "alive": True} for pid, role in zip(player_ids, roles)],
        'status': 'in_game',
        'phase': 'night',
        'current_round': 1,
        'votes': {},
        'round_results': ["The first night falls. A nervous silence blankets the village..."],
        'graveyard': [],
        'winner': None
    })
    return game_state

def check_win_conditions(game_state: dict):
    """Checks if a win condition is met and updates the game state."""
    alive_people = [p for p in game_state['people'] if p['alive']]
    beasts = [p for p in alive_people if p['role'] == 'Beast']
    villagers = [p for p in alive_people if p['role'] != 'Beast']

    if len(beasts) == 0:
        game_state['winner'] = "Villagers Win! 🎉"
    elif len(beasts) >= len(villagers):
        game_state['winner'] = "Beasts Win! 🐺"
    return game_state

def process_night_phase(game_state: dict):
    """Tallies night votes and eliminates a player."""
    votes = game_state.get('votes', {})
    if not votes:
        game_state['round_results'].append("The Beasts were indecisive and no one was eliminated.")
    else:
        vote_counts = Counter(votes.values())
        max_votes = max(vote_counts.values())
        targets = [p for p, v in vote_counts.items() if v == max_votes]
        eliminated_id = random.choice(targets)
        
        for p in game_state['people']:
            if p['id'] == eliminated_id:
                p['alive'] = False
                break
        
        game_state['graveyard'].append(f"**{eliminated_id}** ({p['role']}) - Eliminated in Night {game_state['current_round']}")
        game_state['round_results'].append(f"Dawn breaks. The village discovers that **{eliminated_id}** has been eliminated!")

    game_state['phase'] = 'day'
    game_state['votes'] = {} # Reset votes for the day phase
    return check_win_conditions(game_state)

def process_day_phase(game_state: dict):
    """Tallies day votes and banishes a player."""
    votes = game_state.get('votes', {})
    if not votes:
        game_state['round_results'].append("The village could not reach a consensus. No one was banished.")
    else:
        vote_counts = Counter(votes.values())
        max_votes = max(vote_counts.values())
        targets = [p for p, v in vote_counts.items() if v == max_votes]

        if len(targets) > 1:
            game_state['round_results'].append(f"The vote was tied between {', '.join(targets)}. No one is banished.")
        else:
            banished_id = targets[0]
            for p in game_state['people']:
                if p['id'] == banished_id:
                    p['alive'] = False
                    game_state['round_results'].append(f"The village has spoken. **{banished_id}** has been banished, revealing they were a **{p['role']}**!")
                    game_state['graveyard'].append(f"**{banished_id}** ({p['role']}) - Banished in Day {game_state['current_round']}")
                    break
    
    game_state['phase'] = 'night'
    game_state['current_round'] += 1
    game_state['votes'] = {}
    return check_win_conditions(game_state)

# --- UI Helper Functions ---
def display_sidebar(game_state):
    st.sidebar.header(f"Room: `{st.session_state.room_id}`")
    st.sidebar.subheader("🪦 Graveyard")
    if not game_state['graveyard']:
        st.sidebar.write("Empty for now...")
    else:
        for entry in game_state['graveyard']:
            st.sidebar.markdown(f"- {entry}")
    
    st.sidebar.subheader("📜 Game Log")
    for result in reversed(game_state['round_results']):
        st.sidebar.markdown(f"- {result}")

def display_spectator_view(game_state):
    """Shows the full game state with roles revealed for eliminated players."""
    st.header("You have been eliminated.")
    st.subheader("Spectator View")
    st.info("You can now see everyone's roles.")
    
    player_data = []
    for p in game_state['people']:
        status = "Alive 🟢" if p['alive'] else "Eliminated ❌"
        player_data.append([p['id'], p['role'], status])
    
    df = pd.DataFrame(player_data, columns=['Player', 'Secret Role', 'Status'])
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    display_sidebar(game_state)
    time.sleep(5)
    st.rerun()

# --- Main App ---
init_db()
st.set_page_config(layout="wide", page_title="Village Survival")
st.title("🐺 Village Survival 🧑‍🌾")

if 'room_id' not in st.session_state:
    st.header("Join or Create a Game Room")
    if st.button("Create a New Game", type="primary"):
        room_id = generate_room_id()
        player_id = "P1"
        initial_state = {
            "status": "lobby", 
            "players": [{"id": player_id, "name": "Player 1"}], 
            "host_id": player_id, 
            "game_config": {"num_beasts": 1, "include_hunter": True}
        }
        update_game_state(room_id, initial_state)
        st.session_state.room_id = room_id
        st.session_state.player_id = player_id
        st.rerun()

    st.markdown("---")
    join_room_id = st.text_input("Enter Room Code to Join:").upper()
    if st.button("Join Game"):
        if not join_room_id: st.error("Please enter a room code.")
        else:
            game_state = get_game_state(join_room_id)
            if game_state is None: st.error("Room not found.")
            elif game_state["status"] != "lobby": st.error("Game has already started.")
            else:
                player_count = len(game_state["players"])
                player_id = f"P{player_count + 1}"
                game_state["players"].append({"id": player_id, "name": f"Player {player_count + 1}"})
                update_game_state(join_room_id, game_state)
                st.session_state.room_id = join_room_id
                st.session_state.player_id = player_id
                st.rerun()
else:
    room_id = st.session_state.room_id
    player_id = st.session_state.player_id
    game_state = get_game_state(room_id)

    if game_state is None:
        st.error("Game room not found. Returning to main menu.")
        for key in list(st.session_state.keys()): del st.session_state[key]
        time.sleep(2); st.rerun()

    if game_state["status"] == "lobby":
        st.header(f"Lobby: `{room_id}`")
        st.write(f"You are **{player_id}**.")
        st.subheader("Players in Lobby:")
        for p in game_state["players"]: st.write(f"- {p['name']} {'(Host)' if p['id'] == game_state['host_id'] else ''}")
        if player_id == game_state["host_id"]:
            st.markdown("---")
            num_players = len(game_state["players"])
            if num_players < 3:
                st.warning("A minimum of 3 players is required to start.")
                st.button("Start Game", type="primary", disabled=True)
            else:
                st.subheader("Game Configuration")
                max_beasts = (num_players - 1) // 2
                if max_beasts < 1: max_beasts = 1
                if max_beasts > 1: num_beasts = st.slider("Number of Beasts 🐺", 1, max_beasts, 1)
                else: st.write("Number of Beasts 🐺: 1"); num_beasts = 1
                include_hunter = st.checkbox("Include Hunter? 🎯", value=True)
                game_state["game_config"] = {"num_beasts": num_beasts, "include_hunter": include_hunter}
                update_game_state(room_id, game_state)
                if st.button("Start Game", type="primary"):
                    config = game_state["game_config"]
                    new_game_state = start_game(game_state, config['num_beasts'], config['include_hunter'])
                    if new_game_state: update_game_state(room_id, new_game_state); st.rerun()
        else:
            st.info("Waiting for the host to configure and start the game...")
        time.sleep(3); st.rerun()

    elif game_state["status"] == "in_game":
        if game_state.get('winner'):
            st.header("Game Over!")
            st.success(f"**{game_state['winner']}**")
            st.balloons()
            display_spectator_view(game_state)
            st.stop()

        my_player_obj = next((p for p in game_state['people'] if p['id'] == player_id), None)
        if not my_player_obj or not my_player_obj['alive']:
            display_spectator_view(game_state)
            st.stop()

        display_sidebar(game_state)
        my_role = my_player_obj['role']
        st.header(f"Round {game_state['current_round']} - {game_state['phase'].title()} Phase")
        st.info(f"Your secret role is: **{my_role}**")
        if my_role == "Beast":
            beast_team = [p['id'] for p in game_state['people'] if p['role'] == "Beast" and p['alive']]
            st.warning(f"Your fellow Beasts are: {', '.join(beast_team)}")
        
        st.markdown("---")

        if game_state['phase'] == 'night':
            alive_beasts = {p['id'] for p in game_state['people'] if p['alive'] and p['role'] == 'Beast'}
            voted_beasts = {pid for pid in game_state.get('votes', {})}
            
            if my_role == 'Beast':
                alive_villagers = [p['id'] for p in game_state['people'] if p['alive'] and p['role'] != 'Beast']
                target = st.selectbox("Vote to eliminate:", alive_villagers, index=None, key=f"vote_{game_state['current_round']}")
                if st.button("Submit Vote"):
                    game_state.setdefault('votes', {})[player_id] = target
                    update_game_state(room_id, game_state); st.rerun()
                if player_id in game_state.get('votes', {}):
                    st.write(f"You have voted for: **{game_state['votes'][player_id]}**")
            else:
                st.info("The village is asleep. Wait for morning...")
            
            if alive_beasts.issubset(voted_beasts):
                st.info("All Beasts have voted. Processing the night...")
                time.sleep(2)
                new_game_state = process_night_phase(game_state)
                update_game_state(room_id, new_game_state)
                st.rerun()
        
        elif game_state['phase'] == 'day':
            st.info(game_state['round_results'][-1])
            st.subheader("Vote to banish a player")
            alive_players = {p['id'] for p in game_state['people'] if p['alive']}
            voted_players = {pid for pid in game_state.get('votes', {})}
            
            target = st.selectbox("Your vote:", [p for p in alive_players if p != player_id], index=None, key=f"vote_{game_state['current_round']}")
            if st.button("Submit Vote"):
                game_state.setdefault('votes', {})[player_id] = target
                update_game_state(room_id, game_state); st.rerun()
            if player_id in game_state.get('votes', {}):
                st.write(f"You have voted for: **{game_state['votes'][player_id]}**")
            
            if alive_players == voted_players:
                st.info("All players have voted. Processing the day...")
                time.sleep(2)
                new_game_state = process_day_phase(game_state)
                update_game_state(room_id, new_game_state)
                st.rerun()

        time.sleep(5); st.rerun()