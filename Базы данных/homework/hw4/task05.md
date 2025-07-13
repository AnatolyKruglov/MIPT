# Задача №5

---

### Контекст

Для администраторов баз данных часто возникает необходимость мониторить потребляемое дисковое пространство, а особо 
отслеживать пользователей, которое злостно "отъедают" память.

### Постановка

Cоздадите представление
```postgresql
v_used_size_per_user(
    table_owner TEXT, 
    schema_name TEXT, 
    table_name TEXT, 
    table_size TEXT, 
    used_per_schema_user_total_size TEXT, 
    used_user_total_size TEXT
)
```
которая агрегирует информацию о потребляемой памяти по каждому пользователю текущей базы данных.
Подробнее о полях этого представления:
 * `table_owner` - имя пользователя
 * `schema_name` - имя схемы
 * `table_name` - имя таблицы, `table_owner` - владелец этой таблицы
 * `table_size` - размер таблицы (тип поля - `TEXT`, человекочитаемый формат)
 * `used_per_schema_user_total_size` - размер всех таблиц пользователя `table_owner` в схеме `schema_name` (тип поля - `TEXT`, человекочитаемый формат)
 * `used_user_total_size` - размер вообще всех таблиц пользователя `table_owner` в базе данных (тип поля - `TEXT`, человекочитаемый формат)

Скрипт создания должен быть нечувствителен к уже объявленным представлениям. Можно создавать вспомогательные представления и CTE.

Для приведения размера в человекочитаемый вид можно воспользоваться функцией `pg_size_pretty`.

**Пример**  

Пример запроса к нашему представлению:
```postgresql
SELECT
    table_owner,
    table_name,
    table_size,
    schema_name,
    used_per_schema_user_total_size,
    used_user_total_size
FROM
    v_used_size_per_user
ORDER BY
    pg_size_bytes(used_user_total_size) DESC,
    table_owner,
    pg_size_bytes(used_per_schema_user_total_size) DESC,
    schema_name,
    pg_size_bytes(table_size) DESC,
    table_name;

---

 ----------------------------------------------------------------------------------------------------------------
| table_owner | table_name   | table_size | schema_name | used_per_schema_user_total_size | used_user_total_size |
|-------------|--------------|------------|-------------|---------------------------------|----------------------|
|  postgres   | pg_proc      | 768 kB     | pg_catalog  | 2912 kB                         | 3000 kB              |
|  postgres   | pg_attribute | 456 kB     | pg_catalog  | 2912 kB                         | 3000 kB              |
|  ...        | ...          | ...        |    ...      | ...                             | ...                  |
 ----------------------------------------------------------------------------------------------------------------

```

### Ожидаемый формат ответа

Выводить ничего не надо. Скрипт с решением должен содержать __только__ объявление представления.
