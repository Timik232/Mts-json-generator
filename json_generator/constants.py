"""Файл для констант"""
import os

API_URL = os.environ.get("API_URL", "https://api.gpt.mws.ru")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.3-70b-instruct")
SYSTEM_JSON_CREATOR = (
    "Используя документацию и json-schema,"
    "тебе нужно создать Json схему. Ответ должен"
    "содержать только json-схему без дополнительных комментариев."
)
JSON_DESCRIPTION = "Бот создаёт Json-схему на основе предоставленной документации."
JSON_TASK = (
    "Сгенерируй json-схему на основе информации от пользователя. "
    "Пример: "
    + """

{
    "name": "Kafka-kafka",
    "type": "complex",
    "description": "Перекладывание сообщений из кафки в кафку",
    "compiled": {
        "activities": [
            {
                "id": "activity-1",
                "type": "workflow_call",
                "description": "",
                "workflowCall": {
                    "workflowDef": {
                        "type": "send_to_kafka",
                        "details": {
                            "sendToKafkaConfig": {
                                "topic": "45",
                                "key": "",
                                "message": {
                                    "payload": "jp{payload}"
                                },
                                "connectionDef": {
                                    "bootstrapServers": "bootstrap.kafka.ru:443",
                                    "authDef": {
                                        "type": "SASL",
                                        "sasl": {
                                            "protocol": "SASL_SSL",
                                            "mechanism": "OAUTHBEARER",
                                            "username": "",
                                            "password": "",
                                            "sslDef": {
                                                "trustStoreType": "PEM",
                                                "trustStoreCertificates": ""
                                            },
                                            "tokenUrl": "https://isso.mts.ru/auth/"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ],
        "start": "activity-1"
    },

    "details": {
        "inputValidateSchema": {
            "type": "object",
            "required": [
                "payload"
            ],
            "properties": {
                "payload": {
                    "type": "object"
                }
            }
        },
        "starters": [
            {
                "name": "Kafka-kafka-KION",
                "type": "kafka_consumer",
                "kafkaConsumer": {
                    "topic": "rtk-kion",
                    "connectionDef": {
                        "bootstrapServers": "11.111.111.11:9094",
                        "authDef": {
                            "type": "TLS",
                            "tls": {
                                "trustStoreType": "PEM",
                                "trustStoreCertificates": "",
                                "keyStoreKey": "",
                                "keyStoreCertificates": ""
                            }
                        }
                    },
                    "payloadValidateSchema": {},
                    "keyValidateSchema": {},
                    "headersValidateSchema": {},
                    "outputTemplate": {
                        "payload": "jp{payload}"
                    }
                }
            }
        ]
    }
}
"""
    + " Информация: "
)
SYSTEM_CLARIFIER = (
    "Тебе нужно составить запрос для агента для создания схемы, но "
    "для этого необходимо уточнить недостающие поля."
    "Если все необходимые поля уже есть, то сообщи об"
    "этом. Если нужно, можешь вызвать функцию для вызова"
    "документации. Напиши TERMINATE когда задача выполнена или если"
    "все необходимые поля представлены и тебе больше не нужно вызывать "
    "функцию."
)
SYSTEM_CLARIFIER_WITHOUT_TERMINATE = (
    "Тебе нужно составить запрос для агента для создания схемы, но "
    "для этого необходимо уточнить недостающие поля."
    "Если все необходимые поля уже есть, то сообщи об"
    "этом. "
)
CLARIFIER_DESCRIPTION = "Бот уточняет недостающие поля для создания Json-схемы."
CLARIFIER_TASK = (
    "Выше сообщения пользователя. По сообщению пользователя и документации"
    " тебе нужно определить, для каких полей не хватает информации. Документация"
    " состоит из json-схемы. "
    "Составь список полей, по которым нужна дополнительная информация, и сообщение "
    "для пользователя."
    " Если документации нет или она не подходит к запросу "
    "пользователя,"
    "то можешь использовать вызов функции retrieve_documents для поиска. "
)
CLARIFY_JSON_TASK = (
    "До этого общий список полей, которые должны быть. По приведённому рассуждению составь ответ "
    " . Поля, по которым пользователь написал информацию, необходимую для заполнения,"
    " занеси в mentioned_params в виде словаря с ключом и значением. В mentiond_params вноси"
    " ТОЛЬКО ключи из обязательных полей, по которым пользователь сообщил информацию! "
    "В missing укажи список из полей, по которым от пользователя нет информации. "
    " can_generate_schema False если есть Missing, если нет, то True."
    " message для сообщения для пользователя, чтобы сказать ему,"
    "какую информацию он должен предоставить, при этом обязательно включи название"
    " схемы, которая была найдена: для какой схемы нужно уточнить поля"
    ", missing и can_generate_schema. Если в"
    "предыдущих сообщениях поля были, то в can_generate true. Если"
    "пользователь привёл большой список параметров, то делай true. "
)
CONTEXT_TOKENS = 131072
COMPLETION_TOKENS = 131072
JSON_OUTPUT = True
VISION = True
FUNCTION_CALLING = True
STRUCTURED_OUTPUT = True
