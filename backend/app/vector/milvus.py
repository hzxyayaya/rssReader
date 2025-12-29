from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MilvusService:
    def __init__(self):
        self.collection_name = "news_chunks"
        self.collection = None
        self.connected = False
        self._loaded = False
        self._connect()
        if self.connected:
            self._init_collection()

    def _connect(self):
        try:
            connections.connect(
                alias="default", 
                host=settings.MILVUS_HOST, 
                port=settings.MILVUS_PORT,
                timeout=5
            )
            self.connected = True
            logger.info(f"Connected to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        except Exception as e:
            self.connected = False
            logger.warning(f"Milvus not available: {e}. AI Q&A features will be disabled.")

    def _init_collection(self):
        """Initialize collection without loading - loading happens lazily on first search"""
        if not self.connected:
            return
            
        try:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' found (will load on first search)")
                return
        except Exception as e:
            logger.warning(f"Failed to get existing collection: {e}, will create new one")

        try:
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
                max_length=4096
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
            logger.info(f"New collection '{self.collection_name}' created")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            self.collection = None

    def _ensure_loaded(self):
        """Lazy load collection into memory when needed"""
        if self._loaded or self.collection is None:
            return True
        
        try:
            logger.info(f"Loading collection '{self.collection_name}' into memory...")
            self.collection.load(_async=False, timeout=120)
            self._loaded = True
            logger.info(f"Collection '{self.collection_name}' loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load collection: {e}")
            self._loaded = False
            # Try to reconnect and reload
            try:
                self._connect()
                if self.connected:
                    self.collection = Collection(self.collection_name)
                    self.collection.load(_async=False, timeout=120)
                    self._loaded = True
                    logger.info(f"Collection '{self.collection_name}' reloaded after reconnect")
                    return True
            except Exception as e2:
                logger.error(f"Failed to reload collection after reconnect: {e2}")
            return False

    def is_available(self):
        """Check if Milvus is available and ready"""
        return self.connected and self.collection is not None

    def insert_vectors(self, vectors, attributes):
        """
        vectors: list of lists (float vectors)
        attributes: list of dicts (scalar fields)
        """
        if not self.is_available():
            logger.warning("Milvus not available, skipping vector insert")
            return
            
        # No need to load for insert operations
        data = [
            [attr["article_id"] for attr in attributes],
            [attr["chunk_content"] for attr in attributes],
            vectors
        ]
        self.collection.insert(data)
        self.collection.flush()

    def search_vectors(self, query_vectors, top_k=5, expr=None):
        if not self.is_available():
            logger.warning("Milvus not available, cannot search")
            return []
        
        # Lazy load only when searching
        self._ensure_loaded()
        if not self._loaded:
            logger.warning("Collection not loaded, cannot search")
            return []
            
        search_params = {
            "metric_type": "L2", 
            "params": {"nprobe": 10}
        }

        output_fields = []
        try:
            schema_fields = {field.name for field in self.collection.schema.fields}
            output_fields = [f for f in ["chunk_content", "article_id"] if f in schema_fields]
            if not output_fields:
                logger.warning("No valid output fields in collection '%s'", self.collection_name)
        except Exception as e:
            logger.warning("Failed to read collection schema: %s", e)

        try:
            results = self.collection.search(
                data=query_vectors, 
                anns_field="vector", 
                param=search_params, 
                limit=top_k, 
                expr=expr,
                output_fields=output_fields
            )
            return results
        except Exception as e:
            logger.error("Milvus search failed: %s", e)
            try:
                results = self.collection.search(
                    data=query_vectors, 
                    anns_field="vector", 
                    param=search_params, 
                    limit=top_k, 
                    expr=expr,
                    output_fields=[]
                )
                return results
            except Exception as e2:
                logger.error("Milvus search retry failed: %s", e2)
                return []

    def delete_by_article_ids(self, article_ids):
        if not article_ids:
            return 0
        try:
            if not hasattr(self, "collection"):
                return 0

            # 确保集合已加载
            self.collection.load()

            # 去重并清理非法 ID
            unique_ids = [int(i) for i in set(article_ids) if i is not None]
            if not unique_ids:
                return 0

            total_deleted = 0
            batch_size = 1000
            for i in range(0, len(unique_ids), batch_size):
                batch = unique_ids[i:i + batch_size]
                expr = f"article_id in [{','.join(map(str, batch))}]"
                result = self.collection.delete(expr)
                total_deleted += getattr(result, "delete_count", 0)

            self.collection.flush()
            try:
                # 触发压实以便尽快清理已删除数据
                self.collection.compact()
            except Exception as e:
                print(f"Milvus compact failed: {e}")

            return total_deleted
        except Exception as e:
            print(f"Failed to delete vectors for articles {article_ids}: {e}")
            return 0

milvus_service = MilvusService()
