from typing import Any
from datetime import datetime

from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.websocket_api import connect
from solana.rpc.responses import SignatureNotification
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

from fastapi.exceptions import HTTPException

from database import db
from schemas import CreateUser
import config


class CRUDUser:

    def __init__(self):
        self.__solana_client = None
        self.__closed = True

    async def _run_client(self) -> None:
        if self.__closed:
            self.__solana_client = AsyncClient(config.SOLANA_API_URL)
            self.__closed = False

    def _to_sol(self, x: int or float) -> int:
        return int(x * 10 ** 9)

    def _from_sol(self, x: int or float) -> int or float:
        return x / 10 ** 9

    async def create_user(self, obj_in: CreateUser) -> dict:
        await self._run_client()
        kp = Keypair.generate()
        user_data = obj_in.dict()
        user_data["public_key"] = str(kp.public_key)
        user_data["secret_key"] = kp.secret_key
        user_data["id"] = await db.fetch_value(
            "INSERT INTO users (username, public_key, secret_key) "
            "VALUES ($1, $2, $3) RETURNING id;", *user_data.values()
        )
        return user_data

    async def get_user(self, user_id: int) -> dict:
        await self._run_client()
        user = await db.fetch_row(
            "SELECT id, username, public_key "
            "FROM users WHERE id = $1;", user_id
        )
        if not user:
            raise HTTPException(status_code=404)
        return user

    async def _get_user_secret_key(self, user_id: int) -> Any:
        return await db.fetch_value(
            "SELECT secret_key "
            "FROM users WHERE id = $1;", user_id
        )

    async def get_balance(self, user_id: int) -> dict:
        await self._run_client()
        user = await self.get_user(user_id)
        resp = await self.__solana_client.get_balance(user["public_key"])
        balance = self._from_sol(resp["result"]["value"])
        return {
            **user,
            "balance": balance,
        }

    async def send_sol(self, sender_id: int, receiver_id: int, amount: int or float) -> dict:
        await self._run_client()
        sender_secret = await self._get_user_secret_key(sender_id)
        receiver_secret = await self._get_user_secret_key(receiver_id)
        if not (sender_secret and receiver_secret):
            raise HTTPException(status_code=404)
        sender = Keypair.from_secret_key(sender_secret)
        receiver = Keypair.from_secret_key(receiver_secret)
        txn = Transaction().add(transfer(TransferParams(
            from_pubkey=sender.public_key, to_pubkey=receiver.public_key, lamports=self._to_sol(amount))))
        resp = await self.__solana_client.send_transaction(txn, sender)
        transaction_sig = resp["result"]
        transaction_data = {
            "transaction_sig": transaction_sig,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "amount": amount
        }
        transaction = await self.create_transaction(transaction_data)
        return transaction

    async def create_transaction(self, obj_in: dict) -> dict:
        obj_in["id"] = await db.fetch_value(
            "INSERT INTO transactions (transaction_sig, sender_id, receiver_id, amount) "
            "VALUES ($1, $2, $3, $4) RETURNING id;",
            *obj_in.values()
        )
        return obj_in

    async def update_transaction(self, transaction_sig: str) -> None:
        async with connect(config.SOLANA_WEBSOCKET_URL) as websocket:
            await websocket.signature_subscribe(transaction_sig, commitment="finalized")
            async for msg in websocket:
                if type(msg) == SignatureNotification:
                    break
        transaction_data = await self.__solana_client.get_transaction(transaction_sig)
        update_data = [
            datetime.fromtimestamp(transaction_data["result"]["blockTime"]),
            self._from_sol(transaction_data["result"]["meta"]["fee"]),
            list(transaction_data["result"]["meta"]["status"].keys())[0]
        ]
        await db.execute(
            "UPDATE transactions SET blocktime = $1, fee = $2, status = $3",
            *update_data
        )


crud_user = CRUDUser()
