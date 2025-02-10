
        
    
#     # Compare with database (example)
#     database_embeddings = [...]  # Your precomputed embeddings
#     similarities = np.dot(database_embeddings, embedding.T)
#     best_match_idx = np.argmax(similarities)
    
#     if similarities[best_match_idx] > 0.6:  # Threshold varies
#         print("Match found!")

# # Example comparison
# embedding1 = get_embedding(preprocess(face1))
# embedding2 = get_embedding(preprocess(face2))
# similarity = np.dot(normalize_embedding(embedding1), normalize_embedding(embedding2).T)
# print(f"Similarity: {similarity[0][0]:.4f}")