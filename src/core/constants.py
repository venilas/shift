UNAUTHORIZED_RESPONSE = {
    "description": "Пользователь не авторизован",
    "content": {
        "application/json": {
            "example": {
                "detail": "Invalid token",
            }
        }
    },
}

NOT_ADMIN_RESPONSE = {
    "description": "Пользователь не является админом",
    "content": {
        "application/json": {
            "example": {
                "detail": "Forbidden",
            }
        }
    },
}

NOT_FOUND_RESPONSES = {
    "room_not_found": {
        "description": "Комната не найдена",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Room not found",
                }
            }
        },
    },
    "booking_not_found": {
        "description": "Бронирование не найдено",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Booking not found",
                }
            }
        },
    },
    "user_not_found": {
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {
                    "detail": "User not found",
                }
            }
        },
    },
    "slot_not_found": {
        "description": "Слот не найден",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Slot not found",
                }
            }
        },
    },
}
