from src.database import Database


def main():

    database = Database()

    events = database.get_recent_events(
        limit=20
    )

    print()
    print("======================================")
    print("       TACTICALVISION EVENTS")
    print("======================================")
    print()

    if not events:

        print("No events stored.")

        database.close()

        return

    for event in events:

        print(
            f"[{event['timestamp']}] "
            f"{event['event_type']} | "
            f"ID={event['object_id']} | "
            f"CLASS={event['object_class']} | "
            f"ZONE={event['zone']} | "
            f"CONF={event['confidence']} | "
            f"DIRECTION={event['direction']} | "
            f"SPEED={event['speed']}"
        )

    print()
    print(
        f"Total events: "
        f"{database.count_events()}"
    )

    database.close()


if __name__ == "__main__":
    main()