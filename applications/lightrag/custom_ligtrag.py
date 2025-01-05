from .storage.tigergraph_storage import TigerGraphStorage
from .storage.tigervector_storage import TigerVectorStorage

from lightrag import LightRAG


# Define a subclass to include your custom graph storage in the storage mapping
class CustomLightRAG(LightRAG):
    def _get_storage_class(self):
        # Extend the default storage mapping with your custom storage
        base_mapping = super()._get_storage_class()
        base_mapping["TigerGraphStorage"] = TigerGraphStorage
        base_mapping["TigerVectorStorage"] = TigerVectorStorage
        return base_mapping
