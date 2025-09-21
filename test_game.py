# test_game.py
import pytest
from app import check_win_conditions, process_night_phase, process_day_phase

def make_game_state(roles):
    """Helper: create a game state with given roles."""
    return {
        "people": [{"id": f"P{i+1}", "role": role, "alive": True} for i, role in enumerate(roles)],
        "status": "in_game",
        "phase": "night",
        "current_round": 1,
        "votes": {},
        "round_results": [],
        "graveyard": [],
        "winner": None,
    }

# ---------------------------
# BASIC TEST CASES
# ---------------------------

def test_all_villagers_win():
    state = make_game_state(["Villager", "Villager", "Villager"])
    state = check_win_conditions(state)
    assert state["winner"] == "Villagers Win! 🎉"

def test_all_beasts_win():
    state = make_game_state(["Beast", "Beast"])
    state = check_win_conditions(state)
    assert state["winner"] == "Beasts Win! 🐺"

def test_one_villager_one_beast():
    state = make_game_state(["Villager", "Beast"])
    state = check_win_conditions(state)
    assert state["winner"] == "Beasts Win! 🐺"

# ---------------------------
# MEDIUM TEST CASES
# ---------------------------

def test_equal_villagers_and_beasts():
    state = make_game_state(["Villager", "Villager", "Beast", "Beast"])
    state = check_win_conditions(state)
    # Beasts equal villagers => beasts win
    assert state["winner"] == "Beasts Win! 🐺"

def test_one_round_mixed_roles():
    state = make_game_state(["Villager", "Beast", "Villager"])
    state["votes"] = {"P2": "P1"}  # Beast votes at night
    state = process_night_phase(state)
    assert not state["people"][0]["alive"]  # P1 eliminated
    assert state["phase"] == "day"

# ---------------------------
# COMPLEX TEST CASES
# ---------------------------

def test_multiple_rounds():
    state = make_game_state(["Villager", "Villager", "Beast"])
    
    # Round 1 - Night: Beast eliminates P1
    state["votes"] = {"P3": "P1"}
    state = process_night_phase(state)
    assert not state["people"][0]["alive"]

    # Round 1 - Day: P2 votes to banish Beast
    state["votes"] = {"P2": "P3"}
    state["phase"] = "day"
    state = process_day_phase(state)
    assert not state["people"][2]["alive"]
    assert state["winner"] == "Villagers Win! 🎉"

def test_large_group_game():
    roles = ["Villager"] * 8 + ["Beast"] * 2
    state = make_game_state(roles)
    state = check_win_conditions(state)
    assert state["winner"] is None  # Game still ongoing

def test_invalid_votes_no_elimination():
    state = make_game_state(["Villager", "Villager", "Beast"])
    state["votes"] = {}  # no one voted
    state = process_day_phase(state)
    assert all(p["alive"] for p in state["people"])  # nobody eliminated
