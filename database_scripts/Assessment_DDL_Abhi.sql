CREATE TABLE IF NOT EXISTS customers
(
    customer_id VARCHAR(100) NOT NULL
    , event_time TIMESTAMP NOT NULL
    , last_name VARCHAR
    , address_city VARCHAR(50)
    , address_state VARCHAR(10)
    ,PRIMARY KEY (customer_id)
);


CREATE TABLE IF NOT EXISTS site_visit
(
    page_id VARCHAR(100) NOT NULL
    , customer_id VARCHAR(100) NOT NULL
    , event_time TIMESTAMP NOT NULL
    , tags jsonb
    ,PRIMARY KEY (customer_id, page_id)
);


CREATE TABLE IF NOT EXISTS image
(
    image_id VARCHAR(100) NOT NULL
    , event_time TIMESTAMP NOT NULL
    , customer_id VARCHAR(100) NOT NULL
    , camera_make VARCHAR(20)
    , camera_model VARCHAR(20)
    , PRIMARY KEY (customer_id, image_id,event_time)
);


CREATE TABLE IF NOT EXISTS "order"
(
    order_id VARCHAR(100) NOT NULL
    , event_time TIMESTAMP NOT NULL
    , customer_id VARCHAR(100) NOT NULL
    , total_amount VARCHAR(20) NOT NULL
    , PRIMARY KEY (order_id)
);

INSERT INTO customer VALUES ('96f55c7d8f42', '2017-01-06T12:46:46.384Z', 'Smith', 'Middletown', 'AK','2017-01-06T12:46:46.384Z');
INSERT INTO site_visit VALUES ('ac05e815502h', '96f55c7d8f42', '2017-01-09T12:46:46.384Z', '[{"some key": "some value"}]');
INSERT INTO image VALUES ('d8ede43b1d9f', '2017-01-06T12:47:12.344Z', '96f55c7d8f42', 'Canon', 'EOS 80D');
INSERT INTO "order" VALUES ('68d84e5d1a45', '2017-01-09T12:55:55.555Z', '96f55c7d8f42', '99.98 USD');