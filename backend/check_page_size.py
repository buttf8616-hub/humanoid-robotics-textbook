import httpx
import asyncio

async def check():
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
        pages = [
            'https://humanoid-robotics-textbook-nu.vercel.app/modules/module-3/chapter-1-gazebo-simulation-environments',
            'https://humanoid-robotics-textbook-nu.vercel.app/modules/module-3/chapter-2-unity-robotics-integration',
        ]
        for url in pages:
            r = await c.get(url)
            name = url.split('/')[-1]
            print(f'{name}: {len(r.text)/1024:.0f} KB')

asyncio.run(check())
