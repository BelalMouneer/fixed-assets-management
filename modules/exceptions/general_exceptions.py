class ResourceNotFoundException(Exception):
  status_code = 404

  def __init__(self, message = 'Resource Not Found Exception', status_code=None):
    super().__init__(message)
    if status_code is not None:
      self.status_code = status_code