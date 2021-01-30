import sys
import argparse
import datetime

import pymysql
from pymysql.cursors import DictCursor
from pymysql.err import DatabaseError
from rich.console import Console
from rich.table import Table

from .config import DB


PENDING = "PENDING"
PROGRESS = "PROGRESS"
FINISHED = "FINISHED"


def register_command(args, conn, cur):
    # print("register_command::args =", args)
    # print("register_command::conn =", conn)
    # print("register_command::cur =", cur)

    sql = """
    INSERT INTO users(username, first_name, last_name)
    VALUES (%s, %s, %s)
    """
    values = (
        args.username,
        args.username.capitalize() if args.first is None else args.first,
        args.last,
    )

    try:
        cur.execute(sql, values)
        conn.commit()
        print("User registered successfully.")
    except pymysql.DatabaseError as exc:
        conn.rollback()
        print("Could not save user.")
        print("Error:", exc)


def list_users_command(args, conn, cur):
    sql = """
SELECT user_id, username,
    TRIM(CONCAT(IFNULL(first_name, ''), ' ', IFNULL(last_name, ''))) AS fullname
FROM users
ORDER BY user_id
    """

    table = Table(title="Users")
    table.add_column("ID", justify="right")
    table.add_column("Username", style="blue", no_wrap=True)
    table.add_column("Fullname")

    cur.execute(sql)
    for row in cur:
        table.add_row("{}.".format(row["user_id"]), row["username"], row["fullname"])

    console = Console()
    console.print(table)


def create_project_command(args, conn, cur):
    sql = """
    INSERT INTO projects(name, manager_id)
    VALUES (%s, %s)
    """

    values = (args.name, args.manager)

    try:
        cur.execute(sql, values)
        conn.commit()
        print("Project created successfully.")
    except DatabaseError as exc:
        print("Could not create project.")
        print("ERROR:", exc)
        conn.rollback()


def list_projects_command(args, conn, cur):
    sql = """
    SELECT p.project_id, p.name,
        TRIM(CONCAT(IFNULL(u.first_name, ''), ' ', IFNULL(u.last_name, '')))
            AS manager_name
    FROM projects p INNER JOIN users u ON p.manager_id = u.user_id
    ORDER BY u.user_id, p.project_id
    """

    table = Table(title="Projects")
    table.add_column("ID", justify="right", style="blue")
    table.add_column("Project name", no_wrap=True, style="green")
    table.add_column("Manager", style="red")

    cur.execute(sql)
    for row in cur:
        table.add_row(f"{row['project_id']}.", row["name"], row["manager_name"])

    console = Console()
    console.print(table)


def add_member_command(args, conn, cur):
    sql = """
    INSERT INTO members(project_id, user_id)
    VALUES (%s, %s)
    """

    console = Console()

    try:
        cur.execute(
            sql,
            (
                args.project_id,
                args.user_id,
            ),
        )
        conn.commit()
        console.print("Member added successfully.", style="green")
    except DatabaseError as exc:
        conn.rollback()
        console.print("Could not add project member.", style="magenta")
        console.print(f"ERROR: {exc!r}", style="red")


def project_details_command(args, conn, cur):
    """
    Get project details using 2 queries
    """

    sql_project = """
    SELECT p.project_id, p.name,
        TRIM(CONCAT(IFNULL(u.first_name, ''), ' ', IFNULL(u.last_name, '')))
            AS manager_name
    FROM projects p INNER JOIN users u ON p.manager_id = u.user_id
    WHERE p.project_id = %s
    """

    sql_members = """
    SELECT u.user_id, u.username,
        TRIM(CONCAT(IFNULL(u.first_name, ''), ' ', IFNULL(u.last_name, '')))
            AS fullname
    FROM members m
        INNER JOIN users u ON m.user_id = u.user_id
    WHERE m.project_id = %s
    """

    console = Console()

    cur.execute(sql_project, (args.project_id,))
    project = cur.fetchone()
    if project is None:
        console.print("Project not found", style="red")
        return

    cur.execute(sql_members, (args.project_id,))
    members = cur.fetchall()

    console.print("ID:", project["project_id"])
    console.print("Project Name:", project["name"])
    console.print("Manager Name:", project["manager_name"])
    console.print("Members:")
    for member in members:
        console.print("\t{user_id}. {fullname} ({username})".format(**member))


