from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            self.model = None
    
    def create_embedding(self, text: str) -> List[float]:
        if not self.model:
            logger.warning("Model not loaded, returning empty embedding")
            return []
        
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return []
    
    def create_exercise_embedding(self, exercise: Dict[str, Any]) -> List[float]:
        """Create embedding for an exercise based on its attributes"""
        text = f"{exercise['name']} {exercise['target_muscle']} {exercise['equipment']} {exercise['description']}"
        return self.create_embedding(text)
    
    def find_similar_exercises(self, query_embedding: List[float], exercise_embeddings: List[Dict], top_k: int = 10) -> List[Dict]:
        """Find exercises similar to the query embedding"""
        if not query_embedding or not exercise_embeddings:
            return []
        
        try:
            query_vec = np.array(query_embedding).reshape(1, -1)
            exercise_vecs = np.array([ex['embedding'] for ex in exercise_embeddings])
            
            similarities = cosine_similarity(query_vec, exercise_vecs)[0]
            
            # Get top_k most similar exercises
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            similar_exercises = []
            for idx in top_indices:
                exercise = exercise_embeddings[idx].copy()
                exercise['similarity'] = float(similarities[idx])
                similar_exercises.append(exercise)
            
            return similar_exercises
        except Exception as e:
            logger.error(f"Error finding similar exercises: {e}")
            return []
    
    def create_query_from_preferences(self, preferences: Dict[str, Any]) -> str:
        """Create a query string from user preferences"""
        focus_areas = " ".join(preferences.get('focus_areas', []))
        equipment = " ".join(preferences.get('available_equipment', []))
        workout_type = preferences.get('workout_type', '')
        user_level = preferences.get('user_level', '')
        
        query = f"{focus_areas} {equipment} {workout_type} {user_level} exercise workout"
        return query.strip()

# Global instance
embedding_service = EmbeddingService()