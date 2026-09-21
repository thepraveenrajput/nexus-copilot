import json

from kafka import KafkaConsumer
from sqlalchemy.orm import Session

from app.db.postgres import SessionLocal
from app.models.analytics_event import AnalyticsEvent


from app.core.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CHAT_TOPIC,
    KAFKA_ANALYTICS_GROUP,
)


def create_consumer():
    return KafkaConsumer(
        KAFKA_CHAT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=KAFKA_ANALYTICS_GROUP,
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )


def save_event(
    db: Session,
    event: dict,
):
    event_id = event.get("event_id")

    if not event_id:
        print("⚠️ Event does not contain event_id")
        return

    # Prevent duplicate events
    existing_event = (
        db.query(AnalyticsEvent)
        .filter(
            AnalyticsEvent.event_id == event_id
        )
        .first()
    )

    if existing_event:
        print(
            f"⚠️ Event already exists: {event_id}"
        )
        return

    analytics_event = AnalyticsEvent(
        event_id=event_id,
        event_type=event.get(
            "event_type",
            "UNKNOWN",
        ),
        user_id=event.get("user_id"),
        conversation_id=event.get(
            "conversation_id"
        ),
        route=event.get("route"),
        agent=event.get("agent"),
        success=event.get(
            "success",
            False,
        ),
        duration_ms=event.get("duration_ms"),
    )

    db.add(analytics_event)
    db.commit()

    print(
        f" Analytics event stored: {event_id}"
    )


def consume_events():
    consumer = create_consumer()

    print(
        " NexusCopilot Analytics Consumer started"
    )

    print(
        f"📡 Listening to topic: {KAFKA_TOPIC}"
    )

    db = SessionLocal()

    try:
        for message in consumer:
            event = message.value


            print(" Kafka Event Received")
            
            print(
                json.dumps(
                    event,
                    indent=2,
                )
            )

        
            try:
                save_event(
                    db=db,
                    event=event,
                )

            except Exception as e:
                db.rollback()

                print(
                    f" Failed to store event: {e}"
                )

    except KeyboardInterrupt:
        print(
            "Analytics Consumer stopped"
        )

    finally:
        db.close()
        consumer.close()


if __name__ == "__main__":
    consume_events()