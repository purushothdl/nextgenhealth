from bson import ObjectId
from typing import Dict, List, Union

def convert_objectids_to_strings(data: Union[Dict, List]) -> Union[Dict, List]:
    """
    Recursively convert all ObjectIds to strings in a dictionary or list.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (dict, list)):
                data[key] = convert_objectids_to_strings(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, ObjectId):
                data[index] = str(item)
            elif isinstance(item, (dict, list)):
                data[index] = convert_objectids_to_strings(item)
    return data