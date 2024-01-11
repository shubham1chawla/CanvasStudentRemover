# Canvas Student Remover (ASU)

This Selenium project automates the removal of students from an ASU Canvas course, which would have been a manual task otherwise.

## Technologies

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)

## Prerequisites
- Make sure you have `poetry` installed on your system. If not, use `pip install poetry` command.
- Configure `poetry` to create virtual environments inside project directory by executing `poetry config virtualenvs.in-project true` command.
- Install dependencies by executing `poetry install` command.
- To enter the virtual environment, use `poetry shell` command.

## Usage

    python main.py \
    --url "https://canvas.asu.edu/courses/<COURSE_CODE>/users"  \
    --username "<ASU_LOGIN_USERNAME>" \
    --password "<ASU_LOGIN_PASSWORD>" \
    --limit <LIMIT_STUDENTS_TO_REMOVE> \
    --exclude "<TXT_FILE_WITH_NAMES_TO_EXCLUDE_STUDENTS>"

> **Note:** Default limit is set to **25** students, you can change it in the `main.py` file or provide it to the CLI

> **Note:** Providing exclude file is optional.