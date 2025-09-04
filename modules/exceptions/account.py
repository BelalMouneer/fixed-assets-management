from .general_exceptions import ResourceNotFoundException

class AccountException(Exception):
  status_code = 400

  def __init__(self, message, status_code=None):
    super().__init__(message)
    if status_code is not None:
      self.status_code = status_code

class AccountExistsException(AccountException):
  def __init__(self, message="Account already exists"):
    super().__init__(message, status_code=409)

class ParentNotFoundException(AccountException, ResourceNotFoundException):
  def __init__(self, message="Parent account not found"):
    super().__init__(message, status_code=404)

class AccountNotFoundException(AccountException, ResourceNotFoundException):
  def __init__(self, message="Account not found"):
    super().__init__(message, status_code=404)

class AccountCannotBeDeletedException(AccountException):
  def __init__(self, message="Account can't be deleted"):
    super().__init__(message, status_code=403)
