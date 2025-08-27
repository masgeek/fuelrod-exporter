from typing import Type, TypeVar, Dict, Any, Tuple, Optional
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def parse_model(model_class: Type[T], data: Dict[str, Any]) -> Tuple[Optional[T], Optional[Dict[str, Any]]]:
    """
    Validate incoming payload against a Pydantic model.
    Returns (model, None) if valid, or (None, error_dict) if invalid.
    """
    try:
        return model_class(**data), None
    except ValidationError as e:
        return None, {
            "success": False,
            "errors": [
                {
                    "field": ".".join(str(x) for x in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
                for err in e.errors()
            ],
        }
