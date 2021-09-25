
class ReverseProxied(object):
    def __init__(self, app, config):
        self.app = app
        self.config = config

    def __call__(self, environ, start_response):
        # if one of x_forwarded or preferred_url is https, prefer it.
        forwarded_scheme = environ.get("HTTP_X_FORWARDED_PROTO", None)
        preferred_scheme = self.config.get("PREFERRED_URL_SCHEME", None)
        if "https" in [forwarded_scheme, preferred_scheme] and not self.config.get("DEV_MODE"):
            environ["wsgi.url_scheme"] = "https"
        return self.app(environ, start_response)
