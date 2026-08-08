from contextvars import ContextVar

request_id_var = ContextVar('request_id')
message_id_var = ContextVar('message_id')
update_id_var = ContextVar('update_id')
user_id_var = ContextVar('user_id')