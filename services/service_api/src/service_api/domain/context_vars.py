from contextvars import ContextVar

request_id_var = ContextVar('request_id')
client_ip_var = ContextVar('client_ip')
user_agent_var = ContextVar('user_agent')
method_var = ContextVar('method')
path_var = ContextVar('path')
