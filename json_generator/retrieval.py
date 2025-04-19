from typing import List


class SimpleRetrievalAgent:
    """
    Простейшая реализация ретривера: ищет по векторному хранилищу релевантные документы.
    Ожидает, что vector_store реализует метод search(query: str, top_k: int) -> List[str].
    """

    def __init__(self, name: str, vector_store, top_k: int = 5):
        self.name = name
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> List[str]:
        # Возвращаем список текстов документов
        return self.vector_store.search(query, top_k=self.top_k)
