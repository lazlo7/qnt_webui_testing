# Тестирование web-интерфейса приложения SBTS

Тестирование интерфейса веб-приложения с помощью `Selenium`, `pytest` и `ChromeDriver`.

## Как запустить тесты?

1\. Запуск сервера приложения `SBTS`:
```
docker compose up -d
```

2\. Установка зависимостей и запуск тестов.  
Для `nix` систем:
```
nix develop
pytest webui
```

С помощью `poetry`:
```
poetry install
poetry run pytest webui
```

С помощью `pip`:
```
pip -r requirements.txt
pytest webui
```

Перед запуском тестов можно указать значения переменных окружения:
- `TESTING_URL`: ссылка, к которой будет подключаться браузер (по умолчанию - `http://localhost:8091/`)
- `CHROME_PATH`: путь к браузеру `Chrome` (по умолчанию выбирается автоматически)  

Ожидается, что все тесты провалятся, что сообщит о найденных ошибках.

## Найденные ошибки

### Ошибка #1

**Раздел**  
2\. Описание модели и режима перемещения

**Описание**  
Перемещаемый корабль может выйти за предел или переместиться на место левого ограничителя (расположенного на координате -20), при быстром нажатии на кнопку перемещения влево, что запрещено правилами ТЗ.

**Тест**  
Проверяется тестом `test_moving_past_left_boundary()`.

### Ошибка #2

**Раздел**  
2\. Описание модели и режима перемещения

**Описание**  
Текущий корабль может перемещаться на произвольное число клеток за время таймера перемещения, что позволяет пермещаться на более чем одну клетку за две секунды, хотя ТЗ заявяет, что ограничение на время перемещения на одну клетку должно составлять не менее двух секунд.

**Тест**  
Используется тест `test_moving_during_timer()`, где проверяется что кнопка может быть нажата во время таймера перемещения и таймер обновится, а также что мы дейстивтельно оказались более чем на одной клетке от начальной позиции за меньшее время.
