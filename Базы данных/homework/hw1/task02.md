# Задача №2

---

### Контекст

В схеме `public` имеется таблица с измерениями роста (в дюймах) и веса (в фунтах) из одного исследования в США.

```postgresql
CREATE TABLE IF NOT EXISTS hw(
    id INTEGER,
    height FLOAT4,
    weight FLOAT4
)
```

### Постановка

Посчитайте BMI (Body Mass Index — [link](https://www.cdc.gov/healthyweight/assessing/bmi/adult_bmi/index.html#:~:text=Body%20mass%20index%20(BMI)%20is,weight%2C%20overweight%2C%20and%20obesity.)) 
для каждого измерения.

### Ожидаемый формат ответа

Ваш запрос должен возвращать таблицу формата:

| bmi     | 
|---------|
| 18.5    |
| 23.2637 |
| 33.042  |
| 21.901  |
