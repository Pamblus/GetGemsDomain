# GetGemsDomain
GetGems domain automatic miner
```Работа
# 🚀 TON DNS Minter (GetGems API)

Этот скрипт позволяет автоматически регистрировать GetGems domain DNS имена в сети TON через API GetGems.

## 📦 Установка зависимостей

```bash
pip install pytoniq pytoniq-core requests
```

## 🔑 Настройка

1. **x-auth-token**:
Нужно заменить auth токен на свой. Я это сделал с помощью консоли разработчика при нажатии и вводе текста на dns gg 
   ```python
   HEADERS = {
       "accept": "*/*",
       "x-auth-token": "2******10400_C-28d******1f5ed24012****fcc84741.b****aadad91392******42fecbeb3c",
       "x-gg-client": "v:1 l:ru"
   }
   ```
   - Токен может устаревать, проверяйте актуальность (хз)

2. **Seed-фраза**:
Сид фраза кошелька с которого будут транзакции
   ```python
   mnemonics = "pride pulp ....."
   ```

## 🛠 Функционал

### Основные возможности:
- ✅ Ручной ввод доменов
- ✅ Пакетная обработка из файла (`english_words.txt`)
- ✅ Автоматический расчет стоимости
- ✅ Поддержка кириллицы и латиницы
- ✅ Настройка задержек между транзакциями

### Ценообразование:
```python
def calculate_price(word):
    length = len(word)
    if word.isascii():  # Английские
        if length == 2: return 300
        elif length == 3: return 100
        elif length == 4: return 10
        elif length == 5: return 5
        elif length == 6: return 1
        elif length >= 7: return 0.5
    else:  # Кириллица
        if length == 1: return 300
        elif length == 2: return 300
        elif length == 3: return 100
        elif length == 4: return 10
        elif length == 5: return 5
        elif length == 6: return 1
        elif length >= 7: return 0.5
    return 0
```

## 🖥 Использование

1. Запустите скрипт:
```bash
python3 getgems_dns_minter.py
```

2. Выберите режим:
```
1) Ручной ввод
2) Выбрать Файл
3) Сменить сеть (не работает, в ручную)
```

3. Для пакетной обработки укажите:
- Имя файла
- Диапазон длин (например 7-7 символов)
- Количество доменов
- Параметры транзакций

## ⚠️ Важные примечания

1. **Testnet**:
   ```python
   provider = LiteBalancer.from_testnet_config(trust_level=2)
   ```

2. **Безопасность**:
   - Никогда не публикуйте свою seed-фразу
   - Храните токены в безопасности
   - остерегайтесь женщин

3. **Ограничения**:
   - API может блокировать при частых запросах
   - Соблюдайте указанные задержки

## 📝 Пример работы

```bash
Введите имя: mydomain
Сумма на минт: 0.5 TON
Минт (слово: mydomain) успешно, цена: 0.5 TON
```

## 👨💻 Автор

По всем вопросам: [@pamblus в Telegram](https://t.me/pamblus)

![TON Logo](https://raw.githubusercontent.com/gist/PonomareVlad/ca27237883d2a47a0588cd180139db55/raw/68996051ffabfc65520c3376df6df11898d3c736/TON.svg)
``` 
