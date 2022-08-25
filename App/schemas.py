from pydantic import BaseModel
from pydantic.types import constr, condecimal


class GetUser(BaseModel):
    id: int
    username: constr(min_length=2, max_length=32)
    public_key: constr(max_length=64)


class GetUserBalance(GetUser):
    balance: condecimal(decimal_places=9)


class CreateUser(BaseModel):
    username: constr(min_length=2, max_length=32)


class GetTransaction(BaseModel):
    id: int
    transaction_sig: constr(max_length=128)
    sender_id: int
    receiver_id: int
