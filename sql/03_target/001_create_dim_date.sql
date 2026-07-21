CREATE TABLE target.dim_date (
    date_key NUMBER(8) NOT NULL,
    full_date DATE NOT NULL,
    day_number NUMBER(2) NOT NULL,
    day_name VARCHAR2(20) NOT NULL,
    week_number NUMBER(2) NOT NULL,
    month_number NUMBER(2) NOT NULL,
    month_name VARCHAR2(20) NOT NULL,
    quarter_number NUMBER(1) NOT NULL,
    year_number NUMBER(4) NOT NULL,
    is_weekend CHAR(1) NOT NULL,

    CONSTRAINT pk_dim_date
        PRIMARY KEY (date_key),

    CONSTRAINT uq_dim_date_full_date
        UNIQUE (full_date),

    CONSTRAINT ck_dim_date_weekend
        CHECK (is_weekend IN ('Y', 'N'))
);