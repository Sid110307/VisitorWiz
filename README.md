<!-- markdownlint-disable MD030 -->

# VisitorWiz `v1.0.2`

> An attendance logging/tracking app for schools.

## Requirements

-   [MySQL](https://dev.mysql.com/)
-   [Python 3.6+](https://www.python.org/downloads/)
-   [MySQL Workbench (optional)](https://dev.mysql.com/downloads/workbench/)
-   A Working Camera

## First Steps

-   Run the following queries:

```sql
CREATE DATABASE IF NOT EXISTS `visitorwiz`;
```

```sql
CREATE TABLE IF NOT EXISTS `visitorwiz`.`attendance` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `face` LONGBLOB NOT NULL,
    `date` DATE NOT NULL,
    `status` VARCHAR(255) NOT NULL,
    `attendanceTime` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`ID`)
) ENGINE=InnoDB;
```

-   Save the students' faces as JPG images in a new `tests` folder in the project root.

## Quick Start

### Unix/Mac

```bash
source .venv/bin/activate
python main.py
```

### Windows

```bat
.venv\bin\activate.bat
python main.py
```

## Usage

-   It may take a while for the program to set up.
-   When the setting up is complete, A window with the camera will open.
-   When your face is recognized, the name of the student will be displayed.
-   Some details like date, attendance time, etc. will be saved in the database.
-   To exit the program, press `q`.
-   The data will be stored in a database called `visitorwiz`. It it recommended to access the database with a tool like [MySQL Workbench](https://www.mysql.com/products/workbench/).

## Database Structure

-   The database is called `visitorwiz`.
    -   There is a table in it, called `attendance`.
        -   All the attendance of the current day will be stored in this table.
        -   The table has the following columns:
            -   `ID`: The primary key.
            -   `name`: The name of the student.
            -   `face`: The face of the student.
            -   `date`: The date of the attendance.
            -   `status`: The status of the student.
            -   `attendanceTime`: The time of the attendance.
    -   Another table, called `attendance_old`, is used as a log for the previous days attendance (and attendance that is marked before that).
        -   It has a similar structure to the `attendance` table.
