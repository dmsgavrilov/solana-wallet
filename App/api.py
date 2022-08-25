from fastapi import APIRouter, BackgroundTasks, HTTPException

from wallet import crud_user
from schemas import GetUser, CreateUser, GetUserBalance, GetTransaction

router = APIRouter()


@router.get("/users/{item_id}", response_model=GetUser)
async def get_user(item_id: int):
    user = await crud_user.get_user(item_id)
    return user


@router.post("/users", response_model=GetUser)
async def create_user(obj_in: CreateUser):
    user = await crud_user.create_user(obj_in)
    return user


@router.get("/users/{item_id}/balance", response_model=GetUserBalance)
async def get_balance(item_id: int):
    user = await crud_user.get_balance(item_id)
    return user


@router.get("/users/{item_id}/send", response_model=GetTransaction)
async def send_sol(item_id: int, receiver_id: int, amount: float or int, background_tasks: BackgroundTasks):
    if amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be greater than 0")
    transaction = await crud_user.send_sol(item_id, receiver_id, amount)
    background_tasks.add_task(crud_user.update_transaction, transaction["transaction_sig"])
    return transaction
