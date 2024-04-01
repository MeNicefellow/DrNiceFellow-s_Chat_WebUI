from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import TextNode
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores import VectorStoreQuery
import psycopg2

class DatabaseManager:
    def __init__(self, db_name, host, password, port, user, table_name, embed_dim=384):
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
        self.db_name = db_name
        self.host = host
        self.password = password
        self.port = port
        self.user = user
        self.table_name = table_name
        self.embed_dim = embed_dim
        self.conn = self._connect_to_db()
        self.vector_store = self._create_vector_store()
        try:
            with self.conn.cursor() as c:
                #c.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
                c.execute(f"CREATE DATABASE {self.db_name}")
        except Exception as e:
            print(f"Error creating database: {e} because it already exists")

    def _connect_to_db(self):
        conn = psycopg2.connect(
            dbname="postgres",
            host=self.host,
            password=self.password,
            port=self.port,
            user=self.user,
        )
        conn.autocommit = True
        return conn

    def _create_vector_store(self):
        return PGVectorStore.from_params(
            database=self.db_name,
            host=self.host,
            password=self.password,
            port=self.port,
            user=self.user,
            table_name=self.table_name,
            embed_dim=self.embed_dim,
        )

    def save_to_db(self, text_chunks):

        nodes = [TextNode(text=text_chunk) for text_chunk in text_chunks]
        print("text chunks: ", text_chunks)

        for node in nodes:
            node_embedding = self.embed_model.get_text_embedding(
                node.get_content(metadata_mode="all")
            )
            node.embedding = node_embedding
        self.vector_store.add(nodes)
        print("Data saved to database")

    def query_db(self, query_str, similarity_top_k=5, mode='default'):
        query_embedding = self.embed_model.get_query_embedding(query_str)

        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding, similarity_top_k=similarity_top_k, mode=mode
        )

        query_result = self.vector_store.query(vector_store_query)
        return ' '.join(node.get_content() for node in query_result.nodes)