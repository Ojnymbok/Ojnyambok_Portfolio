Python 3.14.5 (tags/v3.14.5:5607950, May 10 2026, 10:43:50) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> 
= RESTART: C:/Essex MSC/Programming/Python Files/Capstone Project_Sawacom Ltd Cybersecurity Platform.py
============================================================
          SAWACOM CYBERSECURITY CAPSTONE ENGINE RUN
============================================================

--- [TEST SCENARIO A]: Attacking with Fraudulent Identity Proxy ---
[EXPECTED EXCEPTION SEEN]: IPRS Verification Failed. Unauthorized proxy registration or agent collusion flag raised.

--- [TEST SCENARIO B]: Valid SIM Swap Overriding Identity Verifications ---
[SUCCESS]: SIM Swap executed successfully for 254711223344. 72-Hour mandatory cooling-down period initiated.

--- [TEST SCENARIO C]: Bank API Transaction Request Intercept ---
[EXPECTED EXCEPTION SEEN - TRANSACTION BLOCKED]: Transaction denied. Line under active 72-hour swap cool-down. Time since swap: 0:00:00.005502.

--- [TEST SCENARIO D]: Cool-down Elapsed with Velocity Spike Detection ---
Normal Value Tx (KES 1100) Status: Transaction Authorized. (Authorized: True)
High-Value Anomaly Tx (KES 25000) Status: Flagged High-Risk Velocity: Amount requested (25000) exceeds 10x average payload (1062.5). (Authorized: False)

--- [TEST SCENARIO E]: USSD Core Whitelisting & Locked Swap Attestation ---
USSD Menu Execution Output: Sawacom SecureLine status for 254711223344 is now: ACTIVE (Whitelisted against unauthorized remote swaps).

Attempting illegal swap on remote-locked profile...

[ALERT - SECURITY ENGAGED]: Mandatory multi-channel authentication dispatched to primary user context for line 254711223344.
-> Reason: Secondary SIM Registration attempt detected via channel 'Physical Branch Representative Terminal' while USSD Remote Lock is Active.
[EXPECTED EXCEPTION SEEN - ATTACK DEFUSED]: SIM Swap rejected automatically. Active Remote Lock requires physical multi-tier authentication.

============================================================
          SAWACOM SECURITY ENGINE TEST CONCLUDED
============================================================
