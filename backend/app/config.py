from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_hostname: str 
    database_port: str 
    database_name: str 
    database_username: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int
    model_config = SettingsConfigDict(env_file="backend/.env")


settings = Settings()
