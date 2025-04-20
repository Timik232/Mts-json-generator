import json
import logging
import uuid
from typing import Any, Dict, List

import lancedb
import langchain
import langchain.chains
import langchain.document_loaders
import langchain.prompts
import pyarrow as pa
from langchain_community.vectorstores import LanceDB


def split_json(json_data: dict[Any]) -> List[Dict[str, Any]]:
    parsed_data = json_data
    result = []
    for item in parsed_data.items():
        obj_id = parsed_data.get("id", str(uuid.uuid4()))
        content = json.dumps(f"{item[0]} structure: {item[1]}")
        result.append({"id": obj_id, "content": content})
    return result


class JsonToLanceDB:
    def __init__(self, db_path: str, table_name: str):
        self.db = lancedb.connect(db_path)
        self.table_name = table_name
        self.table = None

    def add_to_lancedb(self, objects: List[Dict[str, Any]]) -> None:
        if not objects:
            print("No objects to add to LanceDB")
            return

        # Create table if it doesn't exist
        if self.table is None:
            schema = pa.schema([("id", pa.string()), ("content", pa.string())])

            self.table = self.db.create_table(
                self.table_name, schema=schema, mode="overwrite"
            )

        # Add documents to table
        self.table.add(objects)
        print(f"Successfully added {len(objects)} documents to {self.table_name}")

    def process_json_to_lancedb(self, json_data: dict[Any]) -> None:
        objects = split_json(json_data)
        self.add_to_lancedb(objects)


class SimpleRetrievalAgent:
    """
    Простейшая реализация ретривера: ищет по векторному хранилищу релевантные документы.
    Ожидает, что vector_store реализует метод search(query: str, top_k: int) -> List[str].
    """

    def __init__(self, name: str, vector_store, top_k: int = 5):
        self.name = name
        self.vector_store = vector_store
        self.top_k = top_k
        if self.vector_store:
            db = lancedb.connect(self.vector_store)
            table = db.open_table("vector_index")
            self.embeddings = langchain.embeddings.HuggingFaceEmbeddings(
                model_name="distiluse-base-multilingual-cased-v1"
            )
            self.vec_store = LanceDB(table, self.embeddings)
        logging.basicConfig(
            level=logging.INFO,
            filename="generation_log.log",
            filemode="w",
            encoding="utf-8",
        )

    def retrieve(self, query: str) -> List[str]:
        search_results = self.vec_store.similarity_search(query, k=self.top_k)
        results = [doc.page_content for doc in search_results]
        if search_results:
            min_distance = search_results[0].metadata.get("_distance", 0)
            logging.info(f"Closest document distance: {min_distance}")
        return results
