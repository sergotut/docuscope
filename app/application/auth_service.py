class AuthService:
    def __init__(self):
        pass

    def get_user(self, tg_id: int):
        # Мок: возвращаем пользователя по tg_id
        return {"id": 1, "tg_id": tg_id}
