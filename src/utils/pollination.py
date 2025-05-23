import aiohttp
import asyncio
import urllib.parse

params = {
    "model": "turbo",
    "seed": 123,
    "width": 720,
    "height": 1280,
    "nologo": "true",
    "private": "true",
    "enhance": "false",
    "safe": "false",
    "referrer": "ImageGenTest"
}

async def fetch_image(prompt: str, filename: str = "temp.jpg", **params):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=300) as resp:
                if resp.status == 200:
                    with open(filename, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    return True
                else:
                    print(f"Failed to fetch image. Status: {resp.status}")
                    text = await resp.text()
                    print(text)
                    return False
    except Exception as e:
        print(f"Error: {e}")


async def main():
    prompt = "1girl, cute, cat girl, maid, large breast, nipples, nsfw, close up"
    success = await fetch_image(prompt, "output.jpg", **params)
    if success:
        print("Image downloaded successfully.")
    else:
        print("Image download failed.")

if __name__ == "__main__":
    asyncio.run(main())