from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "mysecretkey"
    mysql_user: str = Field(default="root")
    mysql_password: str = Field(default="password")
    mysql_host: str = Field(default="mysql-db")
    mysql_port: str = Field(default="3306")
    mysql_name: str = Field(default="mysql_db")
    ASYNC_DATABASE_URL: str = ""

    class Config:
        env_file = ".env"

    @model_validator(mode='after')
    def db_url(self):
        self.ASYNC_DATABASE_URL = (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_name}"
        )
        return self

settings = Settings()