BEGIN TRANSACTION;
CREATE TABLE article
(
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT,
    dep    NUMBER,
    parent NUMBER,
    type   TEXT,
    edit   NUMBER,
    sum    NUMBER,
    rate   NUMBER
);
CREATE TABLE dep
(
    id      NUMBER,
    name    TEXT,
    warning NUMBER
);
INSERT INTO dep
VALUES (1, 'аксессуары', 0);
INSERT INTO dep
VALUES (2, '', 0);
INSERT INTO dep
VALUES (3, '', 0);
INSERT INTO dep
VALUES (4, '', 0);
INSERT INTO dep
VALUES (5, '', 0);
INSERT INTO dep
VALUES (6, '', 0);
INSERT INTO dep
VALUES (7, '', 0);
INSERT INTO dep
VALUES (8, '', 0);
INSERT INTO dep
VALUES (9, '', 0);
INSERT INTO dep
VALUES (10, '', 0);
CREATE TABLE edit_log
(
    date          TEXT,
    time          TEXT,
    title         TEXT,
    event         TEXT,
    original_date TEXT,
    original_time TEXT
);
CREATE TABLE income
(
    date    TEXT,
    time    TEXT,
    dep     NUMBER,
    article TEXT,
    art_id  NUMBER,
    sum     NUMBER,
    rate    NUMBER,
    name    TEXT,
    edit    NUMBER
);
CREATE TABLE misc
(
    name  TEXT,
    value TEXT
);
INSERT INTO misc
VALUES ('sync_enable', 0);
INSERT INTO misc
VALUES ('sync_period', 15);
INSERT INTO misc
VALUES ('sync_login', '');
INSERT INTO misc
VALUES ('sync_point', '');
INSERT INTO misc
VALUES ('sync_server', 'http://my-selling.ru');
INSERT INTO misc
VALUES ('sync_points', '[]');
INSERT INTO misc
VALUES ('sync_passw', '');
INSERT INTO misc
VALUES ('last_update', '1583270728');
INSERT INTO misc
VALUES ('update_date', '2000-04-21');
INSERT INTO misc
VALUES ('update_time', '13:00:00');
INSERT INTO misc
VALUES ('allow_del_phone', 1);
INSERT INTO misc
VALUES ('notepad_text', '');
INSERT INTO misc
VALUES ('cashbox', 0);
INSERT INTO misc
VALUES ('col_width_phone', 10);
INSERT INTO misc
VALUES ('col_width_name', 10);
INSERT INTO misc
VALUES ('col_width_details', 40);
INSERT INTO misc
VALUES ('col_width_date', 8);
INSERT INTO misc
VALUES ('col_width_time', 8);
INSERT INTO misc
VALUES ('col_width_done_date', 8);
INSERT INTO misc
VALUES ('col_width_done_time', 8);
INSERT INTO misc
VALUES ('col_width_main_time', 8);
INSERT INTO misc
VALUES ('col_width_main_dep', 5);
INSERT INTO misc
VALUES ('col_width_main_art', 60);
INSERT INTO misc
VALUES ('col_width_main_sum', 5);
INSERT INTO misc
VALUES ('col_width_main_rate', 1);
INSERT INTO misc
VALUES ('col_width_main_total', 5);
INSERT INTO misc
VALUES ('col_width_main_user', 12);


CREATE TABLE outcome
(
    date    TEXT,
    time    TEXT,
    article TEXT,
    art_id  NUMBER,
    sum     NUMBER,
    name    TEXT,
    edit    NUMBER
);
CREATE TABLE users
(
    name  TEXT,
    passw TEXT,
    caps  TEXT
);
INSERT INTO users
VALUES ('Администратор', '', '[]');

CREATE TABLE in_art
(
    id   NUMBER,
    date NUMBER,
    time NUMBER,
    dep  TEXT,
    name TEXT,
    rate NUMBER,
    user NUMBER
);
CREATE TABLE out_art
(
    date  NUMBER,
    time  NUMBER,
    name  TEXT,
    event TEXT,
    rate  NUMBER,
    user  NUMBER
);
CREATE TABLE phone
(
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    date         NUMBER,
    time         NUMBER,
    phone        TEXT,
    name         TEXT,
    details      TEXT,
    done         NUMBER,
    done_date    NUMBER,
    done_time    NUMBER,
    done_details TEXT
);
CREATE TABLE receipt
(
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             NUMBER,
    time             NUMBER,
    number           NUMBER,
    phone_main       TEXT,
    phone_additional TEXT,
    done             NUMBER,
    service_center   TEXT,
    max_repair_time  TEXT
);
CREATE TABLE receipt_item
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id      NUMBER,
    line_number     NUMBER,
    device          TEXT,
    serial          TEXT,
    declared_defect TEXT,
    existing_damage TEXT,
    alleged_defect  TEXT,
    repair_time     TEXT,
    repair_price    NUMBER,
    sale_price      NUMBER,
    warranty_period NUMBER
);
COMMIT;
