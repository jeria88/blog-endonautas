from django.apps import AppConfig


class TokensConfig(AppConfig):
    name = 'tokens'

    def ready(self):
        import tokens.signals  # noqa: F401
