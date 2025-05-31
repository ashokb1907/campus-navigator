# collectibles_data.py

"""
Structure for each collectible item:
{
    "id": "unique_string_identifier",
    "name": "Display Name or Category",
    "world_x": YOUR_X_COORDINATE_HERE, # Integer or float, found from your game
    "world_y": YOUR_Y_COORDINATE_HERE, # Integer or float, found from your game
    "image_path": "assets/icons/your_actual_icon.png", # Actual path to your image file
    "info_text": "The interesting fact or piece of information to display AFTER solving the riddle.",
    "points_value": 10,  # How many points for collecting this item
    "riddle_text": "The riddle question.",
    "riddle_options": ["Option A", "Option B", "Option C", "Option D"], # List of 4 strings
    "correct_option_index": 0 # Integer (0-3) indicating the correct option
}
"""

collectibles_data = [
    # --- Academic & Research Themes ---
    {
        "id": "business_insight_1",
        "name": "Business Insight",
        "world_x": 726,
        "world_y": 638,
        "image_path": "assets/icon/genericItem_color_141.png",
        "info_text": "Aston Business School is among the top 1% of business schools worldwide with triple accreditation (AACSB, AMBA, EQUIS).",
        "points_value": 15,
        "riddle_text": "I analyze markets and guide companies to profit. What am I often part of?",
        "riddle_options": ["A. A sports team", "B. A musical band", "C. A business school", "D. A bakery"],
        "correct_option_index": 2
    },
    {
        "id": "library_gem_1",
        "name": "Library Gem",
        "world_x": 682,
        "world_y": 693,
        "image_path": "assets/icon/genericItem_color_035.png",
        "info_text": "The Aston University Library offers extensive online databases, quiet study zones, and academic support services.",
        "points_value": 10,
        "riddle_text": "I have many stories but cannot speak; many shelves but no rooms. What am I?",
        "riddle_options": ["A. A forest", "B. A library", "C. A river", "D. A cloud"],
        "correct_option_index": 1
    },
    {
        "id": "engineering_spark_1",
        "name": "Engineering Spark",
        "world_x": 1098,
        "world_y": 522,
        "image_path": "assets/icon/genericItem_color_148.png",
        "info_text": "Aston's College of Engineering and Physical Sciences is renowned for its industry links and research impact.",
        "points_value": 20,
        "riddle_text": "I design bridges, circuits, and machines, solving practical problems. Who am I?",
        "riddle_options": ["A. A doctor", "B. An artist", "C. An engineer", "D. A chef"],
        "correct_option_index": 2
    },
    {
        "id": "health_fact_1",
        "name": "Health Science Fact",
        "world_x": 742,
        "world_y": 726,
        "image_path": "assets/icon/genericItem_color_110.png",
        "info_text": "Aston is a leader in health sciences, with strong programs in optometry, pharmacy, audiology, and biomedical sciences.",
        "points_value": 15,
        "riddle_text": "I focus on well-being, from eyesight to hearing, and the science of medicine. What field am I?",
        "riddle_options": ["A. Geology", "B. Health Science", "C. Astronomy", "D. Meteorology"],
        "correct_option_index": 1
    },
    {
        "id": "ebri_innovation_1",
        "name": "EBRI Innovation",
        "world_x": 880,
        "world_y": 438,
        "image_path": "assets/icon/genericItem_color_153.png",
        "info_text": "EBRI (Energy & Bioproducts Research Institute) at Aston pioneers sustainable energy technologies from biomass and waste.",
        "points_value": 15,
        "riddle_text": "I turn waste into power and champion green solutions. My research involves...?",
        "riddle_options": ["A. Fashion design", "B. Space travel", "C. Bioenergy", "D. Ancient history"],
        "correct_option_index": 2
    },
    {
        "id": "brain_teaser_1",
        "name": "Brain Teaser Insight",
        "world_x": 682,
        "world_y": 845,
        "image_path": "assets/icon/genericItem_color_079.png", # Consider a brain icon
        "info_text": "The Aston Brain Centre uses advanced neuroimaging like MEG and EEG to understand the human brain.",
        "points_value": 15,
        "riddle_text": "I am your body's command center, full of thoughts, emotions, and memories. What am I?",
        "riddle_options": ["A. Your heart", "B. Your phone", "C. Your brain", "D. Your backpack"],
        "correct_option_index": 2
    },
    {
        "id": "language_learning_tip",
        "name": "Languages & Social Sciences Fact",
        "world_x": 810,
        "world_y": 310,
        "image_path": "assets/icon/globe.png",
        "info_text": "Aston offers diverse programs in languages, translation, international relations, and sociology.",
        "points_value": 10,
        "riddle_text": "Hola! Bonjour! Guten Tag! What academic area helps you understand these greetings?",
        "riddle_options": ["A. Mathematics", "B. Language Studies", "C. Biology", "D. Engineering"],
        "correct_option_index": 1
    },
    {
        "id": "computer_science_byte",
        "name": "Computer Science Byte",
        "world_x": 1014,
        "world_y": 420,
        "image_path": "assets/icon/genericItem_color_075.png", # Consider a chip/code icon
        "info_text": "AI, cybersecurity, and software engineering are key areas in Aston's Computer Science department.",
        "points_value": 15,
        "riddle_text": "I think in 0s and 1s and create the apps you use daily. What field am I in?",
        "riddle_options": ["A. Agriculture", "B. Computer Science", "C. Construction", "D. Catering"],
        "correct_option_index": 1
    },
    # --- Campus Life & History Themes ---
    {
        "id": "su_event_highlight",
        "name": "Student Union Buzz",
        "world_x": 458,
        "world_y": 810,
        "image_path": "assets/icon/calender.png", # A party popper or community icon might work too
        "info_text": "The Aston Students' Union (SU) is run by students, for students, offering support, activities, and representation.",
        "points_value": 10,
        "riddle_text": "I am the hub for student clubs, events, and support on campus. What am I?",
        "riddle_options": ["A. The City Library", "B. The Main Lecture Hall", "C. The Students' Union", "D. The University Cafe"],
        "correct_option_index": 2
    },
    {
        "id": "aston_history_1",
        "name": "Aston Historical Note",
        "world_x": 502,
        "world_y": 406,
        "image_path": "assets/icon/old_key.png", # A scroll or building icon could also work
        "info_text": "Aston University was founded as the Birmingham Municipal Technical School in 1895 and gained university status in 1966.",
        "points_value": 10,
        "riddle_text": "I was established in 1895 as a technical school before becoming a full university. Who am I?",
        "riddle_options": ["A. University of Oxford", "B. University of Cambridge", "C. Aston University", "D. University of London"],
        "correct_option_index": 2
    },
    {
        "id": "campus_green_1",
        "name": "Campus Green Spot",
        "world_x": 618,
        "world_y": 690,
        "image_path": r"assets\icon\butterfly.png", # A leaf or tree icon
        "info_text": "Aston's campus integrates green spaces, providing areas for relaxation and biodiversity within the city.",
        "points_value": 5,
        "riddle_text": "I am a patch of nature on campus, offering a break from studies. What might I be?",
        "riddle_options": ["A. A car park", "B. A campus green / park", "C. A chemistry lab", "D. A rooftop"],
        "correct_option_index": 1
    },
    {
        "id": "sports_fact_1",
        "name": "Aston Sport Fact",
        "world_x": 970,
        "world_y": 374,
        "image_path": r"assets\icon\trophy.png", # A sports ball or running shoe icon
        "info_text": "The Sir Doug Ellis Woodcock Sports Centre offers excellent facilities for students and the community.",
        "points_value": 10,
        "riddle_text": "I feature courts, a gym, and often a pool for physical activities. I am the...?",
        "riddle_options": ["A. Art Gallery", "B. Cafeteria", "C. Sports Centre", "D. Bookshop"],
        "correct_option_index": 2
    },
    {
        "id": "mlk_centre_info",
        "name": "Multi-Faith Centre Info",
        "world_x": 618,
        "world_y": 856,
        "image_path": r"assets\icon\dove.png", # Interlinked hands or a peace symbol
        "info_text": "The Martin Luther King Multi-Faith Centre offers chaplaincy services and spaces for all faiths and beliefs.",
        "points_value": 10,
        "riddle_text": "I offer a welcoming space for prayer, meditation, and community for all. What am I?",
        "riddle_options": ["A. A concert venue", "B. A shopping centre", "C. A Multi-Faith Centre", "D. A cinema"],
        "correct_option_index": 2
    },
    {
        "id": "alumni_achiever",
        "name": "Alumni Spotlight",
        "world_x": 566,
        "world_y": 522,
        "image_path": "assets/icon/graduation_cap.png",
        "info_text": "Aston has a global network of successful alumni in various industries and professions.",
        "points_value": 10,
        "riddle_text": "Once students graduate from Aston, they become part of a proud global community known as...?",
        "riddle_options": ["A. Freshers", "B. Tutors", "C. Alumni", "D. Applicants"],
        "correct_option_index": 2
    },
    {
        "id": "innovation_hub_fact",
        "name": "Innovation Hub Fact",
        "world_x": 1174,
        "world_y": 374,
        "image_path": r"assets\icon\network.png", # An idea cloud or a startup icon
        "info_text": "Innovation Birmingham Campus, near Aston, is a hub for tech startups, entrepreneurs, and digital innovation.",
        "points_value": 10,
        "riddle_text": "I am a place where new tech ideas and startup businesses are nurtured and grown. What am I?",
        "riddle_options": ["A. A historical library", "B. An innovation hub/campus", "C. An ancient monument", "D. A traditional farm"],
        "correct_option_index": 1
    },
    # --- Practical / Fun Facts ---
    {
        "id": "campus_shop_tip",
        "name": "Campus Shop Tip",
        "world_x": 406,
        "world_y": 490,
        "image_path": "assets/icon/shopping_bag.png", # A coffee cup or sandwich icon
        "info_text": "On-campus shops like Tesco Express and Greggs provide convenient options for students.",
        "points_value": 5,
        "riddle_text": "I offer quick snacks, drinks, and essentials right on campus. You might find a Tesco Express here!",
        "riddle_options": ["A. The main lecture theatre", "B. The campus shops", "C. The quiet study zone", "D. The sports field"],
        "correct_option_index": 1
    },
    {
        "id": "transport_link_info",
        "name": "Transport Link Info",
        "world_x": 586,
        "world_y": 618,
        "image_path": r"assets\icon\bus.png", # A train or map pin icon
        "info_text": "Aston University is conveniently located with good public transport links to Birmingham city centre and train stations.",
        "points_value": 5,
        "riddle_text": "I connect the campus to the wider city and beyond, often running on roads or rails. What am I?",
        "riddle_options": ["A. A campus footpath", "B. Public transport", "C. A library bookshelf", "D. A university lecture"],
        "correct_option_index": 1
    },
    {
        "id": "study_abroad_opp",
        "name": "Study Abroad Info",
        "world_x": 653,
        "world_y": 534,
        "image_path": "assets/icon/passport.png", # An airplane or different flags
        "info_text": "Aston offers many opportunities for students to study abroad as part of their degree.",
        "points_value": 10,
        "riddle_text": "I allow students to experience university life in another country. What am I?",
        "riddle_options": ["A. A local internship", "B. A campus job", "C. A study abroad program", "D. A final exam"],
        "correct_option_index": 2
    },
    {
        "id": "sustainability_at_aston",
        "name": "Sustainability Fact",
        "world_x": 310,
        "world_y": 799,
        "image_path": r"assets\icon\recyle.png", # A wind turbine or green leaf
        "info_text": "Aston University actively promotes sustainability through recycling, energy efficiency, and green campus initiatives.",
        "points_value": 10,
        "riddle_text": "I focus on protecting the environment through recycling and using resources wisely. What is this concept?",
        "riddle_options": ["A. Industrialization", "B. Urbanization", "C. Sustainability", "D. Globalization"],
        "correct_option_index": 2
    },
    {
        "id": "aston_welcome_fact",
        "name": "Aston Welcome",
        "world_x": 1291, # Perhaps near a main campus entrance point from the map
        "world_y": 27,   # (You'll need to verify this location carefully)
        "image_path": "assets/icon/smiling.png", # A waving hand or welcome mat icon
        "info_text": "Aston University prides itself on being a welcoming and diverse community for students from all over the world.",
        "points_value": 5,
        "riddle_text": "What is a key characteristic of the Aston University community for new students and visitors?",
        "riddle_options": ["A. Exclusive and remote", "B. Welcoming and diverse", "C. Old-fashioned and quiet", "D. Strictly business-only"],
        "correct_option_index": 1
    }
]