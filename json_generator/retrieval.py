"""Модуль для гибридного поиска по JSON-документам с использованием BM25 и векторного поиска.

Этот модуль предоставляет функциональность для:
- Разбиения JSON на отдельные документы
- Создания векторных эмбеддингов
- Хранения документов в LanceDB
- Гибридного поиска с использованием BM25 и векторного поиска
"""

import uuid
import re
import json
import lancedb
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import logging

import langchain
import langchain.document_loaders
from langchain_community.vectorstores import LanceDB
from langchain_community.embeddings import HuggingFaceEmbeddings
import langchain.chains
import langchain.prompts
import pyarrow as pa


def split_json(json_data: dict[Any]) -> List[Dict[str, Any]]:
    """Разбивает JSON на отдельные документы с текстовым содержимым.

    Args:
        json_data (dict[Any]): Входной JSON-объект для разбиения.

    Returns:
        List[Dict[str, Any]]: Список документов, где каждый документ содержит:
            - id: уникальный идентификатор
            - content: текстовое представление данных
            - original_key: оригинальный ключ из JSON
            - original_value: оригинальное значение в формате JSON
    """
    result = []
    for key, value in json_data.items():
        # Создаем текстовое представление
        if isinstance(value, dict):
            # Для словарей создаем структурированный текст
            text_parts = [f"{k}: {v}" for k, v in value.items()]
            content = f"{key} {' '.join(text_parts)}"
        else:
            # Для других типов просто создаем строку
            content = f"{key}: {value}"
        
        # Создаем документ
        doc = {
            'id': str(uuid.uuid4()),
            'content': content,
            'original_key': key,
            'original_value': json.dumps(value)
        }
        result.append(doc)
    return result


def preprocess_text(text: str) -> str:
    """Предобработка текста для улучшения поиска.

    Args:
        text (str): Исходный текст для обработки.

    Returns:
        str: Обработанный текст с удаленными специальными символами
             и нормализованными пробелами.
    """
    # Удаляем специальные символы и приводим к нижнему регистру
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Заменяем множественные пробелы на один
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def preprocess_query(query: str) -> str:
    """Предобработка запроса для улучшения поиска.

    Args:
        query (str): Исходный поисковый запрос.

    Returns:
        str: Обработанный запрос, готовый для поиска.
    """
    # Приводим к нижнему регистру
    query = query.lower()
    # Удаляем специальные символы
    query = re.sub(r'[^\w\s]', ' ', query)
    # Заменяем множественные пробелы на один
    query = re.sub(r'\s+', ' ', query)
    return query.strip()


