from .storage import TigerGraphStorage

from lightrag import LightRAG


# Define a subclass to include your custom graph storage in the storage mapping
class CustomLightRAG(LightRAG):
    def _get_storage_class(self):
        # Extend the default storage mapping with your custom storage
        base_mapping = super()._get_storage_class()
        base_mapping["TigerGraphStorage"] = TigerGraphStorage
        return base_mapping
