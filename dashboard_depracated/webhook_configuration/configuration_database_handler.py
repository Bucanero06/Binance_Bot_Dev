import json

import redis


class AssetConfigurationDatabaseHandler:
    def __init__(self, configuration_group_name, redis_host, redis_port, redis_db, decode_responses=True):
        self.configuration_group_name = configuration_group_name
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.decode_responses = decode_responses

        # r.hset('h', 'field', 'value')
        # print(r.hget('h', 'field'))
        # # print lenth of hash h
        # print(r.hlen('h'))

    def set_configuration(self, key, value):
        r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db,
                              decode_responses=self.decode_responses)

        if isinstance(value, dict):
            value = json.dumps(value)


        return r.hset(self.configuration_group_name, key, value)

    def get_configuration(self, key):
        r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db,
                              decode_responses=self.decode_responses)
        return r.hget(self.configuration_group_name, key)

    def get_all_configurations(self):
        r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db,
                              decode_responses=self.decode_responses)
        return r.hgetall(self.configuration_group_name)

    def delete_configuration(self, key):
        r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db,
                              decode_responses=self.decode_responses)
        return r.hdel(self.configuration_group_name, key)

    def delete_all_configurations(self):
        r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db,
                              decode_responses=self.decode_responses)
        return r.delete(self.configuration_group_name)

    def get_configuration_count(self):
        r = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db,
                              decode_responses=self.decode_responses)
        return r.hlen(self.configuration_group_name)

# class Configuration_Json_Database_Handler:  # todo hotfix until we set up a redis database
#     def __init__(self, configuration_file_name):
#         self.configurations = {}
#         self.json_name = configuration_file_name
#         self.file_name = self.json_name + '.json'
#         self.reload_configurations_from_file()
#
#     def reload_configurations_from_file(self):
#         import os
#         if os.path.isfile(self.file_name):
#             import json
#             with open(self.file_name, 'r') as f:
#                 self.configurations = json.load(f)
#
#     def get_configuration(self, key):
#         return self.configurations[key]
#
#     def set_configuration(self, key, value):
#         self.configurations[key] = value
#
#     def get_all_configuration_keys(self):
#         return self.configurations.keys()
#
#     def delete_configuration(self, key):
#         self.configurations.pop(key)
#         return self.configurations
#
#     def delete_all_configurations(self):
#         self.configurations = {}
#
#     def get_configuration_count(self):
#         return len(self.configurations)
#
#     def save_configurations_to_file(self):
#         import json
#         with open(self.file_name, 'w') as f:
#             json.dump(self.configurations, f)
