class HeaderParsingError(Exception):
    """
    Raised when the header of a CSV file cannot be parsed due to incorrect field names or out of range index values.
    """

    pass


class TimestampParsingError(Exception):
    """
    Raised when the timestamp of a CSV file row cannot be parsed.
    """

    pass
