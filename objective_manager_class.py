# objective_manager_class.py
import random
# from settings import NUM_OBJECTIVES_TO_COMPLETE # Import from settings

class ObjectiveManager:
    def __init__(self, all_destination_objects_list, num_objectives_to_complete): # Pass num_objectives
        self.NUM_OBJECTIVES_TO_COMPLETE = num_objectives_to_complete
        self.full_destination_pool = [
            d for d in all_destination_objects_list 
            if d.world_x is not None and d.world_y is not None
        ]
        self.game_objectives = [] 
        self.current_objective_idx_in_game_list = -1
        self.current_target_destination = None
        self.reset() 

    def reset(self): 
        for dest in self.full_destination_pool: 
            dest.visited = False
            dest.set_active_target(False)
        self.current_objective_idx_in_game_list = -1
        self.current_target_destination = None
        self._select_random_objectives()
        self.set_next_objective()

    def _select_random_objectives(self):
        if not self.full_destination_pool: 
            self.game_objectives = []
            print("Warning: No valid destinations in pool to select for objectives.")
            return
        
        available_to_pick = list(self.full_destination_pool)
        random.shuffle(available_to_pick)
        num_to_select = min(len(available_to_pick), self.NUM_OBJECTIVES_TO_COMPLETE)
        self.game_objectives = available_to_pick[:num_to_select]
        
        if self.game_objectives: 
            print(f"Selected {len(self.game_objectives)} main objectives for this session:")
            for i,d in enumerate(self.game_objectives): print(f"  {i+1}. {d.name}")
        else: 
            print("Warning: Could not select any main objectives for this session.")

    def set_next_objective(self):
        if self.current_target_destination: 
            self.current_target_destination.set_active_target(False)
        
        self.current_objective_idx_in_game_list +=1
        if self.current_objective_idx_in_game_list < len(self.game_objectives):
            self.current_target_destination = self.game_objectives[self.current_objective_idx_in_game_list]
            if not self.current_target_destination.visited: # Should typically be true
                 self.current_target_destination.set_active_target(True)
                 print(f"New Main Objective: Go to {self.current_target_destination.name}")
                 return True
            else: # This objective was somehow already visited (e.g., by debug), try next
                print(f"Debug: Objective {self.current_target_destination.name} already visited, trying next.")
                return self.set_next_objective()
        else: 
            self.current_target_destination = None
            print("All main session objectives visited!")
            return False # No more objectives

    def get_current_objective_text(self):
        if self.current_target_destination: 
            return f"Find ({self.current_objective_idx_in_game_list + 1}/{len(self.game_objectives)}): {self.current_target_destination.name}"
        elif self.all_session_objectives_visited(): 
            return "Main Objectives Complete!"
        elif not self.game_objectives: 
            return "No main objectives set for this session."
        return "Welcome! Starting campus tour..."
        
    def all_session_objectives_visited(self):
        if not self.game_objectives: return True # If no objectives were set, consider it "done"
        return all(d.visited for d in self.game_objectives)