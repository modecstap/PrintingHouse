from backend.storage.exceptions.service_exception import ServiceException


class NotFoundException(ServiceException):
    def __init__(self, item_id: int, message: str = None):
        self.message = message
        self.item_id = item_id

    def __str__(self):
        print('calling str')
        if self.message:
            return f"NotFoundException, {self.message}"
        else:
            return f'NotFoundException, item with id {self.item_id} not found'
