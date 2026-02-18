class DeliveryServiceError(Exception):
    """Базовое исключение для ошибок бизнес-логики."""


class ParcelNotFoundError(DeliveryServiceError):
    """Посылка не найдена."""


class ParcelTypeNotFoundError(DeliveryServiceError):
    """Тип посылки не найден."""

