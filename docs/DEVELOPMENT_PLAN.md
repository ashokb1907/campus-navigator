## Campus Navigator Challenge: Development Plan

This document is a rough roademap on how i want to achieve the task objective.Main focus would be to be work on the core functionality and adding features to it.

---

### Phase 1: Setting the Foundation

* **Goal:** Get the basic game window running and player movement working with a controller.
* **Tasks:**
    * Set up a  github repository .(Profeesional one.)
    * Initialize Pygame and create the main game window.
    * Detect connected controllers and handle their basic input.Trying to find most generic controller available.
    * Create a simple character or dot for the player.
    * Implement player movement logic based on controller input like a snake game.
    * Ensure the player stays within the screen boundaries like some obstacle dection.

---

### Phase 2: Building the World & Interaction

* **Goal:** Create a simple environment for the player to navigate and interact with.
* **Tasks:**
    * Design and draw a basic map layout (representing walls, paths, or buildings).
    * Implement collision detection so the player cannot move through walls/obstacles.
    * Define specific "destination" points on the map.
    * Visually represent these destinations.
    * Detect when the player reaches a destination.

---

### Phase 3: Adding Gameplay Elements

* **Goal:** Introduce objectives, scoring, and challenges to make it feel like a game.
* **Tasks:**
    * Create a simple User Interface (UI) to display information (like current objective, score, time).
    * Implement a system to give the player objectives (e.g., "Go to the Library").
    * Update the objective when a destination is reached.
    * Add collectible items ("knowledge points") to the map.
    * Implement item collection logic (detect collision, remove item).
    * Add a scoring system (points for items/destinations).
    * Implement a countdown timer for the game session.

---

### Phase 4: Enhancing the Experience

* **Goal:** Improve the look and feel of the game with better visuals and audio.
* **Tasks:**
    * Replace placeholder graphics with actual sprites/images for the player, map elements, items, and destinations.
    * Refine the feel of player movement and collision response.
    * (Optional) Add simple sound effects for key actions (collecting items, reaching destinations).
    * Create a basic start screen or menu.

---

### Phase 5: Finishing Touches & Testing

* **Goal:** Ensure the game is complete, stable, and easy to understand.
* **Tasks:**
    * Implement clear game states (e.g., Start Menu, Playing, Game Over/Win).
    * Define win/loss conditions (e.g., reach all goals vs. time runs out).
    * Add instructions on how to play (on the start screen or a help screen).
    * Thoroughly test the game, checking for bugs, controller issues, and gameplay balance.
    * Review and clean up the code, adding comments for clarity.
    * Prepare final documentation.

---

This is a rough sketch formulated by reading resources will change further on professor input.