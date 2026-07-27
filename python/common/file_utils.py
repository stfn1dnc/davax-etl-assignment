#*******************************************************************************
#ATENTIE                                                                       *
#Acest fisier nu genereaza niciodata o eroare, dar returneaza o lista goala.   *
#                                                                              *
#*******************************************************************************
from pathlib import Path


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def find_input_files(input_directory: Path) -> list[Path]:
    if not input_directory.exists():
        return []

    return sorted(
        file_path
        for file_path in input_directory.iterdir()
        if file_path.is_file()  ##verifica ca variabila introdusa sa fie fisier nu folder
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS  ##extrage extensia
    )