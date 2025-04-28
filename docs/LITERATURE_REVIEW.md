# Literature Review: Campus Navigator Challenge

**Note: This is written as a basic draft of my understanding in reading various resources and summarizing them**

## 1. Introduction

This literature review is intended for the development of the "Campus Navigator Challenge," a 2D game using Python/Pygame designed for an Aston College open day. The game's objective is to familiarize visitors with the campus layout and different fields of engineering we provide, using the controller as an input. This review includes relevant topics from educational game design (serious games), player motivation, cognitive load, usability for novice players, accessibility, spatial navigation in virtual environments, and Pygame to inform the project's design and implementation.

## 2. Serious Games and Educational Effectiveness

The use of games for purposes beyond pure entertainment, often termed "serious games," has gained popularity in education and training. Key design principles for effective educational games include setting clear goals and objectives, establishing structured rules, providing real-time feedback, and encouraging voluntary participation. Goals provide purpose and structure, while feedback mechanisms allow learners to adjust strategies and track progress, creating a sense of accomplishment. The game design should be implemented in such a way that it would be easy for the user to follow through.

 Educational games have demonstrated effectiveness in enhancing knowledge, developing skills, and influencing attitudes by providing realistic and engaging, learning environments. They can bridge the gap between theoretical knowledge and practical application, offering opportunities for experiential learning in a safe setting where failure is a learning opportunity rather than a penalty. For orientation purposes, like introducing a campus, a game can offer an active, experience. The "Campus Navigator Challenge" aims to leverage these principles by setting clear navigation goals (find departments), providing implicit rules (navigate the map), and offering feedback (reaching a destination, collecting items), while keeping the interface simple for the users.

## 3. Player Motivation, Engagement, and Usability

Designing compelling experiences, particularly in instructional games, requires an understanding of player motivation. According to the widely used Self-Determination Theory (SDT), motivation is driven by meeting the basic needs for **autonomy** (control, meaningful choices), **competence** (effectiveness, mastering challenges), and **relatedness** (social connection, though less important in short, single-player sessions). Games can promote competence by striking a balance between ability and challenge, and autonomy through choices—even basic path choices. Intrinsic motivation can also be improved by aspects of fantasy and curiosity.

Effective game design, particularly for a broad audience such as novice players at an open day, is dependent on solid usability standards. Core mechanics should be straightforward and compelling, allowing players to interact naturally. The user interface (UI), which includes controls and menus, must be simple to learn and use, reducing cognitive burden and allowing players to focus on gaming. For brief sessions like an open day, immediate clarity, quick feedback loops, and easily attainable initial goals are critical to ensuring a great experience within minutes. The "Campus Navigator" should stress interactive controller movement, a clear map, visible destination markers, and immediate feedback to ensure accessibility and engagement during brief engagements.

## 4. Accessibility and Controller Input

Designing for accessibility ensures that players with age groups can engage with the game. Controller input presents specific accessibility challenges and opportunities. A fundamental best practice is allowing control remapping, enabling players with motor disabilities or specific preferences to configure inputs comfortably . While full remapping might be beyond the scope of a this project, providing simple, intuitive default controls (using common keys) and potentially offering alternative keys for varied controllers.

Other considerations include adjustable difficulty levels, clear visual cues to supplement audio information , high-contrast text, and adjustable text sizes . Awareness of adaptive controllers like the Xbox Adaptive Controller or PlayStation Access Controller highlights the importance of flexible input design. For the "Campus Navigator," ensuring the default controller scheme is simple, responsive, and requires minor inputs is important  for more user engagement.

