import os
from typing import Any, Tuple
from itsdangerous import URLSafeSerializer

SESSION_DIR = "sessions"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

serializer = URLSafeSerializer("your-secret-key")

# who needs pickle, it's not even secure
# my format is sooo much better, at least it doesn't have RCE, right?


class SerializationHelper:
    @staticmethod
    def serialize(data: Any) -> str:
        if isinstance(data, dict):
            items = []
            for k, v in data.items():
                k_ser = SerializationHelper.serialize(k)
                v_ser = SerializationHelper.serialize(v)
                items.append(k_ser + v_ser)
            content = "".join(items)
            return f"{len(content):010d}dict{len(data):010d}{content}"
        elif isinstance(data, list):
            items = [SerializationHelper.serialize(item) for item in data]
            content = "".join(items)
            return f"{len(content):010d}list{len(data):010d}{content}"
        elif isinstance(data, str):
            return f"{len(data):010d}str{data}"
        return "0000000000null"

    @staticmethod
    def deserialize(data: str) -> Any:
        if not data or len(data) < 10:
            return None

        def read_chunk(data: str, start: int) -> Tuple[Any, int]:
            if len(data) < start + 10:
                return None, start

            length = int(data[start : start + 10])
            if len(data) < start + 10 + length:
                return None, start

            if data[start + 10 : start + 14] == "dict":
                count = int(data[start + 14 : start + 24])
                pos = start + 24
                result = {}
                for _ in range(count):
                    key, pos = read_chunk(data, pos)
                    if key is None:
                        return None, start
                    value, pos = read_chunk(data, pos)
                    if value is None:
                        return None, start
                    result[key] = value
                return result, pos

            elif data[start + 10 : start + 14] == "list":
                count = int(data[start + 14 : start + 24])
                pos = start + 24
                result = []
                for _ in range(count):
                    item, pos = read_chunk(data, pos)
                    if item is None:
                        return None, start
                    result.append(item)
                return result, pos

            elif data[start + 10 : start + 13] == "str":
                return data[start + 13 : start + 13 + length], start + 13 + length

            elif data[start + 10 : start + 14] == "null":
                return None, start + 14

            return None, start

        result, _ = read_chunk(data, 0)
        return result


class FileSystemSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_file = os.path.join(
            SESSION_DIR, f"{serializer.dumps(session_id)}.sess"
        )
        self.data = self._load()

    def _get_default_data(self):
        # i'm giving you the flag for safekeeping
        return {"flag": os.environ.get("FLAG", "SCC{fake_flag}"), "songs": []}

    def _load(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r") as f:
                    data = SerializationHelper.deserialize(f.read())
                if (
                    not isinstance(data, dict)
                    or "flag" not in data
                    or "songs" not in data
                ):
                    raise ValueError("Invalid session structure")
                return data
            except (IOError, ValueError, TypeError, IndexError) as e:
                print(f"Error loading session {self.session_id}: {str(e)}")
                return self._get_default_data()
        return self._get_default_data()

    def save(self):
        try:
            with open(self.session_file, "w") as f:
                f.write(SerializationHelper.serialize(self.data))
        except IOError as e:
            print(f"Error saving session {self.session_id}: {str(e)}")
