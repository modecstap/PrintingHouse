from backend.aggregate.printer.errors import InvalidIdException


class PrinterID:
    def __init__(self, value: int) -> None:
        """Сохраняет номер принтера.

        Предусловия: value имеет тип int и не меньше 1.
        Результат: объект с полем value.
        Ошибки: InvalidIdException, если тип не int или значение меньше 1.
        """
        if type(value) is not int or value < 1:
            raise InvalidIdException(
                f"создание номера принтера: значение {value!r} должно быть целым не меньше 1"
            )
        self.value = value

    def __eq__(self, other: object) -> bool:
        if type(other) is not PrinterID:
            return NotImplemented
        return self.value == other.value
