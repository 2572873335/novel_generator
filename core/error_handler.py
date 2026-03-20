class NovelGenerationError(Exception):
    """Base class for exceptions in the novel generation system."""
    pass

class InvalidInputError(NovelGenerationError):
    """Exception raised for invalid input provided to the novel generator."""
    def __init__(self, message='Invalid input provided.'):  
        self.message = message  
        super().__init__(self.message)

class GenerationError(NovelGenerationError):
    """Exception raised when there is an error during novel generation."""
    def __init__(self, message='Error occurred during novel generation.'):  
        self.message = message  
        super().__init__(self.message)

class ResourceNotFoundError(NovelGenerationError):
    """Exception raised when a required resource is not found."""
    def __init__(self, resource_name):  
        self.message = f'Resource {resource_name} not found.'  
        super().__init__(self.message)

# Error handling utility functions

def handle_error(error):
    if isinstance(error, NovelGenerationError):
        print(f'NovelGenerationError occurred: {error}')
    else:
        print(f'An unexpected error occurred: {error}')