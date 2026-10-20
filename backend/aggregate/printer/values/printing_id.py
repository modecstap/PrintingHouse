from backend.aggregate.printer.errors import InvalidIdException


class PrintingID:
    def __init__(self, value: int) -> None:
        """Сохраняет номер записи истории печати.

        Предусловия: value имеет тип int и не меньше 1.
        Результат: объект с полем value.
        Ошибки: InvalidIdException, если тип не int или значение меньше 1.
        """
        if type(value) is not int or value < 1:
            raise InvalidIdException(
                f"создание номера печати: значение {value!r} должно быть целым не меньше 1"
            )
        self.value = value

    def __eq__(self, other: object) -> bool:
        if type(other) is not PrintingID:
            return NotImplemented
        return self.value == other.value
