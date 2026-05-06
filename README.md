#  Context Recovery AI System

##  Problem
Conversations often lose context due to missing or fragmented messages, leading to poor AI responses.

---

##  Solution
We built a web-based AI system that:
- Recovers missing context
- Uses relevance scoring
- Reconstructs conversation flow
- Generates coherent responses

---

##  Core Features
- Conversation tracking & segmentation
- Memory storage (fragment-based)
- Relevance + priority scoring
- Context reconstruction pipeline
- Dynamic AI responses (non-repetitive)
- User onboarding system

---

##  Tech Stack
- Frontend: HTML, CSS
- Backend: Python (Flask)
- Storage: In-memory database
- AI Logic: Rule-based + scoring system

---

##  Backend Architecture

User Input  
→ Tokenization  
→ Memory Retrieval  
→ Relevance Scoring  
→ Priority Ranking  
→ Context Reconstruction  
→ Response Generation  

---

##  User Flow

1. User logs in / signs up  
2. Completes onboarding  
3. Enters dashboard  
4. Sends message  
5. System retrieves past context  
6. Applies scoring  
7. Reconstructs conversation  
8. Generates response  

---
## 🎬 Demo Example

Input:
I have a bug in my project

Output:
- Context-aware response
- Uses past conversation
- Non-repetitive

---

##  How to Run

1. Install:
pip install flask


2. Run:
python app.py


3. Open:
http://127.0.0.1:5000


---

##  Key Innovation
- Handles broken conversations  
- Recovers missing context dynamically  
- Uses scoring-based memory system  
- Produces human-like responses  

---

##  Future Scope
- Add database (MongoDB / Firebase)  
- Use embeddings for semantic search  
- Deploy to cloud  

---


> “Our system reconstructs missing conversational context using relevance scoring and memory prioritization to ensure coherent AI responses.”
