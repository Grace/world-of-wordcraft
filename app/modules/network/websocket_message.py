from typing import Any, Dict, Optional
import json

class WebSocketMessage:
    def __init__(self, type: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.type = type
        self.message = message
        self.data = data if data else {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        return cls(
            type=data.get('type', ''),
            message=data.get('message', ''),
            data=data.get('data', {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        return cls.from_dict(json.loads(json_str))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'message': self.message,
            'data': self.data
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())