import codecs


class UTF8Validator:
    """
    Utility class for validating whether a given file or string is UTF-8 encoded.
    """

    @staticmethod
    def is_valid_utf8_bytes(byte_data: bytes) -> bool:
        """
        Check if the provided bytes are valid UTF-8.

        Args:
            byte_data (bytes): Byte content to validate.

        Returns:
            bool: True if valid UTF-8, False otherwise.
        """
        try:
            byte_data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False

    @staticmethod
    def is_valid_utf8_file(file_path: str) -> bool:
        """
        Check if a file is valid UTF-8 encoded.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file is UTF-8 encoded, False otherwise.
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                return UTF8Validator.is_valid_utf8_bytes(data)
        except (OSError, IOError):
            return False
