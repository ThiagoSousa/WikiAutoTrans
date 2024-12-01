
class WikiNotAvailableError(Exception):
    """
    Exception for the case the wiki is not available or doesn't exist
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor of the WikiNotAvailableError class
        :param args:
        :param kwargs:
        """
        super().__init__(*args, *kwargs)
