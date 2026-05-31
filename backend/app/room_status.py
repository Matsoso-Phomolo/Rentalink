from app.models import RoomStatus


VACANT_ROOM_STATUSES = {
    RoomStatus.vacant,
    RoomStatus.available,
}


OCCUPIED_ROOM_STATUSES = {
    RoomStatus.occupied,
    RoomStatus.partially_occupied,
    RoomStatus.full,
}


def is_vacant_room_status(status: RoomStatus | None) -> bool:
    return status in VACANT_ROOM_STATUSES


def is_occupied_room_status(status: RoomStatus | None) -> bool:
    return status in OCCUPIED_ROOM_STATUSES
