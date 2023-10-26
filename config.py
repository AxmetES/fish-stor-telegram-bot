from environs import Env

env = Env()
env.read_env()


class Settings:
    BOT_TOKEN = env('BOT_TOKEN')
    API_TOKEN = env('API_TOKEN', 'da468417cf5793050a3da1ddc65f60272c58642374569e01fadc34585313a1000de49819d449c60ef7cb968148cd98cdaf5f437d63f8bf1bcc8d7c88ea68c6cef442f8f0c549fe706fc97222a7d3ecaba29a3617ed0e1bfd5d291b8e402c6bff47b5ad0155e0b9c5eb1b35e517a7f1529815f48fb22ac4c719c01a564dd6231d')

    DATABASE_PASSWORD = env('DATABASE_PASSWORD')
    DATABASE_HOST = env('DATABASE_HOST')
    DATABASE_PORT = env('DATABASE_PORT')


settings = Settings()
