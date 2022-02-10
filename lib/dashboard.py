from aiohttp import ClientSession
from os import getenv
from datetime import datetime, timedelta

class DashboardClient:
    def __init__(self, loop):
        self.__id = "798825395461160960"
        self.__secret = str(getenv("client_secret"))
        self.baseurl = "https://discord.com/api/v9"
        self.session = ClientSession(loop = loop)

    async def change_code(self, code):
        data = {
            "client_id": self.__id,
            "client_secret": self.__secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://dmsblog.cf/callback"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        async with self.session.post(self.baseurl + "/oauth2/token", data=data, headers=headers) as r:
            data = await r.json()
        now = datetime.now()
        expires = now + timedelta(seconds=data["expires_in"])
        return data["access_token"], expires

    async def fetch_user(self, request):
        token = request.cookies["token"]
        headers = {
            "Authorization": "Bearer " + token
        }
        async with self.session.get(self.baseurl + "/users/@me", headers = headers) as r:
            return await r.json()