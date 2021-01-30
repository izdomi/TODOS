Homework
========

Implement a new command "add-task" that assigns a task to a member in a certain project.

For example:

```
$ poetry run python -m todos add-task --project-id=2 --user-id=5 --hours=4 "Add new command to todo app"
```

It will create a new task for the project with ID 2 assigned to user with id 5 that should take 4 hours.

TASKS
=====

Add tasks in project details
----------------------------

```
ID: 1
Project Name: Create DB Management Tool
Manager Name: John Lennon
Members:
    2. Paul McCartney (pmccartney)
    3. George Harrison (gharrison)
Tasks:
    1. Do smth - PENDING - George Harrison (gharrison)
```
