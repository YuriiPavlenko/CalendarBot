import logging
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Convert time to ISO8601 with UTC
        ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        
        log_record = {
            "time": ts,
            "level": record.levelname,
            "message": record.getMessage(),
            "extra": {}
        }

        # If `extra` fields were provided to logger methods, they appear in record.__dict__
        # Convention: extra fields are anything not in standard LogRecord attributes
        reserved = set(["name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                        "created", "msecs", "relativeCreated", "thread", "threadName",
                        "processName", "process"])
        extras = {k:v for k,v in record.__dict__.items() if k not in reserved}
        if extras:
            log_record["extra"] = extras

        return json.dumps(log_record)
