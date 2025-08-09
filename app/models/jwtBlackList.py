from sqlmodel import SQLModel, Field 

class JwtBlackList(SQLModel, table=True): 
    __tablename__ = "jwt_blacklist" 

    id: int = Field(default=None, primary_key=True)
    token: str = Field(default=None)
