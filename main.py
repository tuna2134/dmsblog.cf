from sanic import Sanic
from lib.dashboard import DashboardClient
from sanic.exceptions import SanicException
from sanic.response import html, redirect, json, file
from functools import partial
from jinja2 import Environment, FileSystemLoader
from lib.db import aiodatabase
from os import getenv
import random, string

app = Sanic("main")
password = getenv("passwd")
env = Environment(
    loader=FileSystemLoader("./"),
    enable_async=True
)

@app.listener("before_server_start")
async def start(_, loop):
    global client
    client = DashboardClient(loop)
    async with aiodatabase("main.db") as c:
        await c.create_table("blog", {"id": "BIGINT", "title": "TEXT", "content": "TEXT"})
        # await c.insert_data("blog", {"id": "123456", "title": "test", "content": "This is test content"})

async def arun(func, *args):
    loop = app.loop
    return await loop.run_in_executor(None, partial(func, *args))

async def template(filename, *args, **kwargs):
    content = await env.get_template(filename).render_async(kwargs)
    return await arun(html, content)

def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

@app.on_request
async def filter(request):
    if request.host != "dmsblog.cf":
        raise SanicException("dmsblog.cfからアクセスしてください", 400)

@app.route("/")
async def m(request):
    return await arun(redirect, "/index.html")

@app.get("/callback")
async def callback(request):
    code = request.args.get("code")
    token, expires = await client.change_code(code)
    res = redirect("/dashboard.html")
    res.cookies["token"] = token
    res.cookies["token"]["expires"] = expires
    return res

@app.get("/api/dashboard")
async def dashboard(request):
    d = await client.fetch_user(request)
    if d.get("id"):
        return json(d)
    else:
        return json({"status": 404})

@app.get("/api/blog")
async def blog(request):
    if not request.args.get("id"):
        async with aiodatabase("main.db") as c:
            data = await c.get_datas("blog")
        return await arun(json, data)
    else:
        id = request.args["id"][0]
        async with aiodatabase("main.db") as c:
            data = await c.get_data("blog", {"id": id})
        if data is None:
            return json({"message": "error"})
        else:
            return json(data)

@app.post("/api/blog")
async def blog_create(request):
    data = request.json
    if data["password"] != password:
        return await arun(json, {"message": "password is not true"})
    id = await arun(randomname, 6)
    payload = {
        "id": id,
        "title": data["title"],
        "content": data["content"]
    }
    async with aiodatabase("main.db") as c:
        await c.insert_data("blog", payload)
    return await arun(json, {"id": id})

@app.route("/<path:path>")
async def main(request, path):
    if path.endswith(".html"):
        return await template(path)
    else:
        return await file(path)

app.run("0.0.0.0", 8080)