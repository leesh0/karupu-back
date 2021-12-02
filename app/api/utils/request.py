from aiohttp import ClientSession


async def request(url, mode="json"):
    async with ClientSession() as session:
        async with session.get(url) as resp:
            return await getattr(resp, mode)()


async def get_google_profile(access_token: str):
    return await request(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}')
