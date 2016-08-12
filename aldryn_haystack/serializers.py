# AWS Credentials for the site's ES IAM user
from elasticsearch import serializer, compat, exceptions
import json


class AldrynJSONSerializer(serializer.JSONSerializer):
    """Customised ElasticSearch JSON Serialiser
    Forces correct handling of non-ASCII payloads when
    transmitting data to ElasticSearch via the secure AWS connector.
    To use, assign an instance to the `serializer` kwarg of the
    Haystack connection settings
    """
    def dumps(self, data):
        if isinstance(data, compat.string_types):
            return data
        try:
            return json.dumps(data, default=self.default, ensure_ascii=True)
        except (ValueError, TypeError) as e:
            raise exceptions.SerializationError(data, e)

