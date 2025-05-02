# Campus Navigator

## Description

This project aims to develop an interactive game for university open days. Visitors can play the game to take a virtual tour of the campus, discover locations, and learn about different fields of study in a fun way.

**Objective:**

* Create a game where visitors virtually tour the campus.
* Allow players to navigate to different locations and collect items related to fields of study.
* Provide an engaging and informative experience about the campus.

**Technology:**

* **Module:** Pygame
* **Language:** Python

---

## Project Documents

This repository tracks the development progress. Key planning and research documents can be found below:

* **Development Plan:** [./docs/DEVELOPMENT_PLAN.md](./docs/DEVELOPMENT_PLAN.md) - Outlines the planned stages and features.
* **Literature Review:** [./LITERATURE_REVIEW.md](./LITERATURE_REVIEW.md) - Research and background study.
* **Resources:** [./RESOURCES.md](./RESOURCES.md) - Useful links, tutorials, and assets used.

---

## Current Status

* Basic Python and Pygame setup. *(In Progress)*
* Literature review and resource identification. *(In Progress)*
* Selection of controller and compatibility testing. *(To Be Started)*
* Map representation and collision detection. *(To Be Started)*

---

## Key Features & Milestones

This section tracks the implementation progress of core features:

* [x] Set up the Python project environment (install Pygame).
* [x] Create the basic Pygame window.
* [x] Implement basic controller detection and input handling (axis motion, hat motion).
* [x] Create a simple player character sprite (placeholder).
* [x] Implement player movement controlled by the controller.
* [x] Add basic screen boundary checks.
* [ ] Implement map representation (drawing static obstacles).
* [ ] Implement basic collision detection between the player and map obstacles.
* [ ] Prevent player movement through obstacles.

*(You can update the checkboxes `[ ]` to `[x]` as you complete tasks.)*

---

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ashokb1907/campus-navigator.git](https://github.com/ashokb1907/campus-navigator.git)
    cd campus-navigator
    ```

2.  **Create and activate a virtual environment (Recommended):**
    * On **Windows**:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * On **macOS/Linux**:
        ```bash
        python -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    *(Ensure the `requirements.txt` file is present in the repository. If not, you may need to create it based on the project's needs, e.g., `pip freeze > requirements.txt` after installing packages like Pygame).*
    ```bash
    pip install -r requirements.txt
    ```

---

## How to Run

1.  Make sure your game controller is connected *before* running the script.
2.  Navigate to the project directory in your terminal.
3.  Ensure your virtual environment is activated (if you created one).
4.  Run the main script:
    ```bash
    python main.py
    ```
    *(Note: The entry point script `main.py` might change as the project evolves.)*

---

## Next Steps

* Refine map implementation and add more detail.
* Develop the item collection mechanic.
* Create UI elements (e.g., score, collected items).
* Design final sprites and assets.
