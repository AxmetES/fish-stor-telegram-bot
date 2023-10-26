from environs import Env

env = Env()
env.read_env()


class Settings:
    BOT_TOKEN = env('BOT_TOKEN')
    API_TOKEN = env('API_TOKEN')

    DATABASE_PASSWORD = env('DATABASE_PASSWORD')
    DATABASE_HOST = env('DATABASE_HOST')
    DATABASE_PORT = env('DATABASE_PORT')


settings = Settings()
