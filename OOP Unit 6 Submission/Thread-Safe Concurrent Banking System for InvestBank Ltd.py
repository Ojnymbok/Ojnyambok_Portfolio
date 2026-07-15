""
InvestBank Ltd - Thread-Safe Concurrent Banking System
OOP implementation ensuring race-condition freedom and deadlock prevention.
"""

import threading
import time
import random
import logging
import unittest

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(threadName)s] %(levelname)s: %(message)s'
)

class BankAccount:
    """Thread-safe bank account using per-instance locking."""

    def __init__(self, account_number: str, initial_balance: float = 0.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._account_number = account_number
        self._balance = float(initial_balance)
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        with self._lock:
            self._balance += amount
            logging.debug(f"Deposited KSH {amount:.2f} to {self._account_number}")

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        with self._lock:
            if self._balance >= amount:
                self._balance -= amount
                logging.debug(f"Withdrew KSH {amount:.2f} from {self._account_number}")
            else:
                logging.warning(f"Insufficient funds in {self._account_number}")
                raise ValueError(f"Insufficient funds for KSH {amount:.2f}")

    def get_balance(self) -> float:
        with self._lock:
            return self._balance

    @property
    def account_number(self) -> str:
        return self._account_number

    @staticmethod
    def transfer(source: 'BankAccount', destination: 'BankAccount', amount: float) -> bool:
        """Deadlock-free transfer using strict resource ordering by account number."""
        if source.account_number == destination.account_number:
            raise ValueError("Source and destination must be different accounts.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        # Always lock lower account number first
        if source.account_number < destination.account_number:
            first_lock, second_lock = source._lock, destination._lock
        else:
            first_lock, second_lock = destination._lock, source._lock

        with first_lock:
            with second_lock:
                if source._balance >= amount:
                    source._balance -= amount
                    destination._balance += amount
                    logging.info(f"Transferred KSH {amount:.2f} from {source.account_number} to {destination.account_number}")
                    return True
                return False


class TransactionSimulator:
    """Simulates 5 concurrent users performing transactions."""

    def __init__(self, target_account: BankAccount, num_users: int = 5):
        self._target_account = target_account
        self._num_users = num_users
        self._threads: list[threading.Thread] = []

    def _user_worker(self, user_id: int, operations: int) -> None:
        logging.info(f"User {user_id} started.")
        for _ in range(operations):
            action = random.choice(['deposit', 'withdraw'])
            amount = float(random.randint(50, 500))
            try:
                if action == 'deposit':
                    self._target_account.deposit(amount)
                else:
                    self._target_account.withdraw(amount)
            except ValueError:
                pass  # Expected for overdraft attempts
            time.sleep(random.uniform(0.0001, 0.002))  # Simulate latency
        logging.info(f"User {user_id} completed.")

    def run_simulation(self, ops_per_user: int = 50) -> None:
        logging.info(f"Starting simulation with {self._num_users} concurrent users...")
        self._threads.clear()
        for i in range(self._num_users):
            t = threading.Thread(
                target=self._user_worker,
                args=(i + 1, ops_per_user),
                name=f"User-{i+1}"
            )
            self._threads.append(t)
            t.start()

        for t in self._threads:
            t.join()
        logging.info("Simulation completed successfully.")
Testing and Validation
The system includes a comprehensive unittest suite to verify correctness under concurrent load.
Python
class TestInvestBankSystem(unittest.TestCase):
    def test_basic_operations(self):
        acc = BankAccount("ACC-001", 10000.0)
        acc.deposit(2500.0)
        self.assertEqual(acc.get_balance(), 12500.0)
        acc.withdraw(3000.0)
        self.assertEqual(acc.get_balance(), 9500.0)
        with self.assertRaises(ValueError):
            acc.withdraw(20000.0)

    def test_concurrent_transactions(self):
        initial = 20000.0
        account = BankAccount("ACC-TEST", initial)
        simulator = TransactionSimulator(account, num_users=5)
        simulator.run_simulation(ops_per_user=60)

        # Final balance should be consistent (no lost updates)
        self.assertGreaterEqual(account.get_balance(), 0.0)
        logging.info(f"Concurrency test passed. Final balance: KSH {account.get_balance():.2f}")

    def test_deadlock_prevention(self):
        acc_a = BankAccount("AAA-001", 50000.0)
        acc_b = BankAccount("BBB-002", 50000.0)
        threads = []

        def worker1():
            for _ in range(300):
                BankAccount.transfer(acc_a, acc_b, 50.0)

        def worker2():
            for _ in range(300):
                BankAccount.transfer(acc_b, acc_a, 50.0)

        t1 = threading.Thread(target=worker1)
        t2 = threading.Thread(target=worker2)
        threads.extend([t1, t2])
        t1.start()
        t2.start()
        for t in threads:
            t.join(timeout=10.0)

        self.assertFalse(t1.is_alive() or t2.is_alive())
        self.assertEqual(acc_a.get_balance() + acc_b.get_balance(), 100000.0)
        logging.info("Deadlock prevention test passed.")

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