def project_details_command_alt(args, conn, cur):
    """
    Get project details using single query
    """

    sql = """
    SELECT p.project_id, p.name,
        TRIM(CONCAT(IFNULL(u.first_name, ''), ' ', IFNULL(u.last_name, '')))
            AS manager_name,
        mu.user_id,
        mu.username,
        TRIM(CONCAT(IFNULL(mu.first_name, ''), ' ', IFNULL(mu.last_name, '')))
            AS fullname
    FROM projects p
        INNER JOIN users u ON p.manager_id = u.user_id
        LEFT OUTER JOIN members m ON p.project_id = m.project_id
        LEFT OUTER JOIN users mu ON m.user_id = mu.user_id
    WHERE p.project_id = %s
    """

    console = Console()

    cur.execute(sql, (args.project_id,))
    rows = cur.fetchall()

    if len(rows) == 0:
        console.print("Project not found", style="red")
        return

    project = rows[0]

    console.print("ID:", project["project_id"])
    console.print("Project Name:", project["name"])
    console.print("Manager Name:", project["manager_name"])
    console.print("Members:")
    if project["user_id"] is None:
        console.print("\tNo members assigned to project", style="red")
    else:
        for member in rows:
            console.print("\t{user_id}. {fullname} ({username})".format(**member))


def add_task_command(args, conn, cur):
    """
    Assign task to member
    """
    sql = """
    INSERT INTO tasks
        (title, `status`, hours, started, project_id, user_id)
    VALUES
        (%s, %s, %s, %s, %s, %s)
    """
    started = None
    if args.status == PROGRESS:
        started = datetime.datetime.utcnow()

    console = Console()

    values = (
        args.title,
        args.status,
        args.time,
        started,
        args.project_id,
        args.user_id,
    )

    try:
        cur.execute(sql, values)
        conn.commit()
        console.print("Task assigned succesfully.", style="green")
    except DatabaseError as exc:
        conn.rollback()
        console.print("Could not assign task.", style="magenta")
        console.print(f"ERROR: {exc!r}", style="red")


def get_parser():
    parser = argparse.ArgumentParser("todos", description="Manage Todos")

    subparsers = parser.add_subparsers()

    register_p = subparsers.add_parser("register", description="Register users")
    register_p.add_argument("username")
    register_p.add_argument("-f", "--first")
    register_p.add_argument("-l", "--last")
    register_p.set_defaults(func=register_command)

    users_p = subparsers.add_parser("users", description="List users")
    users_p.set_defaults(func=list_users_command)

    create_p = subparsers.add_parser("create", description="Create Project")
    create_p.add_argument("name", help="Project name")
    create_p.add_argument(
        "-m",
        "--manager",
        type=int,
        required=True,
        help="ID of the user who will manage the project.",
    )
    create_p.set_defaults(func=create_project_command)

    projects_p = subparsers.add_parser("projects", description="List projects")
    projects_p.set_defaults(func=list_projects_command)

    add_member_p = subparsers.add_parser(
        "add-member", description="Add member to project"
    )
    add_member_p.add_argument(
        "-p", "--project-id", type=int, required=True, help="Project ID"
    )
    add_member_p.add_argument(
        "-u", "--user-id", type=int, required=True, help="User ID"
    )
    add_member_p.set_defaults(func=add_member_command)

    project_details_p = subparsers.add_parser(
        "project-details", description="Show project details"
    )
    project_details_p.add_argument("project_id", help="Project ID")
    # project_details_p.set_defaults(func=project_details_command)
    project_details_p.set_defaults(func=project_details_command_alt)

    add_task_p = subparsers.add_parser("add-task", description="Assign task to member.")
    add_task_p.add_argument(
        "-p", "--project-id", type=int, required=True, help="Project ID"
    )
    add_task_p.add_argument("-u", "--user-id", type=int, required=True, help="User ID")
    add_task_p.add_argument(
        "-t",
        "--time",
        type=int,
        default=1,
        help="Time required to complete task in hours",
    )
    add_task_p.add_argument(
        "-s", "--status", choices=[PENDING, PROGRESS], default=PENDING
    )
    add_task_p.add_argument("title", help="Tasks title")
    add_task_p.set_defaults(func=add_task_command)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(args=argv)

    with pymysql.connect(**DB, cursorclass=DictCursor) as conn:
        with conn.cursor() as cur:
            args.func(args, conn=conn, cur=cur)


if __name__ == "__main__":
    sys.exit(main())
