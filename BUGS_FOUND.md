# Bugs Found During Testing

This document lists the bugs identified during testing of the **Village Survival Game** project.  
All bugs have also been reported individually as GitHub Issues.

---

## 1. Game does not update when player exits
- **Steps to Reproduce:** Start a game with multiple players, have one exit.  
- **Expected:** Remaining players’ game state updates instantly.  
- **Actual:** Game gets stuck after a player exits.  
- **Impact:** Blocks gameplay until restart.

---

## 2. Game restarts when a player refreshes page
- **Steps to Reproduce:** Start a game, one player refreshes browser.  
- **Expected:** Game should continue running.  
- **Actual:** Game restarts when refreshed.  
- **Impact:** Disrupts continuity of gameplay.

---

## 3. Wrong end-screen messages for losing team
- **Steps to Reproduce:** Play until Beasts or Villagers lose.  
- **Expected:** Losing team should see "You Lost."  
- **Actual:** Both teams see a same message.  
- **Impact:** Confusing feedback for players.

---

## 4. Incorrect elimination message after game ends
- **Steps to Reproduce:** Survive until the end of the game.  
- **Expected:** Surviving players should see "You Survived" or "You Won."  
- **Actual:** Message shown is "You have been eliminated."  
- **Impact:** Wrong result shown to players.

---

## 5. Maximum number of players not enforced
- **Steps to Reproduce:** Add players beyond maximum limit (e.g., more than 10).  
- **Expected:** System should prevent joining beyond limit.  
- **Actual:** No restriction on player count.  
- **Impact:** Causes imbalance and may lead to errors.

---

## Summary
These bugs highlight issues in **session state, game logic, and player limits**.  
Fixing them will improve stability and user experience.

---

*Reported by: [Your Name] (Tester)*
