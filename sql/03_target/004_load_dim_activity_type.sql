INSERT INTO target.dim_activity_type (
    activity_code,
    activity_name,
    description
)
VALUES (
    'WORK',
    'Worked Hours',
    'Hours worked by an employee on a project.'
);

INSERT INTO target.dim_activity_type (
    activity_code,
    activity_name,
    description
)
VALUES (
    'ABSENCE',
    'Absence',
    'Employee absence hours such as leave or sickness.'
);

INSERT INTO target.dim_activity_type (
    activity_code,
    activity_name,
    description
)
VALUES (
    'TRAINING',
    'Training Attendance',
    'Employee attendance at a training session or meeting.'
);

INSERT INTO target.dim_activity_type (
    activity_code,
    activity_name,
    description
)
VALUES (
    'EXAM',
    'Exam Activity',
    'Employee exam-related activity or scheduled exam absence.'
);

COMMIT;