import os, io, time, json, random, string, datetime
import pandas as pd
from faker import Faker
from dateutil.relativedelta import relativedelta
from util import put_object_bytes

BRONZE_BUCKET = os.getenv("BRONZE_BUCKET", "bronze")

fake = Faker()
Faker.seed(42)
random.seed(42)

PRODUCTS = [
    (1, "Sneakers AirMax", "Shoes", 119.99),
    (2, "Headphones ZX", "Audio", 79.90),
    (3, "Smartwatch Lite", "Wearables", 149.00),
    (4, "Backpack Pro", "Bags", 59.50),
    (5, "Gaming Mouse", "Peripherals", 39.99),
]

def rand_pct(p): return random.random() < p

def gen_customers(n=50):
    rows = []
    for i in range(n):
        cid = random.randint(1, 10000)
        first = fake.first_name()
        last = fake.last_name()
        email = f"{first.lower()}.{last.lower()}@{fake.free_email_domain()}"
        country = fake.country_code()
        signup = fake.date_between(start_date="-2y", end_date="today")

        # Corruptions
        if rand_pct(0.1): email = ""  # missing email
        if rand_pct(0.05): signup = "32/13/2025"  # invalid date
        rows.append([cid, first, last, email, country, str(signup)])
    return pd.DataFrame(rows, columns=["customer_id","first_name","last_name","email","country","signup_date"])

def gen_orders(n=100):
    rows = []
    now = datetime.datetime.utcnow()
    for i in range(n):
        order_id = random.randint(100000, 999999)
        customer_id = random.randint(1, 10000)
        pid, name, cat, price = random.choice(PRODUCTS)
        qty = random.randint(1, 5)
        unit_price = price
        total = round(qty * unit_price, 2)
        ts = now - relativedelta(minutes=random.randint(0, 1440))
        channel = random.choice(["web","mobile","store"])

        # Corruptions
        if rand_pct(0.05): qty = -1  # invalid qty
        if rand_pct(0.03): unit_price = -abs(unit_price)  # invalid price
        if rand_pct(0.03): total = None  # missing total
        if rand_pct(0.05): ts = "99-99-9999"  # invalid ts
        rows.append([order_id, customer_id, pid, qty, unit_price, total, str(ts), channel])
    df = pd.DataFrame(rows, columns=["order_id","customer_id","product_id","quantity","unit_price","total_amount","order_ts","channel"])
    # Inject duplicates
    if len(df) >= 5:
        dup = df.sample(5, random_state=42)
        df = pd.concat([df, dup], ignore_index=True)
    return df

def gen_clicks(n=80):
    rows = []
    for i in range(n):
        cid = random.randint(1, 10000)
        path = random.choice(["/","/product/1","/product/2","/cart","/checkout"])
        ip = fake.ipv4()
        ts = fake.date_time_between(start_date="-2d", end_date="now").isoformat()
        # Corruptions
        if rand_pct(0.05): ip = "999.999.999.999"
        rows.append({"customer_id": cid, "path": path, "ip": ip, "ts": ts})
    return rows

def upload_batch():
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    # customers CSV
    customers = gen_customers(40)
    csv_bytes = customers.to_csv(index=False).encode("utf-8")
    put_object_bytes(BRONZE_BUCKET, f"customers/customers_{ts}.csv", csv_bytes, "text/csv")

    # orders JSON
    orders = gen_orders(100)
    orders_json = orders.to_dict(orient="records")
    put_object_bytes(BRONZE_BUCKET, f"orders/orders_{ts}.json", json.dumps(orders_json).encode("utf-8"), "application/json")

    # clicks TXT (JSON Lines)
    clicks = gen_clicks(80)
    lines = [json.dumps(x) for x in clicks]
    put_object_bytes(BRONZE_BUCKET, f"clicks/clicks_{ts}.txt", ("\n".join(lines)).encode("utf-8"), "text/plain")

    print(f"[generator] Uploaded batch at {ts}")

def main():
    time.sleep(3)
    while True:
        try:
            upload_batch()
        except Exception as e:
            print(f"[generator] ERROR: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()