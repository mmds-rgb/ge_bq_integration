import os
import random
from datetime import datetime, timedelta
from google.cloud import bigquery

def create_mock_data():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "primary-394719")
    client = bigquery.Client(project=project_id)
    
    dataset_id = f"{project_id}.financial_services_mock"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {client.project}.{dataset.dataset_id}")
    except Exception as e:
        print(f"Dataset might exist: {e}")
        dataset = client.get_dataset(dataset_id)

    # 1. Create Customers Table
    schema_customers = [
        bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("last_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("join_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("risk_profile", "STRING", mode="NULLABLE", description="Low, Medium, High"),
    ]
    table_customers_id = f"{dataset_id}.customers"
    table_customers = bigquery.Table(table_customers_id, schema=schema_customers)
    try:
        table_customers = client.create_table(table_customers)
        print(f"Created table {table_customers.table_id}")
    except Exception as e:
        print(f"Table customers might exist: {e}")
        table_customers = client.get_table(table_customers_id)

    # 2. Create Accounts Table
    schema_accounts = [
        bigquery.SchemaField("account_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("account_type", "STRING", mode="REQUIRED", description="Checking, Savings, Credit, Investment"),
        bigquery.SchemaField("balance", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("open_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED", description="Active, Closed, Suspended"),
    ]
    table_accounts_id = f"{dataset_id}.accounts"
    table_accounts = bigquery.Table(table_accounts_id, schema=schema_accounts)
    try:
        table_accounts = client.create_table(table_accounts)
        print(f"Created table {table_accounts.table_id}")
    except Exception as e:
        print(f"Table accounts might exist: {e}")
        table_accounts = client.get_table(table_accounts_id)

    # 3. Create Transactions Table
    schema_transactions = [
        bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("account_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("transaction_date", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("amount", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("transaction_type", "STRING", mode="REQUIRED", description="Deposit, Withdrawal, Transfer, Payment"),
        bigquery.SchemaField("merchant_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED", description="Completed, Pending, Failed"),
    ]
    table_transactions_id = f"{dataset_id}.transactions"
    table_transactions = bigquery.Table(table_transactions_id, schema=schema_transactions)
    try:
        table_transactions = client.create_table(table_transactions)
        print(f"Created table {table_transactions.table_id}")
    except Exception as e:
        print(f"Table transactions might exist: {e}")
        table_transactions = client.get_table(table_transactions_id)

    print("Generating mock data...")
    
    # Generate Mock Data
    customers_to_insert = []
    accounts_to_insert = []
    transactions_to_insert = []
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    merchants = ["Amazon", "Walmart", "Target", "Starbucks", "Uber", "Netflix", "Whole Foods", "Shell", "Home Depot", "Apple"]
    categories = ["Groceries", "Entertainment", "Transport", "Shopping", "Utilities", "Dining", "Health", "Travel"]
    
    for i in range(1, 51): # 50 customers
        customer_id = f"CUST{i:04d}"
        join_date = (datetime.now() - timedelta(days=random.randint(100, 2000))).date()
        customers_to_insert.append({
            "customer_id": customer_id,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
            "email": f"customer{i}@example.com",
            "phone": f"555-{random.randint(1000, 9999)}",
            "address": f"{random.randint(100, 999)} Main St, City, State",
            "join_date": join_date.isoformat(),
            "risk_profile": random.choice(["Low", "Medium", "High"])
        })
        
        # 1-3 accounts per customer
        num_accounts = random.randint(1, 3)
        for j in range(num_accounts):
            account_id = f"ACC{i:04d}{j:02d}"
            account_type = random.choice(["Checking", "Savings", "Credit", "Investment"])
            balance = round(random.uniform(100.0, 50000.0), 2)
            if account_type == "Credit":
                balance = -round(random.uniform(0.0, 5000.0), 2)
            
            accounts_to_insert.append({
                "account_id": account_id,
                "customer_id": customer_id,
                "account_type": account_type,
                "balance": balance,
                "open_date": (join_date + timedelta(days=random.randint(0, 30))).isoformat(),
                "status": random.choice(["Active", "Active", "Active", "Closed"])
            })
            
            # 5-20 transactions per account
            num_transactions = random.randint(5, 20)
            for k in range(num_transactions):
                transaction_id = f"TXN{account_id}{k:03d}"
                tx_type = random.choice(["Deposit", "Withdrawal", "Transfer", "Payment"])
                amount = round(random.uniform(5.0, 1000.0), 2)
                if tx_type in ["Withdrawal", "Payment"]:
                    amount = -amount
                    
                transactions_to_insert.append({
                    "transaction_id": transaction_id,
                    "account_id": account_id,
                    "transaction_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                    "amount": amount,
                    "transaction_type": tx_type,
                    "merchant_name": random.choice(merchants) if tx_type in ["Withdrawal", "Payment"] else None,
                    "category": random.choice(categories) if tx_type in ["Withdrawal", "Payment"] else "Income/Transfer",
                    "status": "Completed"
                })

    print(f"Inserting {len(customers_to_insert)} customers...")
    errors = client.insert_rows_json(table_customers_id, customers_to_insert)
    if errors: print(f"Errors inserting customers: {errors}")
    
    print(f"Inserting {len(accounts_to_insert)} accounts...")
    errors = client.insert_rows_json(table_accounts_id, accounts_to_insert)
    if errors: print(f"Errors inserting accounts: {errors}")
    
    print(f"Inserting {len(transactions_to_insert)} transactions...")
    # Batch insert transactions to avoid payload size limits if too large
    batch_size = 500
    for i in range(0, len(transactions_to_insert), batch_size):
        batch = transactions_to_insert[i:i+batch_size]
        errors = client.insert_rows_json(table_transactions_id, batch)
        if errors: print(f"Errors inserting transactions batch: {errors}")
        
    print("Mock data creation complete!")

if __name__ == "__main__":
    create_mock_data()
