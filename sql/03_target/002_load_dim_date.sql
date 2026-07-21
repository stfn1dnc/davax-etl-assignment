INSERT INTO target.dim_date (
    date_key,
    full_date,
    day_number,
    day_name,
    week_number,
    month_number,
    month_name,
    quarter_number,
    year_number,
    is_weekend
)
SELECT
    TO_NUMBER(TO_CHAR(calendar_date, 'YYYYMMDD')),
    calendar_date,
    TO_NUMBER(TO_CHAR(calendar_date, 'DD')),
    TRIM(TO_CHAR(calendar_date, 'DAY', 'NLS_DATE_LANGUAGE=ENGLISH')),
    TO_NUMBER(TO_CHAR(calendar_date, 'IW')),
    TO_NUMBER(TO_CHAR(calendar_date, 'MM')),
    TRIM(TO_CHAR(calendar_date, 'MONTH', 'NLS_DATE_LANGUAGE=ENGLISH')),
    TO_NUMBER(TO_CHAR(calendar_date, 'Q')),
    TO_NUMBER(TO_CHAR(calendar_date, 'YYYY')),
    CASE
        WHEN TO_CHAR(
            calendar_date,
            'DY',
            'NLS_DATE_LANGUAGE=ENGLISH'
        ) IN ('SAT', 'SUN')
        THEN 'Y'
        ELSE 'N'
    END
FROM (
    SELECT DATE '2020-01-01' + LEVEL - 1 AS calendar_date
    FROM dual
    CONNECT BY LEVEL <= (
        DATE '2030-12-31' - DATE '2020-01-01' + 1
    )
);

COMMIT;