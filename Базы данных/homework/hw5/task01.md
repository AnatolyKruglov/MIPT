В схеме public имеется таблица с историей криптовалюты.
CREATE TABLE IF NOT EXISTS coins(
    dt VARCHAR(16),
    avg_price NUMERIC,
    full_nm VARCHAR(128),
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    vol NUMERIC,
    market NUMERIC
)
Поясним значения хранящиеся в колонках:
dt — дата измерений
avg_price — средняя цена монеты за торговый день в USD
full_nm — название монеты
open_price — цена монеты в начале торгов данного дня
high_price — самая высокая цена данной монеты в течение торгового дня
low_price — самая низкая цена данной монеты в течение торгового дня
close_price — цена монеты в конце торгов данного дня
vol — объем торгов данной монетой на биржах в данный день
market — капитализация данной монеты в данный день

Написать функцию count_non_volatile_days(full_nm TEXT) на plpgsql, которая считает кол-во дней, когда цена торгов криптомонеты не менялась.
Если такой криптомонеты не существует, вызвать исключение с ERRCODE = '02000' b текстом: Crypto currency with name "{full_nm}" is absent in database!, {full_nm} — имя криптомонеты, взятое из аргументов функции. 


Исправь ошибки:
syntax error at or near "IF"
IF x = "Binance Coin" THEN RETURN 0 END IF;

____________________________ test_non_zero_answers _____________________________
/home/tests/hw5/test_task01.py:160: in test_non_zero_answers
    assert test_cnt == cnt, (
E   AssertionError: Coin 'Bitcoin' has 1 days instead of count_non_volatile_days(Bitcoin) == 1866
E   assert 1866 == 1
______________________________ test_zero_answers _______________________________
/home/tests/hw5/test_task01.py:176: in test_zero_answers
    assert test_cnt == 0, (
E   AssertionError: Coin 'Binance Coin' has 0 days instead of count_non_volatile_days(Binance Coin) == 317
E   assert 317 == 0
=========================== short test summary info ============================
FAILED ../../../home/tests/hw5/test_task01.py::test_non_zero_answers - AssertionError: Coin 'Bitcoin' has 1 days instead of count_non_volatile_days(Bitcoin) == 1866
assert 1866 == 1
FAILED ../../../home/tests/hw5/test_task01.py::test_zero_answers - AssertionError: Coin 'Binance Coin' has 0 days instead of count_non_volatile_days(Binance Coin) == 317
assert 317 == 0



CREATE OR REPLACE FUNCTION count_non_volatile_days(x TEXT)
RETURNS INTEGER AS 
$$
DECLARE
  non_volatile_days INTEGER;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM coins WHERE coins.full_nm = x) THEN
    RAISE EXCEPTION 'Crypto currency with name "%s" is absent in database!', x USING ERRCODE = '02000';
  END IF;
  SELECT COUNT(*) INTO non_volatile_days
  FROM (
    SELECT DISTINCT ON (dt) close_price
    FROM coins
    WHERE coins.full_nm = x
    ORDER BY dt, close_price
  ) AS subquery;
  RETURN non_volatile_days;
END;
$$ LANGUAGE plpgsql;


пожалуйста, попробуй исправить ошибки по сообщениям:
____________________________ test_non_zero_answers _____________________________
/home/tests/hw5/test_task01.py:160: in test_non_zero_answers
    assert test_cnt == cnt, (
E   AssertionError: Coin 'Bitcoin' has 1 days instead of count_non_volatile_days(Bitcoin) == 5
E   assert 5 == 1
______________________________ test_zero_answers _______________________________
/home/tests/hw5/test_task01.py:176: in test_zero_answers
    assert test_cnt == 0, (
E   AssertionError: Coin 'Binance Coin' has 0 days instead of count_non_volatile_days(Binance Coin) == 8
E   assert 8 == 0
=========================== short test summary info ============================
FAILED ../../../home/tests/hw5/test_task01.py::test_non_zero_answers - AssertionError: Coin 'Bitcoin' has 1 days instead of count_non_volatile_days(Bitcoin) == 5
assert 5 == 1
FAILED ../../../home/tests/hw5/test_task01.py::test_zero_answers - AssertionError: Coin 'Binance Coin' has 0 days instead of count_non_volatile_days(Binance Coin) == 8
assert 8 == 0