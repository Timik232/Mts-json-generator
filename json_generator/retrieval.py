"""Файл для реализации ретривера, который ищет по векторному хранилищу релевантные документы."""
import logging
from typing import List

import lancedb
import langchain
import langchain.chains
import langchain.document_loaders
import langchain.prompts
from langchain_community.vectorstores import LanceDB


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
