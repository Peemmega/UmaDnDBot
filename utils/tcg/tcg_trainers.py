from .tcg_cards import get_cards_by_type


TRAINERS = get_cards_by_type("Trainer")


def get_trainer(trainer_id: str) -> dict | None:
    return TRAINERS.get(trainer_id)


def list_trainers() -> list[dict]:
    return list(TRAINERS.values())