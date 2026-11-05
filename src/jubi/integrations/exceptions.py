class JobWriteError(Exception):
    """Raised when a job cant be written"""

    pass


class JobValidationError(Exception):
    """Raised when a job is formatted incorrectly"""

    pass


class NotificationError(Exception):
    """Raise when a notification fails"""


class ResumeUploadError(Exception):
    """Raise when uploading fails"""


class ResumeAccessError(Exception):
    """Raise when access fails"""


class JobDescriptionError(Exception):
    """Raise when no job descript"""
