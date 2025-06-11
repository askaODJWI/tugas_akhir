import pandas as pd

class ProfileMatcher:
    def __init__(self):
        """
        Initializes the ProfileMatcher with all necessary configurations and weights.
        """
        # --- Weights Configuration ---
        self.cf_weight = 0.6
        self.sf_weight = 0.4
        self.category_weights = {
            'Karakteristik Hunian': 0.4,
            'Fasilitas Hunian': 0.3,
            'Fasilitas Lokasi': 0.3
        }

        # --- Ideal Scores for PERSONA IDENTIFICATION ---
        # These are the "perfect" scores for each attribute for a given persona.
        # This is used to find which persona a user's input matches best.
        self.ideal_persona_scores = {
            'Individu Lajang': {
                'building_area': 5,
                'bedrooms': 5,
                'bathrooms': 3,
                'floors': 3,
                'type': 5,
                'hospital': 4,
                'school': 4,
                'market': 4,
                'mall': 4,
                'transport': 4,
                'ac': 3,
                'carport': 2,
                'garasi': 2,
                'garden': 2,
                'stove': 3,
                'oven': 2,
                'refrigerator': 3,
                'microwave': 2,
                'pam': 3,
                'water_heater': 2,
                'gordyn': 2
            },
            'Berkeluarga tanpa Anak': {
                'building_area': 5,
                'bedrooms': 5,
                'bathrooms': 3,
                'floors': 3,
                'type': 5,
                'hospital': 4,
                'school': 4,
                'market': 4,
                'mall': 4,
                'transport': 4,
                'ac': 3,
                'carport': 3,
                'garasi': 3,
                'garden': 2,
                'stove': 3,
                'oven': 3,
                'refrigerator': 3,
                'microwave': 2,
                'pam': 3,
                'water_heater': 2,
                'gordyn': 2
            },
            'Berkeluarga dengan Anak': {
                'building_area': 5,
                'bedrooms': 5,
                'bathrooms': 3,
                'floors': 3,
                'type': 5,
                'hospital': 4,
                'school': 4,
                'market': 4,
                'mall': 4,
                'transport': 4,
                'ac': 3,
                'carport': 3,
                'garasi': 3,
                'garden': 3,
                'stove': 3,
                'oven': 3,
                'refrigerator': 3,
                'microwave': 3,
                'pam': 3,
                'water_heater': 3,
                'gordyn': 3
            }
        }

        # --- Ideal Scores for PROPERTY SCORING ---
        # These are the target values used to calculate the gap when scoring a property.
        self.ideal_property_scores = {
            'Individu Lajang': {
                'building_area': 5, 'bedrooms': 5, 'bathrooms': 3, 'floors': 3, 'type': 5, 'hospital': 4,
                'school': 4, 'market': 4, 'mall': 4, 'transport': 4, 'ac': 3, 'carport': 2, 'garasi': 2,
                'garden': 2, 'stove': 3, 'oven': 2, 'refrigerator': 3, 'microwave': 2, 'pam': 3,
                'water_heater': 2, 'gordyn': 2
            },
            'Berkeluarga tanpa Anak': {
                'building_area': 5, 'bedrooms': 5, 'bathrooms': 3, 'floors': 3, 'type': 5, 'hospital': 4,
                'school': 4, 'market': 4, 'mall': 4, 'transport': 4, 'ac': 3, 'carport': 3, 'garasi': 3,
                'garden': 2, 'stove': 3, 'oven': 3, 'refrigerator': 3, 'microwave': 2, 'pam': 3,
                'water_heater': 2, 'gordyn': 2
            },
            'Berkeluarga dengan Anak': {
                'building_area': 5, 'bedrooms': 5, 'bathrooms': 3, 'floors': 3, 'type': 5, 'hospital': 4,
                'school': 4, 'market': 4, 'mall': 4, 'transport': 4, 'ac': 3, 'carport': 3, 'garasi': 3,
                'garden': 3, 'stove': 3, 'oven': 3, 'refrigerator': 3, 'microwave': 3, 'pam': 3,
                'water_heater': 3, 'gordyn': 3
            }
        }

        # --- Criteria Structure (Category and Factor Type) ---
        self.criteria_structure = {
            # Definitions for 'Individu Lajang', 'Berkeluarga tanpa Anak', 'Berkeluarga dengan Anak'
            # (This dictionary is large and has been omitted for brevity, but it's the same as in your original file)
            'Individu Lajang': {
                'building_area': ('Karakteristik Hunian', 'SF'), 'bedrooms': ('Karakteristik Hunian', 'CF'),
                'bathrooms': ('Karakteristik Hunian', 'SF'), 'floors': ('Karakteristik Hunian', 'SF'),
                'type': ('Fasilitas Hunian', 'CF'), 'hospital': ('Fasilitas Lokasi', 'SF'),
                'school': ('Fasilitas Lokasi', 'SF'), 'market': ('Fasilitas Lokasi', 'SF'),
                'mall': ('Fasilitas Lokasi', 'CF'), 'transport': ('Fasilitas Lokasi', 'CF'),
                'ac': ('Fasilitas Hunian', 'CF'), 'carport': ('Fasilitas Hunian', 'SF'),
                'garasi': ('Fasilitas Hunian', 'SF'), 'garden': ('Fasilitas Hunian', 'SF'),
                'stove': ('Fasilitas Hunian', 'CF'), 'oven': ('Fasilitas Hunian', 'SF'),
                'refrigerator': ('Fasilitas Hunian', 'CF'), 'microwave': ('Fasilitas Hunian', 'SF'),
                'pam': ('Fasilitas Hunian', 'CF'), 'water_heater': ('Fasilitas Hunian', 'SF'),
                'gordyn': ('Fasilitas Hunian', 'SF')
            },
            'Berkeluarga tanpa Anak': {
                'building_area': ('Karakteristik Hunian', 'CF'), 'bedrooms': ('Karakteristik Hunian', 'CF'),
                'bathrooms': ('Karakteristik Hunian', 'SF'), 'floors': ('Karakteristik Hunian', 'SF'),
                'type': ('Fasilitas Hunian', 'SF'), 'hospital': ('Fasilitas Lokasi', 'CF'),
                'school': ('Fasilitas Lokasi', 'SF'), 'market': ('Fasilitas Lokasi', 'CF'),
                'mall': ('Fasilitas Lokasi', 'SF'), 'transport': ('Fasilitas Lokasi', 'SF'),
                'ac': ('Fasilitas Hunian', 'CF'), 'carport': ('Fasilitas Hunian', 'CF'),
                'garasi': ('Fasilitas Hunian', 'CF'), 'garden': ('Fasilitas Hunian', 'SF'),
                'stove': ('Fasilitas Hunian', 'CF'), 'oven': ('Fasilitas Hunian', 'CF'),
                'refrigerator': ('Fasilitas Hunian', 'CF'), 'microwave': ('Fasilitas Hunian', 'SF'),
                'pam': ('Fasilitas Hunian', 'CF'), 'water_heater': ('Fasilitas Hunian', 'SF'),
                'gordyn': ('Fasilitas Hunian', 'SF')
            },
            'Berkeluarga dengan Anak': {
                'building_area': ('Karakteristik Hunian', 'CF'), 'bedrooms': ('Karakteristik Hunian', 'CF'),
                'bathrooms': ('Karakteristik Hunian', 'CF'), 'floors': ('Karakteristik Hunian', 'SF'),
                'type': ('Fasilitas Hunian', 'SF'), 'hospital': ('Fasilitas Lokasi', 'CF'),
                'school': ('Fasilitas Lokasi', 'CF'), 'market': ('Fasilitas Lokasi', 'SF'),
                'mall': ('Fasilitas Lokasi', 'SF'), 'transport': ('Fasilitas Lokasi', 'SF'),
                'ac': ('Fasilitas Hunian', 'CF'), 'carport': ('Fasilitas Hunian', 'CF'),
                'garasi': ('Fasilitas Hunian', 'CF'), 'garden': ('Fasilitas Hunian', 'CF'),
                'stove': ('Fasilitas Hunian', 'CF'), 'oven': ('Fasilitas Hunian', 'CF'),
                'refrigerator': ('Fasilitas Hunian', 'CF'), 'microwave': ('Fasilitas Hunian', 'CF'),
                'pam': ('Fasilitas Hunian', 'CF'), 'water_heater': ('Fasilitas Hunian', 'CF'),
                'gordyn': ('Fasilitas Hunian', 'CF')
            }
        }


    # --- Private Helper Methods ---
    def _gap_to_weighted_score(self, gap):
        return max(1, 5 - abs(gap))

    # --- Scoring Functions (Internal) ---
    def _score_building_area(self, value, persona):
        if persona == 'Individu Lajang': return 5 if value <= 72 else 4 if value <= 99 else 3 if value <= 149 else 2 if value <= 200 else 1
        else: return 1 if value <= 72 else 2 if value <= 99 else 3 if value <= 149 else 4 if value <= 200 else 5

    def _score_bedrooms(self, value, persona):
        if persona == 'Individu Lajang': return 5 if value <= 1 else 3 if value == 2 else 1
        elif persona == 'Berkeluarga tanpa Anak': return 5 if value <= 2 else 3 if value == 3 else 2
        else: return 1 if value <= 1 else 3 if value == 2 else 5

    def _score_bathrooms(self, value, persona):
        if persona == 'Individu Lajang': return 5 if value == 1 else 3 if value == 2 else 1
        elif persona == 'Berkeluarga tanpa Anak': return 3 if value == 2 else 5 if value == 1 else 1
        else: return 1 if value <= 1 else 3 if value == 2 else 5
    
    def _score_floors(self, value, persona):
        if persona == 'Individu Lajang': return 5 if value == 1 else 3 if value == 2 else 1
        elif persona == 'Berkeluarga tanpa Anak': return 3 if value == 2 else 5 if value == 1 else 1
        else: return 1 if value == 1 else 3 if value == 2 else 5

    def _score_type(self, value, persona):
        val = str(value).lower()
        return 5 if (persona == 'Individu Lajang' and val == 'apartemen') or \
                    (persona != 'Individu Lajang' and val == 'rumah') else 1

    def _score_location_facility(self, value, persona, facility_type):
        # This is a generic function for hospital, school, market, mall, transport
        if value != 1: return 1
        if persona == 'Individu Lajang':
            return 5 if facility_type in ['mall', 'transport'] else 3
        elif persona == 'Berkeluarga tanpa Anak':
            return 5 if facility_type in ['hospital', 'market'] else 3
        else: # Berkeluarga dengan Anak
            return 5 if facility_type in ['hospital', 'school'] else 3

    def _score_home_facility(self, value, persona, facility_type):
        # This is a generic function for most home facilities
        if value != 1: return 1
        # Add specific exceptions if any, otherwise most are 5 if present
        if persona == 'Individu Lajang':
            if facility_type in ['carport', 'garasi', 'garden', 'oven', 'microwave', 'water_heater', 'gordyn']: return 1 # Not essential
        elif persona == 'Berkeluarga dengan Anak':
             if facility_type in ['garden', 'microwave', 'water_heater']: return 5 # More essential
        return 5 # Generally desirable


    # --- Public Methods ---
    def identify_persona(self, user_input):
        """
        Identifies the best persona for a given user_input dictionary.
        This replaces the logic from ProfileMatching.py.
        """
        persona_scores = {}
        for persona, criteria in self.ideal_persona_scores.items():
            total_gap = 0
            for criterion, ideal_score in criteria.items():
                value = user_input.get(criterion, 0) # Get value from user input dict
                
                # Dynamically call the correct scoring function
                score_func = getattr(self, f'_score_{criterion}', lambda v, p: 1)
                actual_score = score_func(value, persona)
                
                gap = abs(ideal_score - actual_score)
                total_gap += gap
            persona_scores[persona] = total_gap

        # The best persona is the one with the minimum total gap
        best_persona = min(persona_scores, key=persona_scores.get)
        return best_persona

    def calculate_property_score(self, property_details, persona):
        """
        Calculates the final match score for a property against a specific persona.
        This replaces the logic from PropertyProfileMatching.py.
        """
        category_cf = {}
        category_sf = {}

        for key, (category, factor) in self.criteria_structure.get(persona, {}).items():
            value = property_details.get(key, 0)
            
            # Map facilities to the generic scoring functions
            if key in ['hospital', 'school', 'market', 'mall', 'transport']:
                score_func = self._score_location_facility
                actual = score_func(value, persona, key)
            elif key in ['ac', 'carport', 'garasi', 'garden', 'stove', 'oven', 'refrigerator', 'microwave', 'pam', 'water_heater', 'gordyn']:
                score_func = self._score_home_facility
                actual = score_func(value, persona, key)
            else:
                score_func = getattr(self, f'_score_{key}', lambda v, p: 1)
                actual = score_func(value, persona)

            ideal = self.ideal_property_scores[persona][key]
            wg = self._gap_to_weighted_score(actual - ideal)

            if factor == 'CF':
                category_cf.setdefault(category, []).append(wg)
            else:
                category_sf.setdefault(category, []).append(wg)

        final_weighted = {}
        all_categories = set(category_cf.keys()) | set(category_sf.keys())
        for cat in all_categories:
            ncf = sum(category_cf.get(cat, [0])) / len(category_cf.get(cat, [1]))
            nsf = sum(category_sf.get(cat, [0])) / len(category_sf.get(cat, [1]))
            final_score = (self.cf_weight * ncf) + (self.sf_weight * nsf)
            final_weighted[cat] = final_score * self.category_weights.get(cat, 0)
            
        return sum(final_weighted.values())