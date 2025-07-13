
Представьте, что вы работает в компании специализирующиеся на высокочастотной торговли. Текущий проект, на котором вы 
задействованы, предоставляет безопасную платформу для торгов в криптовалюте.

Непосредственно ваша текущая задача это миграция данных из одного хранилища в другое. Системой-источником выбран был MongoDb,
а система-приемник у вас Postgres. Архитекторами проекта было решено воспользоваться встроенными механизмами переноса данных, 
а не писать свой отдельный сервис.

В Postgres имеется 3 таблицы, в которые делается вставка: auctioneer, attachment, bet.

Данные в источнике хранятся в json-коллекции betting в таком формате:
{
    "auctioneer": {
        "firstname": "john",
        "lastname": "doe",
        "nickname": "mr.notknown",
        "email": "john.doe@email.com"
    },
    "attachment": {
        "filename": "key.token1",
        "location": {
            "datacenter": "AWS_EU",
            "localname": "iD1234sdv23r23rtfwv"
        }
    },
    "bet": {
        "volume": 0.00001,
        "ts": 1672520400
    }
}

Пользователи платформы (информация о пользователе — таблица auctioneer) делают ставки на аукционе
(таблица bet). Из соображений безопасности во время произведения ставки пользователь 
должен приложить файл, полученный во время регистрации на аукцион (таблица attachment).

Внутренний механизм миграции:
1. делает вставку БД по одному документу из коллекции;
2. не имеет прав на вставку в таблицы auctioneer, attachment, bet;
3. может вставлять документы "как есть" в виде строки.
В силу этих ограничений вставка происходит черех view v_auction_payload.
Для нумерации событий стоит воспользоваться SEQUENCE.
Нумерация должна начинаться с 1.
Для получения текущего момента времени можно воспользоваться функцией now().

Ваше решение должно быть в виде дополнения к скрипту:
postgresql
CREATE TABLE auctioneer (
    event_id   INTEGER,
    firstname  TEXT,
    lastname   TEXT,
    nickname   TEXT,
    email      TEXT
);
CREATE TABLE attachment (
    event_id   INTEGER,
    filename   TEXT,
    datacenter TEXT,
    localname  TEXT
);
CREATE TABLE bet (
    event_id   INTEGER,
    volume     NUMERIC,
    ts         TIMESTAMP
);

CREATE OR REPLACE FUNCTION auctioneer_to_json(event_id INTEGER)
    RETURNS TEXT
    LANGUAGE plpgsql
AS $$
DECLARE
    firstname_ TEXT;
    lastname_  TEXT;
    nickname_  TEXT;
    email_     TEXT;
BEGIN
    SELECT
        firstname, lastname, nickname, email
    INTO
        firstname_, lastname_, nickname_, email_
    FROM
        auctioneer
    WHERE
        auctioneer.event_id = $1;
    RETURN format(
        '{"firstname": %I, "lastname": %I, "nickname": %I, "email": %I}',
        firstname_, lastname_, nickname_, email_
    );
END;
$$;

CREATE OR REPLACE FUNCTION attachment_to_json(event_id INTEGER)
    RETURNS TEXT
    LANGUAGE plpgsql
AS $$
DECLARE
    filename_   TEXT;
    datacenter_ TEXT;
    localname_  TEXT;
BEGIN
    SELECT
        filename, datacenter, localname
    INTO
        filename_, datacenter_, localname_
    FROM
        attachment
    WHERE
        attachment.event_id = $1;
    RETURN format(
        '{"filename": %I, location": {"datacenter": %I, "localname": %I}}',
        filename_, datacenter_, localname_
    );
END;
$$;

CREATE OR REPLACE FUNCTION bet_to_json(event_id INTEGER)
    RETURNS TEXT
    LANGUAGE plpgsql
AS $$
DECLARE
    volume_     NUMERIC;
    ts_         TIMESTAMP;
BEGIN
    SELECT
        volume, ts
    INTO
        volume_, ts_
    FROM
        bet
    WHERE
        bet.event_id = $1;
    RETURN format(
        '{"volume": %s, "ts": %s}',
        volume_, EXTRACT(EPOCH FROM ts_)::BIGINT
    );
END;
$$;


CREATE OR REPLACE VIEW v_auction_payload(payload) AS
    SELECT
        format(
            '{"auctioneer": %s, "attachment": %s, "bet": %s}',
            auctioneer_to_json(bet.event_id),
            attachment_to_json(bet.event_id),
            bet_to_json(bet.event_id)
        )
    FROM
        auctioneer
    JOIN
        attachment
        ON
            auctioneer.event_id = attachment.event_id
    JOIN
        bet
        ON
            attachment.event_id = bet.event_id;


### Пример
Ваше дополнение к скрипту должно позволить получить следующий эффект
postgresql
INSERT INTO v_auction_payload(payload) VALUES (
'{
    "auctioneer": {
        "firstname": "john",
        "lastname": "doe",
        "nickname": "mr.notknown",
        "email": "john.doe@email.com"
    },
    "attachment": {
        "filename": "key.token1",
        "location": {
            "datacenter": "AWS_EU",
            "localname": "iD1234sdv23r23rtfwv"
        }
    },
    "bet": {
        "volume": 0.00001,
        "ts": 1672520400
    }
}');
INSERT INTO v_auction_payload(payload) VALUES (
'{
    "auctioneer": {
        "firstname": "john",
        "lastname": "doe",
        "nickname": "mr.notknown",
        "email": "john.doe@email.com"
    },
    "attachment": {
        "filename": "key.token2",
        "location": {
            "datacenter": "AWS_US",
            "localname": "iDasd@-asfasf23@3s"
        }
    },
    "bet": {
        "volume": 0.00085,
        "ts": 1676928960
    }
}');

postgresql
SELECT * FROM auctioneer;
1,john,doe,mr.notknown,john.doe@email.com
2,john,doe,mr.notknown,john.doe@email.com

postgresql
SELECT * FROM attachment;
1,key.token1,AWS_EU,iD1234sdv23r23rtfwv
2,key.token2,AWS_US,iDasd@-asfasf23@3s

postgresql
SELECT * FROM bet;
1,0.00001,2022-12-31 21:00:00.000000
2,0.00085,2023-02-20 21:36:00.000000

postgresql
SELECT * FROM v_auction_payload;
"{""auctioneer"": {""firstname"": john, ""lastname"": doe, ""nickname"": ""mr.notknown"", ""email"": ""john.doe@email.com""}, ""attachment"": {""filename"": ""key.token1"", location"": {""datacenter"": ""AWS_EU"", ""localname"": ""iD1234sdv23r23rtfwv""}}, ""bet"": {""volume"": 0.00001, ""ts"": 1672520400}}"
"{""auctioneer"": {""firstname"": john, ""lastname"": doe, ""nickname"": ""mr.notknown"", ""email"": ""john.doe@email.com""}, ""attachment"": {""filename"": ""key.token2"", location"": {""datacenter"": ""AWS_US"", ""localname"": ""iDasd@-asfasf23@3s""}}, ""bet"": {""volume"": 0.00085, ""ts"": 1676928960}}"