from fastapi import FastAPI, Query
import pymysql
import os
import requests
import uuid
import random

app = FastAPI(title="网上购物商城API")

# 数据库utf8mb4编码配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PWD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4"
}
OLLAMA_URL = os.getenv("OLLAMA_API_URL")

def get_db_conn():
    return pymysql.connect(**DB_CONFIG, autocommit=False)

# ========== 用户登录注册模块 ==========
@app.get("/api/user/register")
def register_user(username: str = Query(""), password: str = Query(""), email: str = Query("")):
    if not username or not password:
        return {"msg":"用户名和密码不能为空"}
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT user_id FROM `user` WHERE username=%s",(username,))
    if cur.fetchone():
        cur.close()
        db.close()
        return {"msg":"用户名已被占用"}
    cur.execute("INSERT INTO `user`(username,password_hash,email) VALUES(%s,%s,%s)",(username,password,email))
    db.commit()
    cur.close()
    db.close()
    return {"msg":"注册成功，请登录"}

@app.get("/api/user/login")
def login_user(username: str = Query(""), password: str = Query("")):
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT user_id,username FROM `user` WHERE username=%s AND password_hash=%s",(username,password))
    res = cur.fetchone()
    cur.close()
    db.close()
    if res:
        return {"msg":"登录成功","user_id":res[0],"username":res[1]}
    else:
        return {"msg":"用户名或密码错误"}

# ========== 商品接口 ==========
@app.get("/api/goods")
def get_all_goods():
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT * FROM goods")
    rows = cur.fetchall()
    cols = [col[0] for col in cur.description]
    res_list = [dict(zip(cols, row)) for row in rows]
    cur.close()
    db.close()
    return {"goods_list": res_list}

@app.get("/api/goods/search")
def search_goods(keyword: str = Query("")):
    db = get_db_conn()
    cur = db.cursor()
    sql = "SELECT * FROM goods WHERE goods_name LIKE %s OR category LIKE %s"
    cur.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
    rows = cur.fetchall()
    cols = [col[0] for col in cur.description]
    res_list = [dict(zip(cols, row)) for row in rows]
    cur.close()
    db.close()
    return {"goods_list": res_list}

@app.get("/api/goods/random")
def get_random_goods(num: int = Query(8)):
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT * FROM goods")
    rows = cur.fetchall()
    cols = [col[0] for col in cur.description]
    all_goods = [dict(zip(cols, row)) for row in rows]
    cur.close()
    db.close()
    pick_num = min(num, len(all_goods))
    random_list = random.sample(all_goods, pick_num)
    return {"goods_list": random_list}

# ========== AI导购 ==========
@app.get("/api/ai/recommend")
def ai_shop_recommend(prompt: str = Query("推荐高性价比商品")):
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT goods_name,category FROM goods")
    goods_data = cur.fetchall()
    cur.close()
    db.close()
    goods_text = "\n".join([f"{name}（分类：{cate}）" for name,cate in goods_data])

    req_payload = {
        "model": "qwen3:0.6b",
        "prompt": f"只能推荐下面本店真实商品，禁止编造商品：\n{goods_text}\n用户需求：{prompt}，简短精准回答",
        "stream": False
    }
    resp = requests.post(f"{OLLAMA_URL}/api/generate", json=req_payload)
    return {"ai回复": resp.json()["response"]}

# ========== 购物车 ==========
@app.get("/api/cart/add")
def add_cart(user_id:int, goods_id:int, buy_num:int=Query(1)):
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT cart_id,buy_num FROM cart WHERE user_id=%s AND goods_id=%s",(user_id,goods_id))
    exist = cur.fetchone()
    if exist:
        new_num = exist[1] + buy_num
        cur.execute("UPDATE cart SET buy_num=%s WHERE cart_id=%s",(new_num,exist[0]))
    else:
        cur.execute("INSERT INTO cart(user_id,goods_id,buy_num) VALUES(%s,%s,%s)",(user_id,goods_id,buy_num))
    db.commit()
    cur.close()
    db.close()
    return {"msg":"加入购物车成功"}

@app.get("/api/cart/list")
def list_cart(user_id:int):
    db = get_db_conn()
    cur = db.cursor()
    sql = """
    SELECT c.cart_id,c.buy_num,g.goods_id,g.goods_name,g.price,g.stock,g.category
    FROM cart c LEFT JOIN goods g ON c.goods_id=g.goods_id
    WHERE c.user_id=%s
    """
    cur.execute(sql,(user_id,))
    rows = cur.fetchall()
    cols = [col[0] for col in cur.description]
    cart_list = [dict(zip(cols, row)) for row in rows]
    cur.close()
    db.close()
    return {"cart_list":cart_list}

@app.get("/api/cart/del")
def del_cart(user_id:int, cart_id:int):
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("DELETE FROM cart WHERE cart_id=%s AND user_id=%s",(cart_id,user_id))
    db.commit()
    cur.close()
    db.close()
    return {"msg":"删除成功"}

# ========== 订单结算（uuid4生成36位订单号，匹配VARCHAR(36)） ==========
@app.get("/api/order/checkout")
def checkout_order(user_id:int):
    db = get_db_conn()
    cur = db.cursor()
    try:
        sql_cart = """
        SELECT c.goods_id,c.buy_num,g.price,g.stock,g.goods_name
        FROM cart c LEFT JOIN goods g ON c.goods_id=g.goods_id
        WHERE c.user_id=%s
        """
        cur.execute(sql_cart,(user_id,))
        cart_items = cur.fetchall()
        if not cart_items:
            return {"msg":"购物车为空，无法结算"}

        total_price = 0
        order_id = str(uuid.uuid4()) # 标准36位UUID订单号
        cur.execute("INSERT INTO orders(order_id,user_id,total_amount,status) VALUES(%s,%s,%s,0)",(order_id,user_id,0))

        for goods_id,buy_num,price,stock,name in cart_items:
            if stock < buy_num:
                raise Exception(f"商品【{name}】库存不足，仅剩{stock}件")
            item_total = price * buy_num
            total_price += item_total
            cur.execute("INSERT INTO order_item(order_id,goods_id,num,single_price) VALUES(%s,%s,%s,%s)",
                        (order_id,goods_id,buy_num,price))
            cur.execute("UPDATE goods SET stock=stock-%s WHERE goods_id=%s",(buy_num,goods_id))

        cur.execute("UPDATE orders SET total_amount=%s WHERE order_id=%s",(total_price,order_id))
        cur.execute("DELETE FROM cart WHERE user_id=%s",(user_id,))

        db.commit()
        return {"msg":"下单成功","order_id":order_id,"total_price":round(total_price,2)}

    except Exception as e:
        db.rollback()
        return {"msg":str(e)}
    finally:
        cur.close()
        db.close()

# ========== 查询订单 ==========
@app.get("/api/order/list")
def list_order(user_id:int):
    db = get_db_conn()
    cur = db.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY create_time DESC",(user_id,))
    order_rows = cur.fetchall()
    cols_order = [col[0] for col in cur.description]
    order_list = [dict(zip(cols_order, row)) for row in order_rows]

    for order in order_list:
        oid = order["order_id"]
        sql_item = """
        SELECT oi.num,oi.single_price,g.goods_name
        FROM order_item oi LEFT JOIN goods g ON oi.goods_id=g.goods_id
        WHERE oi.order_id=%s
        """
        cur.execute(sql_item,(oid,))
        item_rows = cur.fetchall()
        cols_item = [col[0] for col in cur.description]
        order["items"] = [dict(zip(cols_item, row)) for row in item_rows]

    cur.close()
    db.close()
    return {"order_list":order_list}