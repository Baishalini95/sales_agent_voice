from database import DatabaseManager

# Test database functionality
db = DatabaseManager()

# Test saving feedback
try:
    feedback_id = db.save_feedback(
        name="Test User",
        email="test@example.com", 
        challenge="Testing the feedback system",
        satisfaction_rating=5,
        query="Test query",
        response="Test response"
    )
    print(f"Feedback saved successfully with ID: {feedback_id}")
    
    # Test retrieving feedback
    all_feedback = db.get_all_feedback()
    print(f"Retrieved {len(all_feedback)} feedback entries")
    
    if all_feedback:
        print("Latest feedback:", all_feedback[0])
        
except Exception as e:
    print(f"Database error: {e}")
    import traceback
    traceback.print_exc()