## 5. Spatial Navigation in Virtual Environments
The "Campus Navigator"'s fundamental mechanic is spatial navigation within a two-dimensional representation of campus. Research indicates that visual design aspects have a substantial impact on spatial experience and navigation. Key aspects include **visual clarity** (clear communication of critical information such as pathways, objectives, and player location) and **visual hierarchy** (making the most important components, such as the player character and destinations, stand out from the background). Clear visual difference, contrast, and the utilization of landmarks are all key cues for players to help them orient and understand layouts. Landmarks placed at decision points (such as junctions) are very useful for remembering and navigation. 
An excellent user interface, which may include a mini-map or objective markers, can facilitate navigation without cluttering the screen. Repeated navigation activities in games can improve the users understanding. This means that the game's map should be visually clear, with distinct sections or landmarks representing different departments or zones to help players navigate and learn.

## 6. Pygame as a Development Platform

Pygame is frequently cited as a suitable library for developing 2D games and multimedia applications in Python, particularly for beginners and educational purposes . It provides modules for essential tasks such as creating display windows, handling graphics (drawing shapes, rendering images/sprites), managing user input (controller), playing sound/music, and detecting collisions . Its ease of use, cross-platform nature, and active community support further enhance its suitability for a project intended for potential deployment in a public setting like an open day. Its feature set directly supports the requirements of the "Campus Navigator," including sprite management for the player/items, map rendering, controller input handling, and collision detection.

## 7. Conclusion

This review highlights key principles that will be used for the development of the "Campus Navigator Challenge." Drawing from serious games research and motivation theories (like SDT), the project will employ clear goals, balanced challenges, and timely feedback to create an engaging educational experience. Usability principles for novice players and short sessions dictate simple core mechanics and intuitive controls, crucial for the open day context. Accessibility considerations, particularly regarding controller input and visual clarity, will ensure broader reach. Insights into spatial navigation emphasize the need for a clear map design with distinct landmarks and effective UI cues. Finally, Pygame provides a capable and easy platform for implementing these features. By integrating these findings, the project aims to deliver a fun, informative, and easy game that effectively serves its purpose at the Aston college open day.

---
## Terminology:
#### Pygame: Python Module Used in developing the game.
#### Spirits: Bit images that are used as character displayed in the game.
#### Spatial Movement : Moving in virtual Space
---

## References (Online Sources & Blogs)

