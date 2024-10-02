import streamlit as st
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=chatbot user=chatbot password=password host=localhost port=5432")
cursor = conn.cursor()

# Fetch vector data
cursor.execute("SELECT vector_column FROM chatbot LIMIT 100")
vectors = cursor.fetchall()

# Visualize the vectors (e.g., using matplotlib for a simple plot)
vectors_np = np.array(vectors)
plt.scatter(vectors_np[:, 0], vectors_np[:, 1])
st.pyplot(plt)
