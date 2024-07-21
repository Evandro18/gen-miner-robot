import hashlib
from typing import Any

class HashString:
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self._generate_folder_name_hash(*args, **kwds)
    
    def _generate_folder_name_hash(self, text: str) -> str:
        hash = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16) % (10 ** 8)
        return f'{hash}'