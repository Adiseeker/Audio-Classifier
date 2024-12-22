import streamlit as st
import gensim.downloader
import numpy as np
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
from dotenv import dotenv_values
import os

# Set Streamlit page config
st.set_page_config(page_title="Wyszukiwarka Audycji", layout="centered")

# Load environment variables
env = dotenv_values(".env")

# Constants
QDRANT_COLLECTION_NAME = "transcripts"

# DB Functions
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(
        url=env["QDRANT_URL"],
        api_key=env["QDRANT_API_KEY"],
    )

def assure_db_collection_exists(model):
    """
    Ensure the Qdrant collection exists with appropriate dimensions.
    """
    if model is None:
        st.error("Model not loaded. Cannot create or check collection in Qdrant.")
        return

    qdrant_client = get_qdrant_client()

    # Determine embedding dimension
    if hasattr(model, 'vector_size'):  # For Word2Vec, FastText, and GloVe
        embedding_dim = model.vector_size
    elif isinstance(model, SentenceTransformer):  # For Sentence Embeddings
        embedding_dim = model.get_sentence_embedding_dimension()
    else:
        st.error("Unsupported model type for determining embedding dimensions.")
        return

    # Check or create collection
    if not qdrant_client.collection_exists(QDRANT_COLLECTION_NAME):
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE,
            ),
        )
    else:
        collection_info = qdrant_client.get_collection(QDRANT_COLLECTION_NAME)
        # Access vector size from the nested params.vectors
        vector_size = collection_info.config.params.vectors.size
        if vector_size != embedding_dim:
            st.error(
                f"Collection '{QDRANT_COLLECTION_NAME}' exists with "
                f"dimension {vector_size}, but the model has dimension {embedding_dim}."
            )
            return
        st.success("Collection exists with correct dimension!")


# Fetch available models
def get_available_models(model_type):
    """
    Return a filtered list of available models based on the selected model type.
    """
    model_names = gensim.downloader.info()['models']

    if model_type == "Word2Vec":
        return [model for model in model_names if "word2vec" in model]
    elif model_type == "FastText":
        return [model for model in model_names if "fasttext" in model]
    elif model_type == "GloVe":
        return [model for model in model_names if "glove" in model]
    elif model_type == "Sentence Embeddings":
        return [
            "paraphrase-MiniLM-L6-v2",
            "all-MiniLM-L6-v2",
            "distilbert-base-nli-mean-tokens",
            "paraphrase-distilroberta-base-v1",
            "stsb-roberta-large",
        ]
    else:
        return model_names

# Load the selected model
def load_model_based_on_selection(model_type, model_name, progress_bar):
    """
    Load the appropriate model based on the selected model type and name.
    """
    try:
        progress_bar.progress(0)

        if model_type in ["Word2Vec", "FastText", "GloVe"]:
            progress_bar.progress(20)
            model = gensim.downloader.load(model_name)
        elif model_type == "Sentence Embeddings":
            progress_bar.progress(20)
            if model_name not in get_available_models("Sentence Embeddings"):
                raise ValueError(f"Model '{model_name}' is not a valid sentence-transformers model.")
            model = SentenceTransformer(model_name)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        progress_bar.progress(100)
        st.success(f"{model_type} model '{model_name}' loaded successfully!")
        return model
    except Exception as e:
        progress_bar.progress(0)
        st.error(f"Error loading model: {e}")
        return None

# Get embeddings
def get_embeddings(text, model):
    if isinstance(model, SentenceTransformer):
        return model.encode([text])[0]
    elif hasattr(model, 'vector_size'):  # For Word2Vec, FastText, and GloVe
        words = text.split()
        embeddings = [model[word] for word in words if word in model]
        if embeddings:
            return np.mean(embeddings, axis=0)
        else:
            st.warning("No valid words found for embedding.")
            return None

# Add DataFrame to Qdrant
def add_dataframe_to_db_auto(df, model):
    """
    Add notes to Qdrant from a DataFrame dynamically.
    """
    qdrant_client = get_qdrant_client()
    if df.empty:
        st.error("The DataFrame is empty. Please upload valid data.")
        return

    total_notes = len(df)
    progress_bar = st.progress(0)

    for idx, row in df.iterrows():
        payload = row.to_dict()
        unique_id = payload.get("reference_path", f"row_{idx}")

        combined_text = " ".join(str(value) for value in payload.values() if isinstance(value, str))
        embedding = get_embeddings(combined_text, model)

        if embedding is not None:
            point_id = qdrant_client.count(collection_name=QDRANT_COLLECTION_NAME).count + 1
            qdrant_client.upsert(
                collection_name=QDRANT_COLLECTION_NAME,
                points=[PointStruct(id=point_id, vector=embedding, payload=payload)],
            )
        progress_bar.progress((idx + 1) / total_notes)

    st.success("DataFrame data has been saved to the database.")

# List notes from DB
def list_notes_from_db(query, model, search_type="semantic"):
    """
    Search for notes in the Qdrant database.
    """
    qdrant_client = get_qdrant_client()

    if not query:
        notes = qdrant_client.scroll(collection_name=QDRANT_COLLECTION_NAME, limit=10)[0]
        return [{"payload": note.payload, "score": None} for note in notes]

    try:
        if search_type == "full_text":
            notes = []
            points = qdrant_client.scroll(collection_name=QDRANT_COLLECTION_NAME, limit=1000)[0]
            for point in points:
                payload = point.payload
                text = " ".join(str(value) for value in payload.values() if isinstance(value, str))
                if query.lower() in text.lower():
                    notes.append({"payload": payload, "score": None})
            return notes
        elif search_type == "semantic":
            embedding = get_embeddings(query, model)
            if embedding is not None:
                notes = qdrant_client.search(
                    collection_name=QDRANT_COLLECTION_NAME,
                    query_vector=embedding,
                    limit=10,
                )
                return [{"payload": note.payload, "score": note.score} for note in notes]
    except Exception as e:
        st.error(f"Error during search: {e}")
        return []

    return []  # Ensure an empty list is returned if nothing is found

# Main Application
model_type = st.sidebar.selectbox("Choose Model Type", ["Word2Vec", "FastText", "GloVe", "Sentence Embeddings"])
available_models = get_available_models(model_type)
selected_model = st.sidebar.selectbox(f"Choose {model_type} Model", available_models)

progress_bar = st.progress(0)
model = load_model_based_on_selection(model_type, selected_model, progress_bar)
assure_db_collection_exists(model)

search_tab, df_tab = st.tabs(["Search Database", "Add from DataFrame"])

with search_tab:
    query = st.text_input("Search Query", key="search_query")
    search_type = st.radio("Search Type", ["Semantic", "Full Text"], index=0)
    search_mode = "semantic" if search_type == "Semantic" else "full_text"

    if st.button("Search"):
        if query:
            for note in list_notes_from_db(query, model, search_mode):
                with st.container():
                    expander = st.expander(str(note['payload'].get("reference_path", "No Title")))
                    with expander:
                        st.json(note['payload'])
                    if note['score'] is not None:
                        st.write(f"Score: {note['score']:.4f}")
        else:
            st.error("Please enter a search query.")

with df_tab:
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df)
        if not df.empty and st.button("Save DataFrame to Database"):
            add_dataframe_to_db_auto(df, model)
