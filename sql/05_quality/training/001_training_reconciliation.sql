/*
Compare the participant duration reported in section 2
with the sum of detailed activities from section 3.
*/

SELECT
    p.run_id,
    p.session_raw_id,
    p.participant_name,
    p.email,
    p.participant_id,

    p.duration_seconds
        AS participant_reported_seconds,

    NVL(a.activity_seconds, 0)
        AS calculated_activity_seconds,

    p.duration_seconds
        - NVL(a.activity_seconds, 0)
        AS difference_seconds,

    CASE
        WHEN ABS(
            p.duration_seconds
            - NVL(a.activity_seconds, 0)
        ) <= 5
        THEN 'PASSED'
        ELSE 'WARNING'
    END AS reconciliation_status

FROM staging.stg_training_participant p

LEFT JOIN (
    SELECT
        session_raw_id,

        NVL(
            LOWER(email),
            NVL(
                participant_id,
                LOWER(participant_name)
            )
        ) AS participant_match_key,

        SUM(duration_seconds) AS activity_seconds

    FROM staging.stg_training_activity

    WHERE validation_status = 'VALID'

    GROUP BY
        session_raw_id,
        NVL(
            LOWER(email),
            NVL(
                participant_id,
                LOWER(participant_name)
            )
        )
) a
    ON a.session_raw_id = p.session_raw_id
   AND a.participant_match_key =
       NVL(
           LOWER(p.email),
           NVL(
               p.participant_id,
               LOWER(p.participant_name)
           )
       )

WHERE p.validation_status = 'VALID'

ORDER BY
    p.run_id,
    p.participant_name;