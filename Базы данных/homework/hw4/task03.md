# Задача №3

---

### Контекст

В PostgreSQL существуют такие вещи как _партиции таблиц_. 
Ознакомиться с тем что это такое и как это употреблять можно [здесь](https://gitlab.atp-fivt.org/courses-public/db2023-supplementary/global/-/tree/main/practice/seminars/11-olap#11-partitioning-%D0%BF%D0%B0%D1%80%D1%82%D0%B8%D1%86%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%D1%81%D0%B5%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5). 
Достаточно посмотреть [пункт 1.1.1](https://gitlab.atp-fivt.org/courses-public/db2023-supplementary/global/-/tree/main/practice/seminars/11-olap#111-%D0%BE%D0%B1%D1%89%D0%B8%D0%B5-%D1%81%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F), но можно и больше :)

### Постановка

Создать представление
`v_first_level_partition_info(parent_schema, parent_table, child_schema, child_table)`, 
которая агрегирует информацию о партициях первого уровня (непосредственные партиции). Скрипт создания должен быть нечувствителен к уже объявленным представлениям. 

Для решения вам потребуются системые таблицы: `pg_inherits`, `pg_class`, `pg_namespace`.

**Пример**  

Имея таблицу:
```postgresql
CREATE TABLE people_partitioned (
    person_id       SERIAL,
    first_name      VARCHAR(128)  NOT NULL,
    last_name       VARCHAR(128)  NOT NULL,
    birthday        DATE          NOT NULL
) PARTITION BY RANGE (birthday);


CREATE TABLE people_partitioned_birthdays_1800_to_1850
    PARTITION OF people_partitioned
        FOR VALUES FROM ('1800-01-01') TO ('1849-12-31');

CREATE TABLE people_partitioned_birthdays_1850_to_1900
    PARTITION OF people_partitioned
        FOR VALUES FROM ('1850-01-01') TO ('1899-12-31');

CREATE TABLE people_partitioned_birthdays_1900_to_1950
    PARTITION OF people_partitioned
        FOR VALUES FROM ('1900-01-01') TO ('1949-12-31');

CREATE TABLE people_partitioned_birthdays_1950_to_2000
    PARTITION OF people_partitioned
        FOR VALUES FROM ('1950-01-01') TO ('1999-12-31');

CREATE TABLE people_partitioned_birthdays_2000_to_2050
    PARTITION OF people_partitioned
        FOR VALUES FROM ('2000-01-01') TO ('2049-12-31');
```
Пример запроса к нашему представлению:
```postgresql
SELECT
    child_schema,
    child_table
FROM
    v_first_level_partition_info
WHERE 1=1
    AND parent_schema = 'public'
    AND parent_table = 'people_partitioned'
ORDER BY
    child_schema,
    child_table;
---
 ----------------------------------------------------------
| child_schema |              child_table                  |
|--------------|-------------------------------------------|
|    public    | people_partitioned_birthdays_1800_to_1850 |
|    public    | people_partitioned_birthdays_1850_to_1900 |
|    public    | people_partitioned_birthdays_1900_to_1950 |
|    public    | people_partitioned_birthdays_1950_to_2000 |
|    public    | people_partitioned_birthdays_2000_to_2050 |
 ----------------------------------------------------------
```

### Ожидаемый формат ответа

Выводить ничего не надо. Скрипт с решением должен содержать __только__ объявление представления.
