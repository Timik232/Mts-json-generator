workflow_rule_tree = {
    "wf_definition": {
        "description": "Workflow definition",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "Type of WF (e.g., complex, await_for_message, rest_call, etc.)",
                "valid_values": ["complex", "await_for_message", "rest_call", "db_call", "send_to_rabbitmq", "send_to_sap", "transform"]
            },
            "name": {
                "type": "String255",
                "required": True,
                "description": "Name of WF"
            },
            "tenantId": {
                "type": "String255",
                "required": False,
                "description": "ID of the system using WF"
            },
            "version": {
                "type": "Int",
                "required": False,
                "description": "Version of WF"
            },
            "description": {
                "type": "String4000",
                "required": False,
                "description": "Description of WF"
            },
            "compiled": {
                "type": "Compiled",
                "required": True,
                "required_cond": "type == 'complex'",
                "description": "Composite type for complex WF",
                "subcomponents": {
                    "start": {
                        "type": "String255",
                        "required": True,
                        "description": "Activity ID for WF entry point"
                    },
                    "activities": {
                        "type": "Activity array",
                        "required": True,
                        "description": "Array of activities in WF"
                    },
                    "outputTemplate": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Filter for output data"
                    }
                }
            },
            "details": {
                "type": "DefinitionDetails",
                "required": True,
                "required_cond": "type != 'complex'",
                "description": "Input/output parameters or details",
                "subcomponents": {
                    "inputValidateSchema": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "JSON schema for input validation"
                    },
                    "outputValidateSchema": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "JSON schema for output validation"
                    },
                    "starters": {
                        "type": "Starters array",
                        "required": True,
                        "description": "Parameters for starting WF"
                    },
                    "sendToKafkaConfig": {
                        "type": "sendToKafkaConfig",
                        "required": True,
                        "required_cond": "type == 'send_to_kafka'",
                        "description": "Kafka configuration"
                    },
                    "sendToS3Config": {
                        "type": "sendToS3Config",
                        "required": True,
                        "required_cond": "type == 'send_to_s3'",
                        "description": "S3 configuration"
                    },
                    "restCallConfig": {
                        "type": "restCallConfig",
                        "required": True,
                        "required_cond": "type == 'rest_call'",
                        "description": "REST call configuration"
                    },
                    "xsltTransformConfig": {
                        "type": "xsltTransformConfig",
                        "required": True,
                        "required_cond": "type == 'xslt_transform'",
                        "description": "XSLT transformation configuration"
                    },
                    "databaseCallConfig": {
                        "type": "databaseCallConfig",
                        "required": True,
                        "required_cond": "type == 'db_call'",
                        "description": "Database call configuration"
                    },
                    "sendToRabbitmqConfig": {
                        "type": "sendToRabbitmqConfig",
                        "required": True,
                        "required_cond": "type == 'send_to_rabbitmq'",
                        "description": "RabbitMQ configuration"
                    },
                    "awaitForMessageConfig": {
                        "type": "awaitForMessageConfig",
                        "required": True,
                        "required_cond": "type == 'await_for_message'",
                        "description": "Await message configuration"
                    },
                    "sendToSapConfig": {
                        "type": "sendToSapConfig",
                        "required": True,
                        "required_cond": "type == 'send_to_sap'",
                        "description": "SAP configuration"
                    }
                }
            },
            "flowEditorConfig": {
                "type": "Composite",
                "required": False,
                "description": "UI data, does not affect execution"
            }
        }
    },
    "starters": {
        "description": "Starter configurations",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "Starter type",
                "valid_values": ["kafka_consumer", "sap_inbound", "rest_call", "scheduler", "rabbitmq_consumer", "mail_consumer"],
                "default": "rest_call"
            },
            "name": {
                "type": "String255",
                "required": True,
                "required_cond": "type != 'rest_call'",
                "description": "Starter name"
            },
            "description": {
                "type": "String255",
                "required": False,
                "description": "Starter description"
            },
            "rabbitmqConsumer": {
                "type": "rabbitmqConsumer",
                "required": True,
                "required_cond": "type == 'rabbitmq_consumer'",
                "description": "RabbitMQ consumer configuration"
            },
            "kafkaConsumer": {
                "type": "kafkaConsumer",
                "required": True,
                "required_cond": "type == 'kafka_consumer'",
                "description": "Kafka consumer configuration"
            },
            "sapInbound": {
                "type": "sapInbound",
                "required": True,
                "required_cond": "type == 'sap_inbound'",
                "description": "SAP inbound configuration"
            },
            "shedulerStarter": {
                "type": "shedulerStarter",
                "required": True,
                "required_cond": "type == 'scheduler'",
                "description": "Scheduler configuration"
            }
        }
    },
    "starter_rest": {
        "description": "REST starter",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "REST call starter",
                "value": "rest_call",
                "note": "Must define details.inputValidateSchema if using specific start data"
            }
        }
    },
    "starter_rabbitmq": {
        "description": "RabbitMQ starter",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "RabbitMQ consumer starter",
                "value": "rabbitmq_consumer"
            },
            "name": {
                "type": "String255",
                "required": True,
                "description": "Starter name"
            },
            "description": {
                "type": "String255",
                "required": False,
                "description": "Starter description"
            },
            "rabbitmqConsumer": {
                "type": "rabbitmqConsumer",
                "required": True,
                "description": "RabbitMQ consumer details",
                "subcomponents": {
                    "queue": {
                        "type": "String255",
                        "required": True,
                        "description": "Queue name"
                    },
                    "connectionDef": {
                        "type": "connectionDef",
                        "required": True,
                        "description": "Connection parameters",
                        "subcomponents": {
                            "userName": {
                                "type": "String255",
                                "required": True,
                                "description": "Username"
                            },
                            "userPass": {
                                "type": "String255",
                                "required": True,
                                "description": "Password"
                            },
                            "addresses": {
                                "type": "Array",
                                "required": True,
                                "description": "Connection address and port"
                            },
                            "virtualHost": {
                                "type": "String255",
                                "required": True,
                                "description": "Virtual host"
                            }
                        }
                    },
                    "payloadValidateSchema": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Message validation schema"
                    },
                    "outputTemplate": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Variable declaration based on message data"
                    }
                }
            }
        }
    },
    "starter_kafkaConsumer": {
        "description": "Kafka consumer starter",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "Kafka consumer starter",
                "value": "kafka_consumer"
            },
            "name": {
                "type": "String255",
                "required": True,
                "description": "Starter name"
            },
            "description": {
                "type": "String255",
                "required": False,
                "description": "Starter description"
            },
            "kafkaConsumer": {
                "type": "kafkaConsumer",
                "required": True,
                "description": "Kafka consumer details",
                "subcomponents": {
                    "topic": {
                        "type": "String255",
                        "required": True,
                        "description": "Topic name"
                    },
                    "connectionDef": {
                        "type": "connectionDef",
                        "required": True,
                        "description": "Connection parameters",
                        "subcomponents": {
                            "bootstrapServers": {
                                "type": "String255",
                                "required": True,
                                "description": "Connection address"
                            },
                            "authDef": {
                                "type": "authDef",
                                "required": True,
                                "description": "Authentication parameters",
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "required_cond": "auth present",
                                        "description": "Authentication type",
                                        "valid_values": ["SASL", "TLS"]
                                    },
                                    "sasl": {
                                        "type": "sasl",
                                        "required": True,
                                        "required_cond": "auth == 'sasl'",
                                        "description": "SASL authentication"
                                    },
                                    "tls": {
                                        "type": "tls",
                                        "required": True,
                                        "required_cond": "auth == 'tls'",
                                        "description": "TLS authentication"
                                    }
                                }
                            }
                        }
                    },
                    "payloadValidateSchema": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Message validation schema"
                    },
                    "keyValidateSchema": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Key validation schema"
                    },
                    "headersValidateSchema": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Headers validation schema"
                    },
                    "outputTemplate": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Variable declaration based on message data"
                    }
                }
            }
        }
    },
    "starter_sapInbound": {
        "description": "SAP inbound starter",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "SAP inbound starter",
                "value": "sap_inbound"
            },
            "inboundDef": {
                "type": "inboundDef",
                "required": True,
                "description": "SAP inbound details",
                "subcomponents": {
                    "name": {
                        "type": "String255",
                        "required": True,
                        "description": "Starter name"
                    },
                    "connectionDef": {
                        "type": "connectionDef",
                        "required": True,
                        "description": "Connection parameters",
                        "subcomponents": {
                            "props": {
                                "type": "props",
                                "required": True,
                                "description": "Connection properties",
                                "subcomponents": {
                                    "jco.client.lang": {
                                        "type": "String255",
                                        "required": True,
                                        "description": "Client language"
                                    },
                                    "jco.client.passwd": {
                                        "type": "String255",
                                        "required": True,
                                        "description": "Password"
                                    },
                                    "jco.client.user": {
                                        "type": "String255",
                                        "required": True,
                                        "description": "Username"
                                    },
                                    "jco.client.sysnr": {
                                        "type": "Int",
                                        "required": True,
                                        "description": "SAP system number"
                                    },
                                    "jco.destination.pool_capacity": {
                                        "type": "Int",
                                        "required": True,
                                        "description": "Max connections in pool"
                                    },
                                    "jco.destination.peak_limit": {
                                        "type": "Int",
                                        "required": True,
                                        "description": "Max simultaneous connections"
                                    },
                                    "jco.client.client": {
                                        "type": "Int",
                                        "required": True,
                                        "description": "SAP client number"
                                    },
                                    "jco.client.ashost": {
                                        "type": "String255",
                                        "required": True,
                                        "description": "Host"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "starter_scheduler": {
        "description": "Scheduler starter",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "Scheduler starter",
                "value": "scheduler"
            },
            "name": {
                "type": "String255",
                "required": True,
                "description": "Starter name"
            },
            "description": {
                "type": "String255",
                "required": False,
                "description": "Starter description"
            },
            "scheduler": {
                "type": "scheduler",
                "required": True,
                "description": "Scheduler details",
                "subcomponents": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "description": "Scheduler type",
                        "value": "cron"
                    },
                    "cron": {
                        "type": "cron",
                        "required": True,
                        "description": "Cron schedule",
                        "subcomponents": {
                            "dayOfWeek": {
                                "type": "String255",
                                "required": True,
                                "required_cond": "at least one cron parameter required",
                                "description": "Day of week"
                            },
                            "month": {
                                "type": "String255",
                                "required": True,
                                "required_cond": "at least one cron parameter required",
                                "description": "Month interval"
                            },
                            "dayOfMonth": {
                                "type": "String255",
                                "required": True,
                                "required_cond": "at least one cron parameter required",
                                "description": "Day of month"
                            },
                            "hour": {
                                "type": "String255",
                                "required": True,
                                "required_cond": "at least one cron parameter required",
                                "description": "Hour"
                            },
                            "minute": {
                                "type": "String255",
                                "required": True,
                                "required_cond": "at least one cron parameter required",
                                "description": "Minute"
                            }
                        }
                    },
                    "startDateTime": {
                        "type": "Date",
                        "required": True,
                        "description": "Start date and time"
                    },
                    "endDateTime": {
                        "type": "Date",
                        "required": False,
                        "description": "End date and time"
                    }
                }
            }
        }
    },
    "starter_mail_consumer": {
        "description": "Mail consumer starter",
        "parameters": {
            "type": {
                "type": "String255",
                "required": True,
                "description": "Mail consumer starter",
                "value": "mail_consumer"
            },
            "name": {
                "type": "String255",
                "required": True,
                "description": "Starter name"
            },
            "description": {
                "type": "String255",
                "required": False,
                "description": "Starter description"
            },
            "mailConsumer": {
                "type": "mailConsumer",
                "required": True,
                "description": "Mail consumer details",
                "subcomponents": {
                    "connectionDef": {
                        "type": "connectionDef",
                        "required": True,
                        "description": "Connection parameters",
                        "subcomponents": {
                            "protocol": {
                                "type": "String255",
                                "required": True,
                                "description": "Protocol",
                                "value": "imap"
                            },
                            "host": {
                                "type": "String255",
                                "required": True,
                                "description": "Connection host"
                            },
                            "port": {
                                "type": "String255",
                                "required": True,
                                "description": "Port"
                            },
                            "mailAuth": {
                                "type": "mailAuth",
                                "required": True,
                                "description": "Authentication parameters",
                                "subcomponents": {
                                    "username": {
                                        "type": "String255",
                                        "required": True,
                                        "description": "Email"
                                    },
                                    "password": {
                                        "type": "String255",
                                        "required": True,
                                        "description": "Password"
                                    }
                                }
                            }
                        }
                    },
                    "mailFilter": {
                        "type": "mailFilter",
                        "required": True,
                        "description": "Email filters",
                        "subcomponents": {
                            "senders": {
                                "type": "Array",
                                "required": False,
                                "description": "Sender emails"
                            },
                            "subjects": {
                                "type": "Array",
                                "required": False,
                                "description": "Email subjects"
                            },
                            "startMailDateTime": {
                                "type": "Date",
                                "required": False,
                                "description": "Start date for unread emails"
                            }
                        }
                    }
                }
            }
        }
    },
    "Activity": {
        "description": "Base entity for workflow activities",
        "parameters": {
            "id": {
                "type": "String255",
                "required": True,
                "description": "Unique identifier for the activity. Must be unique within a business process."
            },
            "description": {
                "type": "String255",
                "required": False,
                "description": "Description of the activity step."
            },
            "transition": {
                "type": "String255",
                "required": True,
                "description": "ID of the next activity. Set to null if the process or branch ends."
            },
            "type": {
                "type": "String255",
                "required": True,
                "description": "Type of activity",
                "values": [
                    "workflow_call",
                    "inject",
                    "switch",
                    "timer",
                    "transform",
                    "parallel"
                ]
            },
            "workflowCall": {
                "type": "WorkflowCall",
                "required": True,
                "condition": "type == 'workflow_call' or type == 'inject'",
                "description": "Parameters for workflow_call activity type",
                "subcomponents": {
                    "args": {
                        "type": "JsonObject",
                        "required": False,
                        "description": "Input arguments for the activity."
                    },
                    "workflowRef": {
                        "type": "Ref",
                        "required": True,
                        "condition": "!workflowDef",
                        "description": "Reference to a predefined workflow template.",
                        "subcomponents": {
                            "id": {
                                "type": "String-UUID",
                                "required": True,
                                "condition": "!name",
                                "description": "ID of the workflow template."
                            },
                            "name": {
                                "type": "String255",
                                "required": True,
                                "condition": "!id",
                                "description": "Name of the workflow template."
                            },
                            "version": {
                                "type": "Int",
                                "required": False,
                                "description": "Version of the template."
                            },
                            "tenantId": {
                                "type": "String255",
                                "required": False,
                                "description": "ID of the system using the template. Defaults to 'default'."
                            }
                        }
                    },
                    "workflowDef": {
                        "type": "SimpleWorkflowDefinition",
                        "required": True,
                        "condition": "!workflowRef",
                        "description": "Definition of the called subprocess.",
                        "subcomponents": {
                            "type": {
                                "type": "String255",
                                "required": True,
                                "description": "Type of workflow definition",
                                "values": [
                                    "await_for_message",
                                    "rest_call",
                                    "db_call",
                                    "send_to_rabbitmq",
                                    "send_to_sap",
                                    "xslt_transform",
                                    "send_to_kafka",
                                    "send_to_s3",
                                    "transform"
                                ]
                            },
                            "details": {
                                "type": "Details",
                                "required": True,
                                "description": "Details of the subprocess."
                            }
                        }
                    },
                    "retryConfig": {
                        "type": "retryConfig",
                        "required": False,
                        "description": "Retry policy configuration.",
                        "subcomponents": {
                            "initialInterval": {
                                "type": "String256",
                                "format": "ISO 8601 duration",
                                "required": False,
                                "description": "Initial retry interval. Default is 1 second."
                            },
                            "maxInterval": {
                                "type": "String256",
                                "format": "ISO 8601 duration",
                                "required": False,
                                "description": "Maximum interval between retries. Must be greater than initialInterval."
                            },
                            "maxAttempts": {
                                "type": "Int",
                                "required": False,
                                "description": "Maximum number of retry attempts."
                            },
                            "backoffCoefficient": {
                                "type": "Float",
                                "required": False,
                                "description": "Coefficient for increasing interval after each retry. Default is 2.0, minimum is 1.0."
                            }
                        }
                    },
                    "failActivityResult": {
                        "type": "failActivityResult",
                        "required": False,
                        "description": "Transition on unsuccessful retry completion.",
                        "subcomponents": {
                            "retryStates": {
                                "type": "Array",
                                "required": False,
                                "description": "States triggering transition on retry failure.",
                                "values": ["RETRY_STATE_MAXIMUM_ATTEMPTS_REACHED"]
                            },
                            "variables": {
                                "type": "JsonString",
                                "required": True,
                                "condition": "outputFilter exists",
                                "description": "Variables declared on retry exit."
                            }
                        }
                    }
                }
            },
            "injectData": {
                "type": "JsonObject",
                "required": True,
                "condition": "type == 'inject'",
                "description": "Data to be injected, e.g., constants or transformed variables."
            },
            "outputFilter": {
                "type": "String255",
                "required": False,
                "description": "Transforms outgoing data after activity completion."
            },
            "dataConditions": {
                "type": "Array",
                "required": True,
                "condition": "type == 'switch'",
                "description": "Conditions and actions for switch type.",
                "subcomponents": {
                    "condition": {
                        "type": "String400",
                        "required": True,
                        "description": "Condition script in Lua format."
                    },
                    "conditionDescription": {
                        "type": "String400",
                        "required": False,
                        "description": "Description of the condition."
                    },
                    "transition": {
                        "type": "String400",
                        "required": False,
                        "description": "Activity ID to transition to if condition is True."
                    }
                }
            },
            "defaultTransition": {
                "type": "DefaultDataTransition",
                "required": True,
                "condition": "type == 'switch'",
                "description": "Behavior if all conditions are False.",
                "subcomponents": {
                    "transition": {
                        "type": "String255",
                        "required": True,
                        "description": "Activity ID to transition to if all conditions are False."
                    },
                    "conditionDescription": {
                        "type": "String400",
                        "required": False,
                        "description": "Description of the default condition."
                    }
                }
            },
            "branches": {
                "type": "Array",
                "required": True,
                "condition": "type == 'parallel'",
                "description": "List of activity IDs to execute in parallel."
            },
            "completionType": {
                "type": "String255",
                "required": True,
                "condition": "type == 'parallel'",
                "description": "Completion type for parallel activities.",
                "values": ["anyOf", "allOf"]
            },
            "timerDuration": {
                "type": "String256",
                "format": "ISO 8601 duration",
                "required": True,
                "condition": "type == 'timer'",
                "description": "Duration before transitioning to the next activity."
            },
            "transform": {
                "type": "transformConfig",
                "required": True,
                "condition": "type == 'transform'",
                "description": "Transformation parameters.",
                "subcomponents": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "description": "Type of transformation.",
                        "values": ["xml_to_json", "json_to_xml"]
                    },
                    "target": {
                        "type": "JsonObject",
                        "required": True,
                        "description": "Target of transformation, e.g., variable containing the document."
                    }
                }
            }
        },
        "primitives": {
            "await_for_message": {
                "description": "Waits for a callback from an external system.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "await_for_message"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": False,
                                "description": "Input arguments for the activity."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "await_for_message"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "awaitForMessageConfig": {
                                                "type": "awaitForMessageConfig",
                                                "required": True,
                                                "description": "Configuration for expected message.",
                                                "subcomponents": {
                                                    "MessageName": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "Name of the expected message from the external system."
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "rest_call": {
                "description": "Makes a REST API call.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "rest_call"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": False,
                                "description": "Input arguments for the REST call."
                            },
                            "retryConfig": {
                                "type": "retryConfig",
                                "required": False,
                                "description": "Retry policy configuration."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "rest_call"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "inputValidateSchema": {
                                                "type": "JsonObject",
                                                "required": False,
                                                "description": "JSON schema for validating input variables."
                                            },
                                            "outputValidateSchema": {
                                                "type": "JsonObject",
                                                "required": False,
                                                "description": "JSON schema for validating output variables."
                                            },
                                            "restCallConfig": {
                                                "type": "restCallConfig",
                                                "required": True,
                                                "description": "REST call configuration.",
                                                "subcomponents": {
                                                    "resultHandlers": {
                                                        "type": "Array",
                                                        "required": False,
                                                        "description": "Conditions for successful call.",
                                                        "subcomponents": {
                                                            "predicate": {
                                                                "type": "predicate",
                                                                "required": True,
                                                                "subcomponents": {
                                                                    "respCode": {
                                                                        "type": "Int",
                                                                        "required": True,
                                                                        "condition": "!respCodes && !respCodeInterval",
                                                                        "description": "Response code."
                                                                    },
                                                                    "respCodes": {
                                                                        "type": "Array",
                                                                        "required": True,
                                                                        "condition": "!respCode && !respCodeInterval",
                                                                        "description": "List of response codes."
                                                                    },
                                                                    "respCodeInterval": {
                                                                        "type": "respCodeInterval",
                                                                        "required": True,
                                                                        "condition": "!respCode && !respCodes",
                                                                        "subcomponents": {
                                                                            "from": {
                                                                                "type": "Int",
                                                                                "required": False,
                                                                                "description": "Start of response code interval."
                                                                            },
                                                                            "to": {
                                                                                "type": "Int",
                                                                                "required": False,
                                                                                "description": "End of response code interval."
                                                                            }
                                                                        }
                                                                    },
                                                                    "respValueAnyOf": {
                                                                        "type": "Array",
                                                                        "required": False,
                                                                        "description": "Variable value conditions.",
                                                                        "subcomponents": {
                                                                            "jsonPath": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Path to the variable."
                                                                            },
                                                                            "values": {
                                                                                "type": "Array",
                                                                                "required": True,
                                                                                "description": "Possible values for the variable."
                                                                            },
                                                                            "and": {
                                                                                "type": "pathValueValidation",
                                                                                "required": False,
                                                                                "description": "Additional AND condition."
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "restCallTemplateRef": {
                                                        "type": "restCallTemplateRef",
                                                        "required": True,
                                                        "condition": "!restCallTemplateDef",
                                                        "description": "Reference to REST call template."
                                                    },
                                                    "restCallTemplateDef": {
                                                        "type": "restCallTemplateDef",
                                                        "required": True,
                                                        "condition": "!restCallTemplateRef",
                                                        "subcomponents": {
                                                            "method": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "condition": "!curl",
                                                                "description": "HTTP method (POST, PUT, etc.)."
                                                            },
                                                            "url": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "condition": "!curl",
                                                                "description": "URL for the REST call."
                                                            },
                                                            "bodyTemplate": {
                                                                "type": "String255",
                                                                "required": False,
                                                                "description": "Request body template."
                                                            },
                                                            "headers": {
                                                                "type": "headers",
                                                                "required": True,
                                                                "condition": "!curl",
                                                                "description": "Request headers."
                                                            },
                                                            "curl": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "condition": "!method && !url && !headers",
                                                                "description": "Escaped curl request."
                                                            },
                                                            "authDef": {
                                                                "type": "authDef",
                                                                "required": True,
                                                                "subcomponents": {
                                                                    "type": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "values": ["basic", "oauth2"],
                                                                        "description": "Authorization type."
                                                                    },
                                                                    "basic": {
                                                                        "type": "basic",
                                                                        "required": True,
                                                                        "condition": "type == 'basic'",
                                                                        "subcomponents": {
                                                                            "login": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Login for basic auth."
                                                                            },
                                                                            "password": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Password for basic auth."
                                                                            }
                                                                        }
                                                                    },
                                                                    "oauth2": {
                                                                        "type": "oauth2",
                                                                        "required": True,
                                                                        "condition": "type == 'oauth2'",
                                                                        "subcomponents": {
                                                                            "issuerLocation": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "URL for OAuth2 validation."
                                                                            },
                                                                            "clientId": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Client ID for OAuth2."
                                                                            },
                                                                            "clientSecret": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Client secret for OAuth2."
                                                                            },
                                                                            "grantType": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "value": "client_credentials",
                                                                                "description": "Grant type for OAuth2."
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "db_call": {
                "description": "Executes a database operation.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "db_call"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": False,
                                "description": "Input arguments for the database call."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "db_call"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "databaseCallConfig": {
                                                "type": "databaseCallConfig",
                                                "required": True,
                                                "description": "Database call configuration.",
                                                "subcomponents": {
                                                    "databaseCallRef": {
                                                        "type": "databaseCallRef",
                                                        "required": True,
                                                        "condition": "!databaseCallDef",
                                                        "description": "Reference to database call template."
                                                    },
                                                    "databaseCallDef": {
                                                        "type": "databaseCallDef",
                                                        "required": True,
                                                        "condition": "!databaseCallRef",
                                                        "subcomponents": {
                                                            "type": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "values": ["function", "select", "procedure"],
                                                                "description": "Type of database operation."
                                                            },
                                                            "sql": {
                                                                "type": "JSONString",
                                                                "required": True,
                                                                "condition": "type == 'select'",
                                                                "description": "SQL select query."
                                                            },
                                                            "schema": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "condition": "type == 'function'",
                                                                "description": "Database schema."
                                                            },
                                                            "catalog": {
                                                                "type": "String255",
                                                                "required": False,
                                                                "description": "Database catalog."
                                                            },
                                                            "functionName": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "condition": "type == 'function'",
                                                                "description": "Name of the function."
                                                            },
                                                            "inParameters": {
                                                                "type": "JSONString",
                                                                "required": False,
                                                                "description": "Input parameters for function or procedure."
                                                            },
                                                            "outParameters": {
                                                                "type": "JSONString",
                                                                "required": False,
                                                                "description": "Output parameters for function."
                                                            }
                                                        }
                                                    },
                                                    "dataSourceId": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "condition": "!dataSourceDef",
                                                        "description": "ID of the data source template."
                                                    },
                                                    "dataSourceDef": {
                                                        "type": "dataSourceDef",
                                                        "required": True,
                                                        "condition": "!dataSourceId",
                                                        "subcomponents": {
                                                            "url": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Database connection URL."
                                                            },
                                                            "className": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Database driver class name."
                                                            },
                                                            "userName": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Database username."
                                                            },
                                                            "userPass": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Database password."
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "send_to_rabbitmq": {
                "description": "Sends a message to RabbitMQ.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "send_to_rabbitmq"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": False,
                                "description": "Input arguments for the RabbitMQ message."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "send_to_rabbitmq"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "sendToRabbitmqConfig": {
                                                "type": "sendToRabbitmqConfig",
                                                "required": True,
                                                "description": "RabbitMQ message configuration.",
                                                "subcomponents": {
                                                    "connectionRef": {
                                                        "type": "connectionRef",
                                                        "required": True,
                                                        "condition": "!connectionDef",
                                                        "description": "Reference to RabbitMQ connection template."
                                                    },
                                                    "connectionDef": {
                                                        "type": "connectionDef",
                                                        "required": True,
                                                        "condition": "!connectionRef",
                                                        "subcomponents": {
                                                            "userName": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Username for RabbitMQ."
                                                            },
                                                            "userPass": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Password for RabbitMQ."
                                                            },
                                                            "addresses": {
                                                                "type": "Array",
                                                                "required": True,
                                                                "description": "Connection address and port."
                                                            },
                                                            "virtualHost": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Virtual host."
                                                            }
                                                        }
                                                    },
                                                    "exchange": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "Exchange name."
                                                    },
                                                    "routingKey": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "Routing key."
                                                    },
                                                    "message": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "Message body."
                                                    },
                                                    "messageProperties": {
                                                        "type": "JsonObject",
                                                        "required": True,
                                                        "description": "Message properties, e.g., contentType, priority."
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "send_to_kafka": {
                "description": "Sends a message to Kafka.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "send_to_kafka"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "send_to_kafka"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "sendToKafkaConfig": {
                                                "type": "sendToKafkaConfig",
                                                "required": True,
                                                "description": "Kafka message configuration.",
                                                "subcomponents": {
                                                    "connectionRef": {
                                                        "type": "connectionRef",
                                                        "required": True,
                                                        "condition": "!connectionDef",
                                                        "description": "Reference to Kafka connection template."
                                                    },
                                                    "connectionDef": {
                                                        "type": "connectionDef",
                                                        "required": True,
                                                        "condition": "!connectionRef",
                                                        "subcomponents": {
                                                            "bootstrapServers": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Kafka bootstrap servers."
                                                            },
                                                            "authDef": {
                                                                "type": "authDef",
                                                                "required": True,
                                                                "subcomponents": {
                                                                    "type": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "values": ["SASL", "TLS"],
                                                                        "description": "Authorization type."
                                                                    },
                                                                    "sasl": {
                                                                        "type": "sasl",
                                                                        "required": True,
                                                                        "condition": "type == 'SASL'",
                                                                        "subcomponents": {
                                                                            "protocol": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "values": ["SASL_SSL", "SASL_PLAINTEXT"],
                                                                                "description": "SASL protocol."
                                                                            },
                                                                            "mechanism": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "values": ["OAUTHBEARER", "SCRAM-SHA-512"],
                                                                                "description": "SASL mechanism."
                                                                            },
                                                                            "username": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Username."
                                                                            },
                                                                            "password": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Password."
                                                                            },
                                                                            "sslDef": {
                                                                                "type": "sslDef",
                                                                                "required": True,
                                                                                "condition": "mechanism == 'SCRAM-SHA-512'",
                                                                                "subcomponents": {
                                                                                    "trustStoreType": {
                                                                                        "type": "String255",
                                                                                        "required": False,
                                                                                        "description": "Certificate type."
                                                                                    },
                                                                                    "trustStoreCertificates": {
                                                                                        "type": "String",
                                                                                        "required": False,
                                                                                        "description": "Certificate body."
                                                                                    }
                                                                                }
                                                                            },
                                                                            "tokenUrl": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "condition": "mechanism == 'OAUTHBEARER'",
                                                                                "description": "Token URL."
                                                                            }
                                                                        }
                                                                    },
                                                                    "tls": {
                                                                        "type": "tls",
                                                                        "required": True,
                                                                        "condition": "type == 'TLS'",
                                                                        "subcomponents": {
                                                                            "keyStoreCertificates": {
                                                                                "type": "String",
                                                                                "required": True,
                                                                                "description": "Client public key."
                                                                            },
                                                                            "keyStoreKey": {
                                                                                "type": "String",
                                                                                "required": True,
                                                                                "description": "Client private key."
                                                                            },
                                                                            "trustStoreCertificates": {
                                                                                "type": "String",
                                                                                "required": True,
                                                                                "description": "Root certificate."
                                                                            },
                                                                            "trustStoreType": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Certificate type."
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "topic": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "Kafka topic."
                                                    },
                                                    "Key": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "Message key."
                                                    },
                                                    "message": {
                                                        "type": "message",
                                                        "required": True,
                                                        "subcomponents": {
                                                            "payload": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Message body."
                                                            }
                                                        }
                                                    },
                                                    "messageProperties": {
                                                        "type": "JsonObject",
                                                        "required": True,
                                                        "description": "Message properties."
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "send_to_s3": {
                "description": "Sends a file to S3.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "send_to_s3"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": False,
                                "description": "Input arguments for the S3 operation."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "send_to_s3"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "sendToS3Config": {
                                                "type": "sendToS3Config",
                                                "required": True,
                                                "description": "S3 configuration.",
                                                "subcomponents": {
                                                    "connectionRef": {
                                                        "type": "connectionRef",
                                                        "required": True,
                                                        "condition": "!connectionDef",
                                                        "description": "Reference to S3 connection template."
                                                    },
                                                    "connectionDef": {
                                                        "type": "connectionDef",
                                                        "required": True,
                                                        "condition": "!connectionRef",
                                                        "subcomponents": {
                                                            "endpoint": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "S3 endpoint."
                                                            },
                                                            "authDef": {
                                                                "type": "authDef",
                                                                "required": True,
                                                                "subcomponents": {
                                                                    "type": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "value": "accessKey",
                                                                        "description": "Authorization type."
                                                                    },
                                                                    "accessKeyAuth": {
                                                                        "type": "accessKeyAuth",
                                                                        "required": True,
                                                                        "subcomponents": {
                                                                            "accessKey": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Access key."
                                                                            },
                                                                            "secretKey": {
                                                                                "type": "String255",
                                                                                "required": True,
                                                                                "description": "Secret key."
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "bucket": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "S3 bucket name."
                                                    },
                                                    "region": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "description": "S3 region."
                                                    },
                                                    "s3File": {
                                                        "type": "s3File",
                                                        "required": True,
                                                        "subcomponents": {
                                                            "filePath": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "File name and extension."
                                                            },
                                                            "content": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "Variable containing file content."
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "send_to_sap": {
                "description": "Sends an IDoc to SAP.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "send_to_sap"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": True,
                                "description": "Input arguments for the SAP operation."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "send_to_sap"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "sendToSapConfig": {
                                                "type": "sendToSapConfig",
                                                "required": True,
                                                "description": "SAP configuration.",
                                                "subcomponents": {
                                                    "connectionRef": {
                                                        "type": "connectionRef",
                                                        "required": True,
                                                        "condition": "!connectionDef",
                                                        "description": "Reference to SAP connection template."
                                                    },
                                                    "connectionDef": {
                                                        "type": "connectionDef",
                                                        "required": True,
                                                        "condition": "!connectionRef",
                                                        "subcomponents": {
                                                            "props": {
                                                                "type": "props",
                                                                "required": True,
                                                                "subcomponents": {
                                                                    "jco.client.lang": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "description": "Client language."
                                                                    },
                                                                    "jco.client.passwd": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "description": "Password."
                                                                    },
                                                                    "jco.client.user": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "description": "Username."
                                                                    },
                                                                    "jco.client.sysnr": {
                                                                        "type": "Int",
                                                                        "required": True,
                                                                        "description": "SAP system number."
                                                                    },
                                                                    "jco.destination.pool_capacity": {
                                                                        "type": "Int",
                                                                        "required": True,
                                                                        "description": "Max pool connections."
                                                                    },
                                                                    "jco.destination.peak_limit": {
                                                                        "type": "Int",
                                                                        "required": True,
                                                                        "description": "Max simultaneous connections."
                                                                    },
                                                                    "jco.client.client": {
                                                                        "type": "Int",
                                                                        "required": True,
                                                                        "description": "SAP client number."
                                                                    },
                                                                    "jco.client.ashost": {
                                                                        "type": "String255",
                                                                        "required": True,
                                                                        "description": "Host."
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "idoc": {
                                                        "type": "idoc",
                                                        "required": True,
                                                        "subcomponents": {
                                                            "xml": {
                                                                "type": "String255",
                                                                "required": True,
                                                                "description": "XML document body."
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "xslt_transform": {
                "description": "Performs an XSLT transformation.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "xslt_transform"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": True,
                                "description": "Input arguments for the XSLT transformation."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "xslt_transform"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "xsltTransformConfig": {
                                                "type": "xsltTransformConfig",
                                                "required": True,
                                                "description": "XSLT transformation configuration.",
                                                "subcomponents": {
                                                    "xsltTemplateRef": {
                                                        "type": "xsltTemplateRef",
                                                        "required": True,
                                                        "condition": "!xsltTemplate",
                                                        "description": "Reference to XSLT template."
                                                    },
                                                    "xsltTransformTargetRef": {
                                                        "type": "xsltTransformTargetRef",
                                                        "required": True,
                                                        "condition": "!xsltTransformTarget",
                                                        "description": "Reference to document for transformation."
                                                    },
                                                    "xsltTemplate": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "condition": "!xsltTemplateRef",
                                                        "description": "XSLT template."
                                                    },
                                                    "xsltTransformTarget": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "condition": "!xsltTransformTargetRef",
                                                        "description": "Document to transform."
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "transform": {
                "description": "Performs XML to JSON or JSON to XML transformation.",
                "parameters": {
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "transform"
                    },
                    "workflowCall": {
                        "type": "WorkflowCall",
                        "required": True,
                        "subcomponents": {
                            "args": {
                                "type": "JsonObject",
                                "required": True,
                                "description": "Input arguments for the transformation."
                            },
                            "workflowDef": {
                                "type": "SimpleWorkflowDefinition",
                                "required": True,
                                "subcomponents": {
                                    "type": {
                                        "type": "String255",
                                        "required": True,
                                        "value": "transform"
                                    },
                                    "details": {
                                        "type": "Details",
                                        "required": True,
                                        "subcomponents": {
                                            "transformConfig": {
                                                "type": "transformConfig",
                                                "required": True,
                                                "description": "Transformation configuration.",
                                                "subcomponents": {
                                                    "type": {
                                                        "type": "String255",
                                                        "required": True,
                                                        "values": ["xml_to_json", "json_to_xml"],
                                                        "description": "Type of transformation."
                                                    },
                                                    "target": {
                                                        "type": "JsonObject",
                                                        "required": True,
                                                        "description": "Target of transformation."
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "Inject": {
                "description": "Inserts constants, modifies parameters, or sets specific behavior via parameter injections.",
                "parameters": {
                    "id": {
                        "type": "String255",
                        "required": True,
                        "description": "Unique identifier for the activity. Must be unique within a business process."
                    },
                    "description": {
                        "type": "String255",
                        "required": False,
                        "description": "Description of the activity step."
                    },
                    "transition": {
                        "type": "String255",
                        "required": True,
                        "description": "ID of the next activity. Set to null if the process or branch ends."
                    },
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "inject",
                        "description": "Type of activity, set to 'inject'."
                    },
                    "injectData": {
                        "type": "JsonObject",
                        "required": True,
                        "description": "Data to be injected, e.g., constants or transformed variables using Lua."
                    }
                }
            },
            "Switch": {
                "description": "Evaluates conditions and transitions based on the first successful condition or a default transition.",
                "parameters": {
                    "id": {
                        "type": "String255",
                        "required": True,
                        "description": "Unique identifier for the activity. Must be unique within a business process."
                    },
                    "description": {
                        "type": "String255",
                        "required": False,
                        "description": "Description of the activity step."
                    },
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "switch",
                        "description": "Type of activity, set to 'switch'."
                    },
                    "dataConditions": {
                        "type": "Array",
                        "required": True,
                        "description": "List of conditions and their corresponding transitions.",
                        "subcomponents": {
                            "condition": {
                                "type": "String400",
                                "required": True,
                                "description": "Condition script in Lua format."
                            },
                            "conditionDescription": {
                                "type": "String400",
                                "required": False,
                                "description": "Description of the condition."
                            },
                            "transition": {
                                "type": "String400",
                                "required": False,
                                "description": "Activity ID to transition to if condition is True. If empty, the workflow ends."
                            }
                        }
                    },
                    "defaultTransition": {
                        "type": "DefaultDataTransition",
                        "required": True,
                        "description": "Behavior if all conditions are False.",
                        "subcomponents": {
                            "transition": {
                                "type": "String255",
                                "required": True,
                                "description": "Activity ID to transition to if all conditions are False."
                            },
                            "conditionDescription": {
                                "type": "String400",
                                "required": False,
                                "description": "Description of the default condition."
                            }
                        }
                    }
                }
            },
            "Parallel": {
                "description": "Executes multiple activities in parallel with a specified completion type.",
                "parameters": {
                    "id": {
                        "type": "String255",
                        "required": True,
                        "description": "Unique identifier for the activity. Must be unique within a business process."
                    },
                    "description": {
                        "type": "String255",
                        "required": False,
                        "description": "Description of the activity step."
                    },
                    "transition": {
                        "type": "String255",
                        "required": True,
                        "description": "ID of the next activity. Set to null if the process or branch ends."
                    },
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "parallel",
                        "description": "Type of activity, set to 'parallel'."
                    },
                    "branches": {
                        "type": "Array",
                        "required": True,
                        "description": "List of activity IDs to execute in parallel."
                    },
                    "completionType": {
                        "type": "String255",
                        "required": True,
                        "description": "Completion type for parallel activities.",
                        "values": ["anyOf", "allOf"]
                    }
                }
            },
            "Timer": {
                "description": "Triggers a transition to the next activity after a specified duration.",
                "parameters": {
                    "id": {
                        "type": "String255",
                        "required": True,
                        "description": "Unique identifier for the activity. Must be unique within a business process."
                    },
                    "description": {
                        "type": "String255",
                        "required": False,
                        "description": "Description of the activity step."
                    },
                    "transition": {
                        "type": "String255",
                        "required": True,
                        "description": "ID of the next activity. Set to null if the process or branch ends."
                    },
                    "type": {
                        "type": "String255",
                        "required": True,
                        "value": "timer",
                        "description": "Type of activity, set to 'timer'."
                    },
                    "timerDuration": {
                        "type": "String256",
                        "format": "ISO 8601 duration",
                        "required": True,
                        "description": "Duration before transitioning to the next activity."
                    }
                }
            }
        }
    }
}
