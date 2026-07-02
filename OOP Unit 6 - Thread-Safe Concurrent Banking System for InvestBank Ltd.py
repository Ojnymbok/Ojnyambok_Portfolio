import threading
import time
import random
import logging
import unittest

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(threadName)s] %(levelname)s: %(message)s')

class BankAccount:
    def __init__(self, account_number: str, initial_balance: float = 0.0):
        self._account_number = account_number
        self._balance = float(initial_balance)
        self._lock = threading.Lock()

    def deposit(self, amount: float, channel: str = "Cash") -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        with self._lock:
            self._balance += amount
            logging.info(f"Deposited KSH {amount:.2f} via {channel} to {self._account_number}")

    def withdraw(self, amount: float, channel: str = "Cash") -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        with self._lock:
            if self._balance >= amount:
                self._balance -= amount
                logging.info(f"Withdrew KSH {amount:.2f} via {channel} from {self._account_number}")
            else:
                logging.warning(f"Insufficient funds via {channel} in {self._account_number}")
                raise ValueError(f"Insufficient funds for KSH {amount:.2f}")

    def get_balance(self, channel: str = "Mobile") -> float:
        with self._lock:
            return self._balance

    @property
    def account_number(self) -> str:
        return self._account_number

    @staticmethod
    def transfer(source: 'BankAccount', destination: 'BankAccount', amount: float, channel: str = "EFT"):
        if source.account_number == destination.account_number:
            raise ValueError("Accounts must differ.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if source.account_number < destination.account_number:
            first_lock, second_lock = source._lock, destination._lock
        else:
            first_lock, second_lock = destination._lock, source._lock
        with first_lock:
            with second_lock:
                if source._balance >= amount:
                    source._balance -= amount
                    destination._balance += amount
                    logging.info(f"Transferred KSH {amount:.2f} via {channel}")
                    return True
                return False

class TransactionSimulator:
    def __init__(self, target_account: BankAccount, num_users: int = 5):
        self._target_account = target_account
        self._num_users = num_users
        self._threads: list[threading.Thread] = []

    def _user_worker(self, user_id: int, operations: int, channel: str):
        for _ in range(operations):
            action = random.choice(['deposit', 'withdraw'])
            amount = float(random.randint(50, 500))
            try:
                if action == 'deposit':
                    self._target_account.deposit(amount, channel)
                else:
                    self._target_account.withdraw(amount, channel)
            except ValueError:
                pass
            time.sleep(random.uniform(0.0001, 0.002))

    def run_simulation(self, ops_per_user: int = 50, channel: str = "Cash"):
        self._threads.clear()
        for i in range(self._num_users):
            t = threading.Thread(target=self._user_worker, args=(i + 1, ops_per_user, channel), name=f"{channel}-User-{i+1}")
            self._threads.append(t)
            t.start()
        for t in self._threads:
            t.join()
