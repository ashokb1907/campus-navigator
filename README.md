        # Campus Navigator Challenge

        ## Description
        The idea of the project is to develop a game for the open-day for the visitors to paly.
        ### Objective: 
        A game where the visitors can virtually tour the campus and collect objects or interactive items.
        Players will navigate to different locations, collect items related to fields of study, and learn about the campus in a fun, interactive way.
        ### Modules: Pygame
        ### Programming_language: Python


        This repository tracks the work done for every part of the project implemented.

        **A task objective i planed to achieve.**
        * [Development Plan](./docs/DEVELOPMENT_PLAN.md)

        **Documentation for my tutorials and references used**
        * [Literature Review](./LITERATURE_REVIEW.md)
        * [Resources](./RESOURCES.md)

        ---

        ## Current Status 

        * Basic Python and pygame setup.- IN PROGRESS
        * Literarture review and Resource Identification. -IN PROGRESS
        * Selection of controller and their compatibility. -TO BE STARTED
        ---

        ## Goals for Current Week

        * [x] Set up the Python project environment (install Pygame).
        * [x] Create the basic Pygame window.
        * [x] Implement basic controller detection and input handling (axis motion, hat motion).

        ## Methods to be identified
        * [x] Create a simple player character sprite (placeholder).
        * [x] Implement player movement controlled by the controller.
        * [x] Add basic screen boundary checks.

        ---

        ## Setup Instructions

        1.  **Clone the repository:**
            ```bash
            git clone https://github.com/ashokb1907/campus-navigator.git
            cd campus-navigator
            ```
        2.  **Create a virtual environment (Recommended):**
            ```bash
            python -m venv venv
            # On Windows we currently are running on windows
            .\venv\Scripts\activate
            # On macOS/Linux
            source venv/bin/activate
            ```
        3.  **Install dependencies:**
            ```bash
            pip install -r requirements.txt
            ```
            

        ---

        ## How to Run
        Note: This is how we are trying to implement.
        1.  Make sure your game controller is connected *before* running the script.
        2.  Navigate to the project directory in your terminal.
        3.  Ensure your virtual environment is activated (if you created one). Better option than running in Global ENV.
        4.  Run the main script:
            ```bash
            python main.py
            ```s
            *(to be changed once project is finalised)*

        ---

        ## Next Steps:

        * Implement map representation (drawing static obstacles).
        * Implement basic collision detection between the player and map obstacles.
        * Prevent player movement through obstacles.
         
