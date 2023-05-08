class PushPullMixin:
    def pull_query(self, collection_name: str = None) -> dict:
        return {"$pull": {collection_name if collection_name else self.get_motor_collection().name: self.to_ref()}}

    def push_query(self, collection_name: str = None) -> dict:
        return {"$push": {collection_name if collection_name else self.get_motor_collection().name: self.to_ref()}}
