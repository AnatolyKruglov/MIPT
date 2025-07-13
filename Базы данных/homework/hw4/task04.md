# Задача №4

---

### Контекст

В PostgreSQL существуют такие вещи как _партиции таблиц_. 
Ознакомиться с тем что это такое и как это употреблять можно [здесь](https://gitlab.atp-fivt.org/courses-public/db2023-supplementary/global/-/tree/main/practice/seminars/11-olap#11-partitioning-%D0%BF%D0%B0%D1%80%D1%82%D0%B8%D1%86%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%D1%81%D0%B5%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5). 
Достаточно посмотреть [пункт 1.1.1](https://gitlab.atp-fivt.org/courses-public/db2023-supplementary/global/-/tree/main/practice/seminars/11-olap#111-%D0%BE%D0%B1%D1%89%D0%B8%D0%B5-%D1%81%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F), но можно и больше :)

### Постановка

Усложним предыдущую задачу и cоздадим представление
`v_rec_level_partition_info(parent_schema, parent_table, child_schema, child_table, part_level)`, 
которая агрегирует информацию о партициях первого уровня (непосредственные партиции), второго уровня (таблица и партиции партиций) и так далее. 
Скрипт создания должен быть нечувствителен к уже объявленным представлениям. Можно создавать вспомогательные представления и CTE.

**Пример**  

```postgresql
CREATE TABLE dt_totals (
    dt_total date NOT NULL,
    geo varchar(2) not null,
    impressions integer DEFAULT 0 NOT NULL,
    sales integer DEFAULT 0 NOT NULL
)
PARTITION BY RANGE (dt_total);

CREATE TABLE dt_totals_201801
    PARTITION OF dt_totals
        FOR VALUES FROM ('2018-01-01') TO ('2018-01-31')
    PARTITION BY LIST (geo);

CREATE TABLE dt_totals_UK_201801 PARTITION OF dt_totals_201801 FOR VALUES IN ('UK');
CREATE TABLE dt_totals_US_201801 PARTITION OF dt_totals_201801 FOR VALUES IN ('US');
CREATE TABLE dt_totals_AU_201801 PARTITION OF dt_totals_201801 FOR VALUES IN ('AU');
```
Пример запроса к нашему представлению:
```postgresql
SELECT
    part_level,
    parent_schema,
    parent_table,
    child_schema,
    child_table
FROM
    v_rec_level_partition_info
ORDER BY
    part_level,
    parent_schema,
    parent_table,
    child_schema,
    child_table;
---
 ------------------------------------------------------------------------------------
| part_level | parent_schema | parent_table    | child_schema |   child_table        |
|------------|---------------|------------------|--------------|---------------------|
|     1      |     public    | dt_totals        |    public    | dt_totals_201801    |
|     1      |     public    | dt_totals_201801 |    public    | dt_totals_au_201801 |
|     1      |     public    | dt_totals_201801 |    public    | dt_totals_uk_201801 |
|     1      |     public    | dt_totals_201801 |    public    | dt_totals_us_201801 |
|     2      |     public    | dt_totals        |    public    | dt_totals_au_201801 |
|     2      |     public    | dt_totals        |    public    | dt_totals_uk_201801 |
|     2      |     public    | dt_totals        |    public    | dt_totals_us_201801 |
 ------------------------------------------------------------------------------------
```

### Ожидаемый формат ответа

Выводить ничего не надо. Скрипт с решением должен содержать __только__ объявление представления.
