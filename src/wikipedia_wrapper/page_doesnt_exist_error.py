
class PageDoesntExistError(Exception):
    """
    Exception for the case that the page doesn't exist
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor of the PageDoesntExistError class
        :param args:
        :param kwargs:
        """
        super().__init__(*args, *kwargs)
