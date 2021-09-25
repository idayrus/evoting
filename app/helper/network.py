from flask import request
from app import app


def get_real_ip():
    try:
        trusted_proxies = app.config.get('PROXY_LIST')
        route = request.access_route + [request.remote_addr]
        return next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)
    except Exception as e:
        print(e)
        return "127.0.0.1"