* **Accessible Game Design, n.d.:** [https://accessiblegamedesign.com/guidelines/controls.html](https://accessiblegamedesign.com/guidelines/controls.html)
* **AND Academy, n.d.:** [https://www.andacademy.com/resources/blog/ui-ux-design/game-ui-design/](https://www.andacademy.com/resources/blog/ui-ux-design/game-ui-design/)
* **CommLab India, n.d.:** [https://blog.commlabindia.com/elearning-design/learning-design-game-design-principles](https://blog.commlabindia.com/elearning-design/learning-design-game-design-principles)
* **ERIC - Math Games, n.d.:** [https://files.eric.ed.gov/fulltext/EJ1166723.pdf](https://files.eric.ed.gov/fulltext/EJ1166723.pdf)
* **Frontiers - Psychology Education, 2025:** [https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1511729/pdf](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1511729/pdf)
* **Frontiers - Self-Regulated Learning, 2022:** [https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.996403/full](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.996403/full)
* **Game Usability Heuristics PDF, 2009:** [https://ocw.metu.edu.tr/pluginfile.php/4129/mod_resource/content/0/ceit706_2/10/game_usability-_heuristics.pdf](https://ocw.metu.edu.tr/pluginfile.php/4129/mod_resource/content/0/ceit706_2/10/game_usability-_heuristics.pdf)
* **GeeksforGeeks - Getting Started, n.d.:** [https://www.geeksforgeeks.org/python-for-game-development-getting-started-with-pygame/](https://www.geeksforgeeks.org/python-for-game-development-getting-started-with-pygame/)
* **GeeksforGeeks - Pygame Tutorial, n.d.:** [https://www.geeksforgeeks.org/pygame-tutorial/](https://www.geeksforgeeks.org/pygame-tutorial/)
* **Harvard Business Publishing, 2024:** [https://hbsp.harvard.edu/inspiring-minds/5-fundamental-principles-for-developing-educational-games](https://hbsp.harvard.edu/inspiring-minds/5-fundamental-principles-for-developing-educational-games)
* **Intellipaat, 2025:** [https://intellipaat.com/blog/what-is-pygame/](https://intellipaat.com/blog/what-is-pygame/)
* **Juego Studios, 2023:** [https://www.juegostudio.com/blog/game-design-principles-every-game-designer-should-know](https://www.juegostudio.com/blog/game-design-principles-every-game-designer-should-know)
* **Little Inventors, 2024:** [https://littleinventors.in/introduction-to-pygame-creating-games-with-python/](https://littleinventors.in/introduction-to-pygame-creating-games-with-python/)
* **Meshy AI, n.d.:** [https://www.meshy.ai/blog/game-design-principles](https://www.meshy.ai/blog/game-design-principles)
* **Pixune Studios, 2020:** [https://pixune.com/blog/principles-of-game-art-design/](https://pixune.com/blog/principles-of-game-art-design/)
* **PMC - Older/Young Adults, n.d.:** [https://pmc.ncbi.nlm.nih.gov/articles/PMC7841238/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7841238/)
* **PMC - University Setting, n.d.:** [https://pmc.ncbi.nlm.nih.gov/articles/PMC11363834/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11363834/)
* **ProtoPie, n.d.:** [https://www.protopie.io/blog/game-ux-design](https://www.protopie.io/blog/game-ux-design)
* **Real Python, n.d.:** [https://realpython.com/pygame-a-primer/](https://realpython.com/pygame-a-primer/)
* **Reddit - Accessible Controllers Research, n.d.:** [https://www.reddit.com/r/disabledgamers/comments/1i7c2ir/im_doing_research_hoping_to_create_more/](https://www.reddit.com/r/disabledgamers/comments/1i7c2ir/im_doing_research_hoping_to_create_more/)
* **ResearchGate - Cognitive Load Optimized, n.d.:** [https://www.researchgate.net/publication/383021292_Game-Based_Learning_Design_Optimized_for_Cognitive_Load](https://www.researchgate.net/publication/383021292_Game-Based_Learning_Design_Optimized_for_Cognitive_Load)
* **ResearchGate - Guidelines, n.d.:** [https://www.researchgate.net/publication/286244330_Guidelines_for_an_effective_design_of_serious_games](https://www.researchgate.net/publication/286244330_Guidelines_for_an_effective_design_of_serious_games)
* **ResearchGate - Intro, n.d. / Request PDF, n.d.:** [https://www.researchgate.net/publication/377064275_Introduction_to_Pygame_and_Game_Development_using_Python_Pygame_by_Dr_MK_Jayanthi_Kannan](https://www.researchgate.net/publication/377064275_Introduction_to_Pygame_and_Game_Development_using_Python_Pygame_by_Dr_MK_Jayanthi_Kannan)
* **ResearchGate - Material Matters, 2024:** [https://www.researchgate.net/publication/384678611_Material_Matters_The_Effects_of_Materials_On_Spatial_Experience_and_Navigation_in_Video_Games](https://www.researchgate.net/publication/384678611_Material_Matters_The_Effects_of_Materials_On_Spatial_Experience_and_Navigation_in_Video_Games)
* **Robo Bionics, n.d.:** [https://www.robobionics.in/blog/best-gaming-accessibility-solutions-for-players-with-disabilities/](https://www.robobionics.in/blog/best-gaming-accessibility-solutions-for-players-with-disabilities/)
* **TestDevLab, 2024:** [https://www.testdevlab.com/blog/accessibility-testing-in-video-games](https://www.testdevlab.com/blog/accessibility-testing-in-video-games)
* **University of Silicon Valley, n.d.:** [https://usv.edu/blog/understanding-player-motivation-in-game-design/](https://usv.edu/blog/understanding-player-motivation-in-game-design/)

