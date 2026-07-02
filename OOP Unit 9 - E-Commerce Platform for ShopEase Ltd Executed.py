Python 3.14.5 (tags/v3.14.5:5607950, May 10 2026, 10:43:50) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> 
= RESTART: C:/Essex MSC/Programming/Python Files/OOP Unit 9 - E-Commerce Platform for ShopEase Ltd.py
==================================================
    SHOPEASE E-COMMERCE PLATFORM SYSTEM START     
==================================================

--- 1. Testing Registration Guardrails ---
Registration Failed: User ID must be a valid email address.
Registration Failed: Password must be at least 8 characters long and contain mixed characters.
User sharon@gmail.com (Shopper) registered successfully.
User supplier_beauty@co.ke (Supplier) registered successfully.

--- 2. Testing Authentication ---
User sharon@gmail.com authenticated successfully.

--- 3. Simulation of Shopping Basket & Checkout Processes ---

--- Processing Order ORD-001 for sharon@gmail.com ---
Total Amount: KES 4,300.00
Sending STK Push to +254712345678 for KES 4,300.00 via M-Pesa...
M-Pesa Transaction confirmed successfully.
[DAL] Transaction TX-20260630221149 securely saved to database.
[NOTIFICATION][EMAIL] Order ORD-001 successfully processed via MpesaPayment. Total: KES 4,300.00
[NOTIFICATION][SMS] Order ORD-001 successfully processed via MpesaPayment. Total: KES 4,300.00

--- Processing Order ORD-002 for sharon@gmail.com ---
Total Amount: KES 1,200.00
Processing Debit card ****-****-****-9010 for KES 1,200.00...
[DAL] Transaction TX-20260630221149 securely saved to database.
[NOTIFICATION][EMAIL] Order ORD-002 successfully processed via CardPayment. Total: KES 1,200.00
[NOTIFICATION][SMS] Order ORD-002 successfully processed via CardPayment. Total: KES 1,200.00

--- Processing Order ORD-003 for sharon@gmail.com ---
Total Amount: KES 2,500.00
Validating shopping voucher 'EASTER-GLOW-2026' for KES 2,500.00...
[DAL] Transaction TX-20260630221149 securely saved to database.
[NOTIFICATION][EMAIL] Order ORD-003 successfully processed via VoucherPayment. Total: KES 2,500.00
[NOTIFICATION][SMS] Order ORD-003 successfully processed via VoucherPayment. Total: KES 2,500.00
