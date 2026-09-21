import json

from kafka import KafkaProducer

from app.core.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CHAT_TOPIC,
)
from app.core.logging import get_logger
from app.events.schemas import ChatEvent


logger = get_logger(__name__)


class EventProducer:
    def __init__(self):
        self.enabled = False
        self.producer = None

    def connect(self):
        """
        Connect to Kafka.
        """

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda value: json.dumps(
                    value
                ).encode("utf-8"),
            )

            self.enabled = True

            logger.info("Kafka producer connected")

        except Exception as e:
            self.enabled = False
            self.producer = None

            logger.warning(
                "Kafka unavailable: %s",
                e,
            )

    def publish_chat_event(
        self,
        event: ChatEvent,
    ):
        """
        Publish a chat event to Kafka.
        """

        if (
            not self.enabled
            or self.producer is None
        ):
            logger.warning(
                "Kafka disabled - event not published"
            )
            return False

        try:
            self.producer.send(
                KAFKA_CHAT_TOPIC,
                event.model_dump(
                    mode="json"
                ),
            )

            self.producer.flush()

            logger.info(
                "Kafka event published: %s",
                event.event_id,
            )

            return True

        except Exception as e:
            self.enabled = False

            logger.error(
                "Kafka publish failed: %s",
                e,
            )

            return False


event_producer = EventProducer()