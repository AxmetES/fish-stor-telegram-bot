from environs import Env

env = Env()
env.read_env()


class Settings:
    BOT_TOKEN = env('BOT_TOKEN')
    API_TOKEN = env('API_TOKEN')
    MAIN_URL = env('MAIN_URL')


settings = Settings()