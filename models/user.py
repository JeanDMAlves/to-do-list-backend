from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """
        Classe base que levará os atributos básicos de um usuário
    """
    name: str
    email: EmailStr
    password: str
    register_date: Optional[datetime] = Field(default_factory=datetime.today)

class UserPartialUpdate(BaseModel):
    """
        Classe utilizada para que apenas uma parte da informação seja atualizada
        Métodos: 
            - Patch, 
            - Put
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
class UserCreate(UserBase):
    """
        Classe utilizada para criar uma nova de usuários no banco de dados
        Métodos: 
            - Get
    """
    pass

class UserDB(UserBase):
    """
        Classe utilizada para o que realmente é salvo no banco de dados
    """
    id: int

class UserBasic(BaseModel):
    """
        Classe utilizada pra excluir usuários
    """
    email: EmailStr
    password: str
    
class UserAuthentication(BaseModel):
    id: int
    email: EmailStr