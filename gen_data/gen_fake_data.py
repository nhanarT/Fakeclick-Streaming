import argparse
import random
import json
from datetime import datetime
from uuid import uuid4

import psycopg
from confluent_kafka import Producer
from faker import Faker

fake = Faker()
USER_MAP = dict()
PRODUCT_MAP = dict()

def random_user_agent():
    return fake.user_agent()

def random_ip():
    return fake.ipv4()

def gen_user_data(num_user_records):
    for id in range(num_user_records):
        USER_MAP[id] = {'user_agent': random_user_agent(), 'ip': random_ip()}
        conn = psycopg.connect('dbname=postgres user=postgres password=postgres host=postgres')
        with conn.cursor() as curr:
            curr.execute("""
                            INSERT INTO commerce.users
                            (id, username, password) VALUES (%s, %s, %s)
                         """, (id, fake.user_name(), fake.password())
                         )
            conn.commit()

            # 10% probability of update user info
            if random.randint(1, 100)>=90:
                curr.execute(
                        "UPDATE commerce.users SET username = %s WHERE id = %s",
                        (fake.user_name(), id)
                        )
            conn.commit()
    return

def mock_gen_user(num_user_records):
    for id in range(num_user_records):
        print('Create user', id)
        USER_MAP[id] = {'user_agent': random_user_agent(), 'ip': random_ip()}

def gen_product_data(num_products):
    for id in range(num_products):
        name = fake.word()
        price = fake.random_int(min=1, max=100)
        PRODUCT_MAP[id] = {'name':name, 'price':price}
        conn = psycopg.connect('dbname=postgres user=postgres password=postgres host=postgres')
        with conn.cursor() as curr:
            curr.execute("""
                            INSERT INTO commerce.products
                            (id, name, description, price) VALUES (%s, %s, %s, %s)
                         """, (id, name, fake.text(), price)
                         )
            conn.commit()

            # 10% probability of update user info
            if random.randint(1, 100)>=90:
                new_name = fake.word()
                PRODUCT_MAP[id]['name'] = new_name
                curr.execute(
                        "UPDATE commerce.products SET name = %s WHERE id = %s",
                        (new_name, id)
                        )
            conn.commit()
    return

def mock_gen_product(num_products):
    for id in range(num_products):
        print('Create product', id)
        name = fake.word()
        price = fake.random_int(min=1, max=100)
        PRODUCT_MAP[id] = {'name':name, 'price':price}
            
def gen_click_event(user_id, product_id):
    click_id = str(uuid4())
    url = fake.uri()
    product = PRODUCT_MAP[product_id]['name']
    price = PRODUCT_MAP[product_id]['price']
    user_agent = USER_MAP[user_id]['user_agent']
    ip_address = USER_MAP[user_id]['ip']
    datetime_occured = datetime.now()

    click_event = {
            'click_id': click_id,
            'user_id': user_id,
            'product_id': product_id,
            'product': product,
            'price': price,
            'url': url,
            'user_agent': user_agent,
            'ip_address': ip_address,
            'datetime_occured': datetime_occured.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            }

    return click_event

def gen_checkout_event(user_id, product_id):
    payment_method = fake.credit_card_provider()
    total_amount = fake.pyfloat(left_digits=3, right_digits=2, positive=True)
    shipping_address = fake.address()
    billing_address = fake.address()
    user_agent = USER_MAP[user_id]['user_agent']
    ip_address = USER_MAP[user_id]['ip'] 
    datetime_occured = datetime.now()

    checkout_event = {
            'checkout_id': str(uuid4()),
            'user_id': user_id,
            'product_id': product_id,
            'payment_method': payment_method,
            'total_amount': total_amount,
            'shipping_address': shipping_address,
            'billing_address': billing_address,
            'user_agent': user_agent,
            'ip_address': ip_address,
            'datetime_occured': datetime_occured.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            }
    return checkout_event

def push_to_kafka(producer, event, topic):
    producer.produce(topic, json.dumps(event).encode('utf-8'))
    producer.flush()

def mock_kafka(event, topic):
    print('Event:', event)
    print('Topic:', topic)

def gen_clickstream_data(num_users, num_products, num_clicks):
    producer = Producer({'bootstrap.servers': 'kafka:9092'})
    for _ in range(num_clicks):
        user_id = random.randint(0, num_users-1)
        product_id = random.randint(0, num_products-1) 
        click_event = gen_click_event(user_id, product_id)
        push_to_kafka(producer, click_event, 'clicks')

        # 50% probability of checkout
        while random.randint(1, 100) >= 50:
            click_event = gen_click_event(user_id, click_event['product_id'])
            push_to_kafka(producer, click_event, 'clicks')

            checkout_event = gen_checkout_event(click_event['user_id'], click_event['product_id'])
            push_to_kafka(producer, checkout_event, 'checkouts')

def mock_gen_clickstream(num_users, num_products, num_clicks):
    for _ in range(num_clicks):
        user_id = random.randint(0, num_users-1)
        product_id = random.randint(0, num_products-1) 
        click_event = gen_click_event(user_id, product_id)
        mock_kafka(click_event, 'clicks')

        while random.randint(1, 100) >= 50:
            click_event = gen_click_event(user_id, click_event['product_id'])
            mock_kafka(click_event, 'clicks')

            mock_kafka(gen_checkout_event(click_event['user_id'], click_event['product_id']), 'checkouts')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num_user_records', type=int, default=100)
    parser.add_argument('-p', '--num_products', type=int, default=100)
    parser.add_argument('-c', '--num_clicks', type=int, default=10_000_000)

    args = parser.parse_args()
    gen_user_data(args.num_user_records)
    gen_product_data(args.num_products)
    gen_clickstream_data(args.num_user_records, args.num_products, args.num_clicks)
    # mock_gen_user(args.num_user_records)
    # mock_gen_product(args.num_products)
    # mock_gen_clickstream(args.num_user_records, args.num_products, args.num_clicks)

if __name__ == "__main__":
    main()
