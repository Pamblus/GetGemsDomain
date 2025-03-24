import asyncio
import requests
import json
import time
from pytoniq import LiteBalancer, WalletV4R2
from pytoniq_core import Address, Cell

# Константы
TESTNET_API_URL = "https://api.testnet.getgems.io/graphql"
HEADERS = {
    "accept": "*/*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\"",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "\"Android\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "x-auth-token": "22***********0_C-28dd23*******d240124******4741.b95ee***ad9*******0c4442f***eb3c",
    "x-gg-client": "v:1 l:ru"
}

# Функция для ручного ввода
def manual_input():
    name = input("Введите имя: ")
    return [name]

# Функция для парсинга файла
def parse_file(filename, min_chars, max_chars, count):
    valid_words = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            word = line.strip()
            if " " not in word and min_chars <= len(word) <= max_chars:
                valid_words.append(word)
                if len(valid_words) >= count:
                    break
    return valid_words

# Функция для расчета стоимости домена
def calculate_price(word):
    length = len(word)
    if word.isascii():  # Английские слова
        if length == 2:
            return 300
        elif length == 3:
            return 100
        elif length == 4:
            return 10
        elif length == 5:
            return 5
        elif length == 6:
            return 1
        elif length >= 7:
            return 0.5
    else:  # Кириллица
        if length == 1:
            return 300
        elif length == 2:
            return 300
        elif length == 3:
            return 100
        elif length == 4:
            return 10
        elif length == 5:
            return 5
        elif length == 6:
            return 1
        elif length >= 7:
            return 0.5
    return 0

# Функция для создания транзакции
async def create_transaction(wallet, destination_address, amount, payload_cell):
    message = wallet.create_wallet_internal_message(
        destination=Address(destination_address),
        value=int(amount * 1e9),  # Переводим в нанотоны
        body=payload_cell
    )
    await wallet.raw_transfer([message])

# Функция для минта домена
async def mint_domain(wallet, word, save_file=None):
    price = calculate_price(word)
    if price == 0:
        print(f"Слово '{word}' не подходит по длине или формату.")
        return

    data = {
        "operationName": "createCartTx",
        "variables": {
            "cart": [{
                "id": f"gg_dns_{word}-{int(time.time())}",
                "createGetGemsDns": {
                    "bidNano": str(int(price * 1e9)),  # Переводим в нанотоны
                    "domain": word
                }
            }]
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "5aa6d3591f1ea2a65bb759b0028a7340832106bff1b1f5a4fd1c20884856ec25"
            }
        }
    }

    try:
        response = requests.post(TESTNET_API_URL, headers=HEADERS, json=data)
        response_data = response.json()
        
        # Проверка на ошибки
        if response_data.get("data", {}).get("createCartTx", {}).get("errors"):
            print(f"Домен '{word}' уже существует или произошла ошибка API.")
            print("Полный ответ API:", json.dumps(response_data, indent=4))
            return

        tx_list = response_data["data"]["createCartTx"]["tx"]["list"]
        if not tx_list:
            print(f"Ошибка: список транзакций пуст для слова '{word}'.")
            return

        tx_item = tx_list[0]
        destination_address = tx_item["to"]
        payload_boc = tx_item["payloadBoc"]
        payload_cell = Cell.one_from_boc(payload_boc)

        await create_transaction(wallet, destination_address, price, payload_cell)
        print(f"Минт (слово: {word}) успешно, цена: {price} TON")

        if save_file:
            with open(save_file, "a", encoding="utf-8") as f:
                f.write(f"{word}\n")
    except Exception as e:
        print(f"Ошибка при минте слова '{word}': {e}")

# Основная функция
async def main():
    print("Меню:")
    print("1) Ручной ввод")
    print("2) Автоматически из файла")
    print("3) Сменить сеть (testnet)")
    choice = input("Выберите опцию: ")

    if choice == "1":
        words = manual_input()
    elif choice == "2":
        filename = input("Введите имя txt файла: ")
        min_chars = int(input("Введите минимальное количество символов: "))
        max_chars = int(input("Введите максимальное количество символов: "))
        count = int(input("Введите количество доменов: "))
        words = parse_file(filename, min_chars, max_chars, count)
    elif choice == "3":
        print("Смена сети пока не реализована.")
        return
    else:
        print("Неверный выбор.")
        return

    transactions_per_batch = int(input("Сколько делать транзакций за раз: "))
    delay = int(input("Введите время в секундах на 1 транзакцию: "))
    save_minted = int(input("Сохранять заминченные слова (1/0): ")) == 1
    save_file = "save_mint_ggdomain.txt" if save_minted else None

    total_cost = sum(calculate_price(word) for word in words)
    print(f"Сумма на минт: {total_cost} TON")

    input("Нажмите Enter для продолжения.")

    provider = LiteBalancer.from_testnet_config(trust_level=2)  # Используем Testnet
    await provider.start_up()

    mnemonics = "pride pulp ......" # Ваша сид-фраза
    wallet = await WalletV4R2.from_mnemonic(provider, mnemonics.split(" "))

    balance = await wallet.get_balance()
    print(f"Баланс кошелька: {balance / 1e9} TON")

    for i in range(0, len(words), transactions_per_batch):
        batch = words[i:i + transactions_per_batch]
        tasks = [mint_domain(wallet, word, save_file) for word in batch]
        await asyncio.gather(*tasks)
        if i + transactions_per_batch < len(words):
            print(f"Ожидание {delay} секунд...")
            await asyncio.sleep(delay)

    print("Минт завершён.")

if __name__ == '__main__':
    asyncio.run(main())
