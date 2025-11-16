# app/core/errors.py
class CMCError(Exception):
   pass


class NotFoundError(CMCError):
   pass


class RateLimitError(CMCError):
   pass