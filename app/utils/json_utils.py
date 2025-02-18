from datetime import datetime, timedelta
import json
from typing import Any

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and timedelta objects."""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            # Convert timedelta to total seconds
            return obj.total_seconds()
        return super().default(obj)

def dumps_with_datetime(obj: Any, **kwargs) -> str:
    """
    Serialize an object to JSON string with proper datetime and timedelta handling.
    
    Args:
        obj: The object to serialize
        **kwargs: Additional arguments passed to json.dumps
    
    Returns:
        str: JSON-formatted string
    """
    return json.dumps(obj, cls=DateTimeEncoder, **kwargs)

def loads_with_datetime(json_str: str) -> Any:
    """
    Deserialize a JSON string, parsing ISO format datetime strings.
    
    Args:
        json_str: JSON string to parse
    
    Returns:
        Any: Deserialized object
    """
    def datetime_parser(dct):
        for k, v in dct.items():
            if isinstance(v, str):
                try:
                    dct[k] = datetime.fromisoformat(v)
                except ValueError:
                    pass
        return dct
    
    return json.loads(json_str, object_hook=datetime_parser)
