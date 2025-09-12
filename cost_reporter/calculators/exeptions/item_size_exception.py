class ItemSizeException(Exception):
    def __str__(self):
        return f"you will probably try to print a item larger that press_sheet"
