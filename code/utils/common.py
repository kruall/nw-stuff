import threading
import os


class run_and_forget:
    def __init__(self, func):
        self.__func = func

    def __call__(self, *args, **kwargs):
        threading.Thread(target=self.__func, args=args, kwargs=kwargs).start()


class EnvVariables:
    def __init__(self):
        self.bot_key = os.getenv("BOT_KEY")
        self.public_key = os.getenv("PUBLIC_KEY")
        self.api_key = os.getenv("API_KEY")
        self.cloud_id = os.getenv("CLOUD_ID")
        self.folder_id = os.getenv("FOLDER_ID")
        self.ydb_enpoint = os.getenv("YDB_ENDPOINT")
        self.ydb_database = os.getenv("YDB_DATABASE")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.discord_application_id = os.getenv("DISCORD_APPLICATION_ID")


variables = EnvVariables()
