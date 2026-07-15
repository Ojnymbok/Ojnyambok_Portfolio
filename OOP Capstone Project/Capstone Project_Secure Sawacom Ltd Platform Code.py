import datetime
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

# ==========================================
# 1. CUSTOM EXCEPTION HIERARCHY (Security & Robustness)
# ==========================================
class SawacomSecurityException(Exception):
    """Base exception class for all Sawacom security and protocol violations."""
    pass

class InvalidIdentityException(SawacomSecurityException):
    """Raised when government document details fail format validation or IPRS verification."""
    pass

class TransactionFrozenException(SawacomSecurityException):
    """Raised when a bank or digital credit provider attempts an operation during a cool-down window."""
    pass

class LineLockedException(SawacomSecurityException):
    """Raised when a restricted operation is performed on a remote-locked line."""
    pass


# ==========================================
# 2. CORE ENTIRE / DATA MODELS (Encapsulation)
# ==========================================
class SubscriberProfile:
    """
    Encapsulates all sensitive state attributes of an MNO subscriber line.
    Enforces strict invariant validation through Python properties.
    """
    def __init__(self, phone_number: str, national_id: str, full_name: str):
        self.phone_number = self._validate_regex(phone_number, r"^254\d{9}$", "Invalid Kenyan phone number format.")
        self.national_id = self._validate_regex(national_id, r"^\d{7,8}$", "Invalid Kenyan National ID format.")
        self.full_name = full_name.strip()
        
        self._last_sim_swap_timestamp: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=10)
        self._is_remote_locked: bool = False
        self._transaction_history: List[float] = []

    @staticmethod
    def _validate_regex(value: str, pattern: str, error_msg: str) -> str:
        if not re.match(pattern, value):
            raise InvalidIdentityException(error_msg)
        return value

    @property
    def last_sim_swap_timestamp(self) -> datetime.datetime:
        return self._last_sim_swap_timestamp

    @last_sim_swap_timestamp.setter
    def last_sim_swap_timestamp(self, timestamp: datetime.datetime):
        if timestamp > datetime.datetime.now():
            raise ValueError("SIM swap timestamp cannot be set in the future.")
        self._last_sim_swap_timestamp = timestamp

    @property
    def is_remote_locked(self) -> bool:
        return self._is_remote_locked

    def set_remote_lock(self, status: bool):
        self._is_remote_locked = status

    def record_transaction(self, amount: float):
        if amount <= 0:
            raise ValueError("Transaction value must be positive.")
        self._transaction_history.append(amount)

    def get_average_transaction(self) -> float:
        if not self._transaction_history:
            return 0.0
        # Analyze up to the last 10 transactions to check velocity spikes
        recent = self._transaction_history[-10:]
        return sum(recent) / len(recent)


# ==========================================
# 3. INTERFACES & DESIGN PATTERNS (Abstraction & Extensibility)
# ==========================================
class IRegistrationObserver(ABC):
    """Abstract Interface acting as the Observer component for system registration events."""
    @abstractmethod
    def on_sim_replacement_triggered(self, subscriber: SubscriberProfile, channel: str):
        pass


class NationalIdentityService(ABC):
    """Abstract Interface for Government Verification infrastructure (AI/Extensibility Ready)."""
    @abstractmethod
    def verify_with_iprs(self, national_id: str, expected_name: str) -> bool:
        pass


# ==========================================
# 4. CONCRETE CONTEXT IMPLEMENTATIONS
# ==========================================
class MockIPRSDatabase(NationalIdentityService):
    """Concrete implementation mimicking the Kenya Integrated Population Registration Services."""
    def __init__(self):
        # Seed realistic national registry records
        self._registry: Dict[str, str] = {
            "12345678": "John Doe",
            "87654321": "Jane Kiprop",
            "11223344": "David Omwamba"
        }

    def verify_with_iprs(self, national_id: str, expected_name: str) -> bool:
        if national_id not in self._registry:
            return False
        return self._registry[national_id].lower() == expected_name.lower()


class SecurityAlertNotificationEngine(IRegistrationObserver):
    """Concrete Observer handling multi-channel notification dispatches upon suspicious operations."""
    def on_sim_replacement_triggered(self, subscriber: SubscriberProfile, channel: str):
        print(f"\n[ALERT - SECURITY ENGAGED]: Mandatory multi-channel authentication dispatched to primary user context for line {subscriber.phone_number}.")
        print(f"-> Reason: Secondary SIM Registration attempt detected via channel '{channel}' while USSD Remote Lock is Active.")


