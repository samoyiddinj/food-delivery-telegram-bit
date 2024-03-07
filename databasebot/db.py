import sqlite3
from datetime import datetime


class Database:
    def __init__(self):

        self.connection = sqlite3.connect("delivery.db")
        self.connection.row_factory = sqlite3.Row
        self.cur = self.connection.cursor()

        self.cur.execute("""
            CREATE table if not exists "User" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "chat_id" INTEGER NOT NULL,
                "tg_firstname" TEXT NOT NULL,
                "tg_username" TEXT,
                "lang" INTEGER,
                "phone_number" NUMERIC,
                "fullname" TEXT,
                "joined_date" TEXT
                )
            """)
        self.cur.execute("""
            CREATE table if not exists "Location" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT ,
                "user_id" INTEGER NOT NULL,
                "lat" TEXT,
                "lon" TEXT,
                "name" TEXT
                )
            """)
        self.cur.execute("""
            CREATE table if not exists "Category" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" TEXT NOT NULL,
                "photo" TEXT 
                )
            """)
        self.cur.execute("""
            CREATE table if not exists "Product" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" TEXT,
                "photo" TEXT,
                "price" NUMERIC,
                "is_available" TEXT,
                "description" TEXT,
                "category_id" INTEGER
                )
            """)
        self.cur.execute("""
            CREATE table if not exists "Bucket" (
                "id" INTEGER NOT  NULL PRIMARY KEY AUTOINCREMENT,
                "user_id" INTEGER
                 )
            """)
        self.cur.execute("""
            CREATE table if not exists "BucketItem" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "bucket_id" INTEGER,
                "product_id" INTEGER,
                "count" INTEGER NOT NULL
                )
            """)
        self.cur.execute("""
            CREATE table if not exists "Order" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "user_id" INTEGER NOT NULL,
                "location_id" INTEGER NOT NULL,
                "price" INTEGER
                )
            """)
        self.cur.execute("""
            CREATE table if not exists "OrderItem" (
                "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                "order_id" INTEGER,
                "product_id" INTEGER NOT NULL,
                "count" INTEGER
                )        
        """)
        self.cur.execute("""
                    CREATE table if not exists "UserLog" (
                        "user_id" INTEGER NOT  NULL,
                        "log" TEXT
                         )
                    """)
        self.connection.commit()

    def get_user(self, chat_id):
        user = self.cur.execute(f"""
            select * from user 
            where chat_id = {chat_id}        
        """).fetchone()
        if user:
            return user
        else:
            return None

    def add_user(self, **kwargs):
        if kwargs.get("chat_id") and kwargs.get("tg_firstname"):
            self.cur.execute("""
                insert into user (chat_id, tg_firstname, tg_username, joined_date)
                values("%d", "%s", "%s", "%s")
            """ % (kwargs.get("chat_id"), kwargs.get("tg_firstname"), kwargs.get("tg_username"), str(datetime.now())))
            self.connection.commit()
        if kwargs.get("lang"):
            self.cur.execute(f"""
                update User set lang={kwargs.get("lang")}
                where chat_id={kwargs.get("chat_id")}
            """)
            self.connection.commit()

        if kwargs.get("fullname"):
            self.cur.execute(f"""
                            update User set fullname="{kwargs.get("fullname")}"
                            where chat_id={kwargs.get("chat_id")}
                        """)
            self.connection.commit()

        if kwargs.get("phone_number"):
            self.cur.execute(f"""
                            update User set phone_number="{kwargs.get("phone_number")}"
                            where chat_id={kwargs.get("chat_id")}
                        """)
            self.connection.commit()

    def add_log(self, user_id, **kwargs):
        log = self.cur.execute(f"""
        select * from UserLog
        where user_id = {user_id}
        """).fetchone()
        if log:
            self.cur.execute(f"""
                    update UserLog set log={kwargs["log"]}
                    where user_id = {user_id}
                """)
        else:
            self.cur.execute("""
            insert into UserLog 
            values(?, ?)           
            """, [user_id, kwargs["log"]])
        self.connection.commit()

    def get_log(self, user_id):
        stage = self.cur.execute("""
            select log from  UserLog
            where user_id = ?
        """, [user_id]).fetchone()
        return stage

    def get_category(self):
        categories = self.cur.execute("""
                select * from Category
                order by id asc   
        """).fetchall()
        return categories

    def get_products(self, category_id):
        products = self.cur.execute(f"""
                select Product.*, Category.name  as category_name, Category.photo as category_photo
                 from Product
                inner join Category on Product.category_id=Category.id
                where category_id = {category_id} and Product.is_available = 1
        """).fetchall()

        return products

    def get_category_id(self, product_id):
        category_id = self.cur.execute(f"""
            select * from Product
            where Product.id={product_id}
        """).fetchone()
        return category_id

    def get_details(self, product_id):
        detail = self.cur.execute(f"""
            select * from Product 
            where Product.id={product_id}  and Product.is_available=1

        """).fetchone()
        return detail

    def get_bucket(self, user_id):
        user_bucket = self.cur.execute(f"""
                select Bucket.id as id 
                from Bucket
                inner join User on User.id = Bucket.user_id
                where User.id = {user_id}
        """).fetchone()
        return user_bucket

    def add_basket(self, user_id):
        user_bucket = self.cur.execute(f"""
            select * from Bucket
            where user_id = {user_id}
            """).fetchone()
        if not user_bucket:
            self.cur.execute(f"""
                insert into  Bucket (user_id)
                values (%d)
            """ % user_id)
        self.connection.commit()
        return 'done'

    def clear_bucket(self, bucket_id):
        self.cur.execute(f'''
            delete from BucketItem
            where bucket_id = {bucket_id}
        ''')
        self.connection.commit()

    def add_item(self, bucket_id, product_id, count):
        one_item = self.cur.execute(f"""
                select * from BucketItem
                where bucket_id = {bucket_id} and product_id = {product_id}
        """).fetchone()
        if one_item:
            item_count = int(one_item['count']) + count
            self.cur.execute(f"""
                    update BucketItem set count = {item_count}
                    where bucket_id = {bucket_id} and product_id = {product_id}
                    """)

        else:

            self.cur.execute(f"""
                insert into BucketItem (bucket_id, product_id, count)
                values (?, ?, ?)     
            """, (bucket_id, product_id, count))
        self.connection.commit()

    def get_item(self, bucket_id):
        items = self.cur.execute(f"""
            select BucketItem.*, Bucket.user_id, Product.name as product_name, Product.price 
            from BucketItem
            inner join Bucket on BucketItem.bucket_id = Bucket.id
            inner join Product  on  Product.id = BucketItem.product_id            
            where BucketItem.bucket_id = {bucket_id}
        """).fetchall()
        return items

    def update_item(self, item_id, count):
        self.cur.execute(f"""
            update BucketItem set count = {count}
            where id = {item_id}
        """)
        self.connection.commit()

    def clear_item(self, item_id):
        self.cur.execute(f"""
            delete from BucketItem
            where id = {item_id}
        """)
        self.connection.commit()

    def add_order(self, user_id, price, date):
        self.cur.execute(f"""
            insert into user_order (user_id, price, order_date)
            values ({user_id}, {price}, "{date}")
        """)
        self.connection.commit()
        order_id = self.cur.execute(f"""
            select user_id from user_order
            where user_id = {user_id} and order_date = "{date}"
        """).fetchone()
        return order_id

    def add_order_item(self, order_id, product_id, count):
        self.cur.execute(f"""
            insert into OrderItem (order_id,product_id,count)
            values({order_id},{product_id},{count})
        """)
        self.connection.commit()

    def get_orders(self, user_id):
        orders = self.cur.execute(f"""
            select * 
            from user_order
            where user_order.user_id = {user_id}.
        """).fetchall()
        return orders

    def get_order_item(self, order_id):
        order_items = self.cur.execute(f"""
            select OrderItem.* , Product.name as product_name, Product.price as price
            from OrderItem 
            inner join Product on OrderItem.product_id = Oroduct.id
            where order_id = {order_id}
        """).fetchall()
        return order_items
