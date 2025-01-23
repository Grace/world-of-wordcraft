from dataclasses import dataclass
from typing import Any, Dict
import json

@dataclass
class WebSocketMessage:
    type: str
    message: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        return cls(
            type=data.get('type', ''),
            message=data.get('message', '')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        return cls.from_dict(json.loads(json_str))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'message': self.message
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())