# ==========================================
# 5. CORE SYSTEM SUBSYSTEM (Sawacom Platform Engine)
# ==========================================
class SawacomMNOEngine:
    """
    Main system platform combining identity verifications, subscriber status,
    and handling compliance logic for the 4 core cybersecurity use cases.
    """
    def __init__(self, identity_service: NationalIdentityService):
        self.identity_service = identity_service
        self._subscribers: Dict[str, SubscriberProfile] = {}
        self._observers: List[IRegistrationObserver] = []

    def register_observer(self, observer: IRegistrationObserver):
        self._observers.append(observer)

    def add_subscriber_profile(self, subscriber: SubscriberProfile):
        self._subscribers[subscriber.phone_number] = subscriber

    def get_subscriber(self, phone_number: str) -> Optional[SubscriberProfile]:
        return self._subscribers.get(phone_number)

    # Use Case 1 & 2: SIM Swap Reset & Physical Layer Verification with IPRS
    def execute_sim_swap(self, phone_number: str, national_id: str, customer_name: str, presented_doc_type: str) -> bool:
        subscriber = self.get_subscriber(phone_number)
        if not subscriber:
            raise SawacomSecurityException("Subscriber record not discovered within MNO database.")

        # Enforce physical documentation logic check
        if presented_doc_type.upper() not in ["ID", "PASSPORT"]:
            raise InvalidIdentityException("Access denied. Invalid legal physical document type presented.")

        # Query the Government Core Identity Layer (IPRS Interconnect)
        is_valid_citizen = self.identity_service.verify_with_iprs(national_id, customer_name)
        if not is_valid_citizen:
            raise InvalidIdentityException("IPRS Verification Failed. Unauthorized proxy registration or agent collusion flag raised.")

        # Check if user has active USSD lock established
        if subscriber.is_remote_locked:
            for observer in self._observers:
                observer.on_sim_replacement_triggered(subscriber, "Physical Branch Representative Terminal")
            raise LineLockedException("SIM Swap rejected automatically. Active Remote Lock requires physical multi-tier authentication.")

        # If clean, activate the 72-hour Cool-down state marker
        subscriber.last_sim_swap_timestamp = datetime.datetime.now()
        print(f"[SUCCESS]: SIM Swap executed successfully for {phone_number}. 72-Hour mandatory cooling-down period initiated.")
        return True

    # Use Case 3: Gateway Aggregator Verification API for External Banks / Credit Platforms
    def verify_transaction_safety(self, phone_number: str, proposed_amount: float) -> Tuple[bool, str]:
        subscriber = self.get_subscriber(phone_number)
        if not subscriber:
            return False, "Subscriber account non-existent."

        # Rule A: Enforce the 72-Hour System Freeze Window
        time_elapsed = datetime.datetime.now() - subscriber.last_sim_swap_timestamp
        if time_elapsed < datetime.timedelta(hours=72):
            raise TransactionFrozenException(f"Transaction denied. Line under active 72-hour swap cool-down. Time since swap: {time_elapsed}.")

        # Rule B: Velocity Anomaly Check (High-Value transaction indicator: > 10x historical average)
        historical_average = subscriber.get_average_transaction()
        if historical_average > 0.0 and proposed_amount > (10 * historical_average):
            return False, f"Flagged High-Risk Velocity: Amount requested ({proposed_amount}) exceeds 10x average payload ({historical_average})."

        return True, "Transaction Authorized."

    # Use Case 4: Remote USSD Whitelisting Interface (*100*100#)
    def process_ussd_lock_toggle(self, phone_number: str, ussd_string: str) -> str:
        if ussd_string != "*100*100#":
            return "USSD Code Malformed or Unknown."
        
        subscriber = self.get_subscriber(phone_number)
        if not subscriber:
            return "Authentication Error: Subscriber profile unlinked."

        # Invert lock condition state dynamically
        current_status = subscriber.is_remote_locked
        subscriber.set_remote_lock(not current_status)
        new_status_msg = "ACTIVE (Whitelisted against unauthorized remote swaps)" if not current_status else "DISABLED"
        
        return f"Sawacom SecureLine status for {phone_number} is now: {new_status_msg}."


