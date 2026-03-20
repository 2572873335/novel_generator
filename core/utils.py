# Utility Functions for File Operations, Validation Checks, and Common Helpers

def read_file(file_path):
    """Read the contents of a file and return it as a string."""
    with open(file_path, 'r') as file:
        return file.read()


def write_file(file_path, content):
    """Write the provided content to a file."""
    with open(file_path, 'w') as file:
        file.write(content)


def validate_filename(filename):
    """Check if the filename is valid according to specific system rules."""
    import re
    return bool(re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', filename))  # Example: valid filenames with extensions


def format_error_message(error):
    """Format error messages for consistency."""
    return f'Error: {str(error)}'


def is_empty(value):
    """Check if the given value is empty."""
    return not bool(value)


# Additional common helper functions can be added below
def example_helper():
    pass  # Placeholder for an additional helper function
