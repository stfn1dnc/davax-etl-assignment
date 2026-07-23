from python.training_attendance.parser import (
    parse_meeting_file,
)


def test_parser_reads_all_three_sections(
    tmp_path,
):
    meeting_file = tmp_path / "Meeting1.csv"

    meeting_file.write_text(
        """1. Summary
Meeting title,Dava.X Academy - ETL Theory
Attended participants,1
Start time,"6/24/25, 1:47:45 PM"
End time,"6/24/25, 3:46:52 PM"
Meeting duration,1h 59m 7s
Average attendance time,1h 30m 52s

2. Participants
Name,First Join,Last Leave,In-Meeting Duration,Email,Participant ID,Role
Employee One,"6/24/25, 1:50:00 PM","6/24/25, 3:20:00 PM",1h 30m 0s,employee1@example.com,EMP001,Presenter

3. In-Meeting Activities
Name,Join Time,Leave Time,Duration,Email,Participant ID,Role
Employee One,"6/24/25, 1:50:00 PM","6/24/25, 2:20:00 PM",30m 0s,employee1@example.com,EMP001,Presenter
Employee One,"6/24/25, 2:30:00 PM","6/24/25, 3:30:00 PM",1h 0m 0s,employee1@example.com,EMP001,Presenter
""",
        encoding="utf-8",
    )

    result = parse_meeting_file(meeting_file)

    assert (
        result["session"]["meeting_title_raw"]
        == "Dava.X Academy - ETL Theory"
    )

    assert len(result["participants"]) == 1
    assert len(result["activities"]) == 2

    assert (
        result["participants"][0][
            "participant_id_raw"
        ]
        == "EMP001"
    )


def test_empty_file_is_rejected(
    tmp_path,
):
    meeting_file = tmp_path / "Meeting1.csv"
    meeting_file.write_text("", encoding="utf-8")

    try:
        parse_meeting_file(meeting_file)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "empty" in str(error).lower()