# ==========================================
# 6. PIPELINE VERIFICATION AND SIMULATION SCENARIOS
# ==========================================
def run_academic_test_suite():
    print("="*60)
    print("          SAWACOM CYBERSECURITY CAPSTONE ENGINE RUN")
    print("="*60)

    # Instantiate Infrastructure Components
    iprs_subsystem = MockIPRSDatabase()
    sawacom_mno = SawacomMNOEngine(iprs_subsystem)
    alert_notifier = SecurityAlertNotificationEngine()
    
    # Register Design Pattern Observers
    sawacom_mno.register_observer(alert_notifier)

    # Establish Baseline Seed Subscribers
    john_profile = SubscriberProfile("254711223344", "12345678", "John Doe")
    # Simulate prior steady-state clean transactions for John
    for amt in [1000, 1200, 950, 1100]:
        john_profile.record_transaction(amt)
        
    sawacom_mno.add_subscriber_profile(john_profile)

    # -------------------------------------------------------------
    # TEST SCENARIO A: Fraudulent IPRS Mismatch Prevention (Use Case 1 & 2)
    # -------------------------------------------------------------
    print("\n--- [TEST SCENARIO A]: Attacking with Fraudulent Identity Proxy ---")
    try:
        sawacom_mno.execute_sim_swap("254711223344", "12345678", "Malicious Agent Name", "ID")
    except InvalidIdentityException as e:
        print(f"[EXPECTED EXCEPTION SEEN]: {e}")

    # -------------------------------------------------------------
    # TEST SCENARIO B: Valid Physical Identity Cross-Match and Cool-down Induction
    # -------------------------------------------------------------
    print("\n--- [TEST SCENARIO B]: Valid SIM Swap Overriding Identity Verifications ---")
    sawacom_mno.execute_sim_swap("254711223344", "12345678", "John Doe", "ID")

    # -------------------------------------------------------------
    # TEST SCENARIO C: Bank Querying API During Active 72h Cool-down Window (Use Case 3)
    # -------------------------------------------------------------
    print("\n--- [TEST SCENARIO C]: Bank API Transaction Request Intercept ---")
    try:
        sawacom_mno.verify_transaction_safety("254711223344", 1500)
    except TransactionFrozenException as e:
        print(f"[EXPECTED EXCEPTION SEEN - TRANSACTION BLOCKED]: {e}")

    # -------------------------------------------------------------
    # TEST SCENARIO D: Resetting Timeline to Simulate Cool-down Expiration & Velocity Attacks
    # -------------------------------------------------------------
    print("\n--- [TEST SCENARIO D]: Cool-down Elapsed with Velocity Spike Detection ---")
    # Bypass time for testing purposes: shift last swap back by 5 days (120 hours)
    john_profile.last_sim_swap_timestamp = datetime.datetime.now() - datetime.timedelta(days=5)
    
    # Check normal transaction approval
    is_safe, msg = sawacom_mno.verify_transaction_safety("254711223344", 1100)
    print(f"Normal Value Tx (KES 1100) Status: {msg} (Authorized: {is_safe})")
    
    # Trigger High-Value Velocity Fraud (> 10x average of ~KES 1062.50)
    is_safe, msg = sawacom_mno.verify_transaction_safety("254711223344", 25000)
    print(f"High-Value Anomaly Tx (KES 25000) Status: {msg} (Authorized: {is_safe})")

    # -------------------------------------------------------------
    # TEST SCENARIO E: USSD Whitelisting & Secondary Intercept System (Use Case 4)
    # -------------------------------------------------------------
    print("\n--- [TEST SCENARIO E]: USSD Core Whitelisting & Locked Swap Attestation ---")
    # User engages lock code
    ussd_reply = sawacom_mno.process_ussd_lock_toggle("254711223344", "*100*100#")
    print(f"USSD Menu Execution Output: {ussd_reply}")
    
    # Attacker tries physical swap on whitelisted line
    print("\nAttempting illegal swap on remote-locked profile...")
    try:
        sawacom_mno.execute_sim_swap("254711223344", "12345678", "John Doe", "ID")
    except LineLockedException as e:
        print(f"[EXPECTED EXCEPTION SEEN - ATTACK DEFUSED]: {e}")

    print("\n" + "="*60)
    print("          SAWACOM SECURITY ENGINE TEST CONCLUDED")
    print("="*60)


if __name__ == "__main__":
    run_academic_test_suite()
