from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.core.config import settings

class MilvusService:
    def __init__(self):
        self.collection_name = "news_chunks"
        self._connect()
        self._init_collection()

    def _connect(self):
        try:
            connections.connect(
                alias="default", 
                host=settings.MILVUS_HOST, 
                port=settings.MILVUS_PORT
            )
            print(f"Connected to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")

    def _init_collection(self):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            self.collection.load()
            return

        # Define schema
        article_id = FieldSchema(
            name="article_id", 
            dtype=DataType.INT64, 
            description="Article ID from PostgreSQL"
        )
        chunk_id = FieldSchema(
            name="id", 
            dtype=DataType.INT64, 
            is_primary=True, 
            auto_id=True
        )
        chunk_content = FieldSchema(
            name="chunk_content", 
            dtype=DataType.VARCHAR, 
            max_length=4096  # Limit text length
        )
        vector = FieldSchema(
            name="vector", 
            dtype=DataType.FLOAT_VECTOR, 
            dim=768  # Gemini Embedding dim
        )

        schema = CollectionSchema(
            fields=[chunk_id, article_id, chunk_content, vector], 
            description="News article chunks"
        )

        self.collection = Collection(
            name=self.collection_name, 
            schema=schema, 
            using='default'
        )
        
        # Create index for vector field
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(field_name="vector", index_params=index_params)
        self.collection.load()

    def insert_vectors(self, vectors, attributes):
        """
        vectors: list of lists (float vectors)
        attributes: list of dicts (scalar fields)
        """
        # pymilvus inserts: [ [field1_values], [field2_values] ... ]
        # Ensure order matches schema
        data = [
            [attr["article_id"] for attr in attributes],
            [attr["chunk_content"] for attr in attributes],
            vectors
        ]
        self.collection.insert(data)
        self.collection.flush()

    def search_vectors(self, query_vectors, top_k=5, expr=None):
        search_params = {
            "metric_type": "L2", 
            "params": {"nprobe": 10}
        }
        
        results = self.collection.search(
            data=query_vectors, 
            anns_field="vector", 
            param=search_params, 
            limit=top_k, 
            expr=expr,
            output_fields=["chunk_content", "article_id"]
        )
        return results

milvus_service = MilvusService()