class JsonToLanceDB:
    """Класс для работы с JSON-документами в LanceDB.

    Attributes:
        db (lancedb.DB): Подключение к базе данных LanceDB.
        table_name (str): Имя таблицы для хранения документов.
        table (lancedb.Table): Таблица с документами.
        embeddings (HuggingFaceEmbeddings): Модель для создания эмбеддингов.
    """

    def __init__(self, db_path: str, table_name: str):
        """Инициализирует подключение к LanceDB и модель эмбеддингов.

        Args:
            db_path (str): Путь к базе данных LanceDB.
            table_name (str): Имя таблицы для хранения документов.
        """
        self.db = lancedb.connect(db_path)
        self.table_name = table_name
        self.table = None
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def add_to_lancedb(self, objects: List[Dict[str, Any]]) -> None:
        """Добавляет документы в LanceDB.

        Args:
            objects (List[Dict[str, Any]]): Список документов для добавления.
        """
        if not objects:
            return

        # Создаем векторные эмбеддинги для каждого документа
        texts = [obj['content'] for obj in objects]
        vectors = self.embeddings.embed_documents(texts)
        
        # Создаем DataFrame с данными
        data = {
            'id': [obj['id'] for obj in objects],
            'content': [obj['content'] for obj in objects],
            'vector': vectors,
            'original_key': [obj['original_key'] for obj in objects],
            'original_value': [obj['original_value'] for obj in objects]
        }
        df = pd.DataFrame(data)

        # Create table if it doesn't exist
        if self.table is None:
            self.table = self.db.create_table(self.table_name, data=df, mode="overwrite")
        else:
            self.table.add(df)

    def process_json_to_lancedb(self, json_data: dict[Any]) -> None:
        """Обрабатывает JSON и добавляет его в LanceDB.

        Args:
            json_data (dict[Any]): JSON-объект для обработки.
        """
        objects = split_json(json_data)
        self.add_to_lancedb(objects)

    def display_table_contents(self, limit: int = 10) -> None:
        """
        Отображает содержимое таблицы в удобном для чтения формате.
        
        Args:
            limit (int): Максимальное количество записей для отображения
        """
        if self.table is None:
            print("Таблица не существует или не была инициализирована")
            return
            
        # Получаем данные из таблицы
        data = self.table.to_pandas().head(limit)
        
        print(f"\nСодержимое таблицы '{self.table_name}':")
        print("-" * 80)
        for idx, row in data.iterrows():
            print(f"Запись #{idx + 1}")
            print(f"ID: {row['id']}")
            try:
                # Парсим JSON и выводим в читаемом формате
                content = json.loads(row['content'])
                print(f"Содержимое: {json.dumps(content, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"Ошибка при парсинге JSON: {e}")
                print(f"Сырые данные: {row['content']}")
            print("-" * 80)


def extract_text_from_json(json_str: str) -> str:
    """Извлекает текстовое содержимое из JSON-строки"""
    try:
        # Пробуем распарсить JSON
        data = json.loads(json_str)
        # Если это строка, возвращаем её
        if isinstance(data, str):
            return data
        # Если это словарь, извлекаем все строковые значения
        if isinstance(data, dict):
            text_parts = []
            for key, value in data.items():
                if isinstance(value, str):
                    text_parts.append(f"{key} {value}")
                elif isinstance(value, (dict, list)):
                    text_parts.append(json.dumps(value))
            return " ".join(text_parts)
        # Если это список, соединяем все элементы
        if isinstance(data, list):
            return " ".join(str(item) for item in data)
        return str(data)
    except json.JSONDecodeError:
        return json_str

def tokenize_text(text: str) -> List[str]:
    """Токенизация текста с учетом особенностей JSON"""
    # Извлекаем текстовое содержимое из JSON
    text = extract_text_from_json(text)
    # Предобрабатываем текст
    text = preprocess_text(text)
    # Разбиваем на слова, сохраняя структуру JSON
    tokens = []
    for word in text.split():
        # Если это JSON-ключ или значение, разбиваем по camelCase и snake_case
        if '_' in word or any(c.isupper() for c in word):
            # Разбиваем по camelCase
            camel_case = re.sub('([A-Z][a-z]+)', r' \1', word)
            # Разбиваем по snake_case
            snake_case = camel_case.replace('_', ' ')
            tokens.extend(snake_case.lower().split())
        else:
            tokens.append(word)
    return tokens


class SimpleRetrievalAgent:
    """Агент для гибридного поиска по документам.

    Использует комбинацию BM25 и векторного поиска для нахождения
    наиболее релевантных документов.

    Attributes:
        db_path (str): Путь к базе данных LanceDB.
        table_name (str): Имя таблицы с документами.
        top_k (int): Количество возвращаемых результатов.
        embeddings (HuggingFaceEmbeddings): Модель для создания эмбеддингов.
        db (lancedb.DB): Подключение к базе данных.
        table (lancedb.Table): Таблица с документами.
        bm25 (BM25Okapi): Индекс для BM25 поиска.
        tokenized_docs (List[List[str]]): Токенизированные документы.
        original_docs (pd.DataFrame): Оригинальные документы.
        vector_store (LanceDB): Векторное хранилище для поиска.
    """

    def __init__(self, db_path: str, table_name: str, top_k: int = 5):
        """Инициализирует агент поиска.

        Args:
            db_path (str): Путь к базе данных LanceDB.
            table_name (str): Имя таблицы с документами.
            top_k (int, optional): Количество возвращаемых результатов.
                                 По умолчанию 5.
        """
        self.db_path = db_path
        self.table_name = table_name
        self.top_k = top_k
        
        # Инициализация эмбеддингов
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Подключение к базе данных
        self.db = lancedb.connect(db_path)
        if table_name not in self.db.table_names():
            raise ValueError(f"Таблица {table_name} не существует в базе данных")
            
        self.table = self.db.open_table(table_name)
        
        # Инициализация BM25
        self._init_bm25()
        
        # Инициализация векторного хранилища
        self.vector_store = LanceDB(
            table=self.table,
            embedding=self.embeddings,
            text_key="content",
            vector_key="vector"
        )
        
        logging.basicConfig(level=logging.INFO, filename="retrieval_log.log", filemode="w", encoding='utf-8')

    def _init_bm25(self):
        """Инициализирует BM25 индекс для поиска."""
        docs = self.table.to_pandas()
        # Токенизируем тексты
        self.tokenized_docs = []
        for doc in docs['content']:
            tokens = doc.split()
            if tokens:  # Проверяем, что есть токены
                self.tokenized_docs.append(tokens)
        
        if not self.tokenized_docs:
            raise ValueError("Нет документов для индексации BM25")
            
        self.bm25 = BM25Okapi(self.tokenized_docs)
        self.original_docs = docs

    def hybrid_search(self, query: str, alpha: float = 0.5) -> List[Dict[str, Any]]:
        """Выполняет гибридный поиск по документам.

        Args:
            query (str): Поисковый запрос.
            alpha (float, optional): Вес векторного поиска в комбинированной оценке.
                                   По умолчанию 0.5.

        Returns:
            List[Dict[str, Any]]: Список найденных документов с оценками.
        """
        try:
            # Предобрабатываем запрос
            processed_query = preprocess_query(query)
            
            # BM25 поиск
            bm25_scores = self.bm25.get_scores(processed_query.split())
            
            # Векторный поиск
            query_embedding = self.embeddings.embed_query(processed_query)
            vector_results = self.table.search(query_embedding, vector_column_name="vector").limit(self.top_k).to_pandas()
            
            # Создаем массив для векторных оценок
            vector_scores = np.zeros(len(self.original_docs))
            if not vector_results.empty:
                for idx, row in vector_results.iterrows():
                    try:
                        doc_idx = self.original_docs[self.original_docs['id'] == row['id']].index[0]
                        vector_scores[doc_idx] = 1 - row['_distance'] / vector_results['_distance'].max()
                    except Exception as e:
                        logging.error(f"Ошибка при обработке документа {row['id']}: {str(e)}")
            
            # Нормализуем BM25 оценки
            bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-6)
            
            # Комбинируем оценки
            combined_scores = alpha * vector_scores + (1 - alpha) * bm25_scores
            
            # Получаем топ-k результатов
            top_indices = np.argsort(combined_scores)[-self.top_k:][::-1]
            
            # Форматируем результаты
            results = []
            for idx in top_indices:
                doc = self.original_docs.iloc[idx]
                results.append({
                    "content": doc['content'],
                    "score": combined_scores[idx],
                    "bm25_score": bm25_scores[idx],
                    "vector_score": vector_scores[idx],
                    "metadata": {
                        "id": doc['id'],
                        "original_key": doc['original_key'],
                        "original_value": doc['original_value']
                    }
                })
            
            return results
            
        except Exception as e:
            logging.error(f"Ошибка при гибридном поиске: {str(e)}")
            return []

    def display_hybrid_search_results(self, query: str, alpha: float = 0.5) -> None:
        """Отображает результаты гибридного поиска.

        Args:
            query (str): Поисковый запрос.
            alpha (float, optional): Вес векторного поиска в комбинированной оценке.
                                   По умолчанию 0.5.
        """
        results = self.hybrid_search(query, alpha)
        
        if not results:
            print(f"\nПо запросу '{query}' ничего не найдено")
            return
            
        print(f"\nРезультаты гибридного поиска по запросу: '{query}'")
        print(f"Вес векторного поиска: {alpha}")
        print("-" * 80)
        
        for idx, result in enumerate(results, 1):
            print(f"Результат #{idx}")
            print(f"Общий score: {result['score']:.4f}")
            print(f"BM25 score: {result['bm25_score']:.4f}")
            print(f"Векторный score: {result['vector_score']:.4f}")
            print("Содержимое:")
            print(result['content'])
            print("Метаданные:")
            print(json.dumps(result['metadata'], ensure_ascii=False, indent=2))
            print("-" * 80)


## Example usage

processor = JsonToLanceDB(db_path="./lancedb", table_name="documents")
with open('json_generator\DefinitionJSONwithreq.json', 'r') as file:
    data = json.load(file)
processor.process_json_to_lancedb(data)

# Создаем ретривер и тестируем поиск
retriever = SimpleRetrievalAgent(
    db_path="./lancedb",
    table_name="documents",
    top_k=2
)

# Тестируем поиск с alpha=0.3
query = "Отправка в REST API"
retriever.display_hybrid_search_results(query, alpha=0.3)
