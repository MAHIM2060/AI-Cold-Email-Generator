import pandas as pd
import chromadb
import uuid

class CandidateDB:
    def __init__(self, file_path="candidates.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="candidates")

    def load_candidates(self):
        # Get all existing IDs from the collection
        existing_ids = self.collection.get()['ids']
        
        # Only try to delete if the collection is not empty
        if existing_ids:
            self.collection.delete(ids=existing_ids)
        
        for _, row in self.data.iterrows():
            # We will search based on a combination of headline and skills
            document_text = f"Headline: {row['Headline']}. Skills: {row['Skills']}"
            
            # Store all candidate info in the metadata
            metadata = {
                "name": row["Name"],
                "headline": row["Headline"],
                "skills": row["Skills"],
                "portfolio_link": row["PortfolioLink"]
            }
            
            self.collection.add(
                documents=document_text,
                metadatas=metadata,
                ids=str(uuid.uuid4())
            )

    def find_best_candidates(self, required_skills, num_candidates=3):
        """Finds the top N most relevant candidates."""
        query_text = ", ".join(required_skills)
        results = self.collection.query(
            query_texts=[query_text], 
            n_results=num_candidates
        )
        
        if results and results['metadatas'] and results['metadatas'][0]:
            return results['metadatas'][0]
        else:
            return []