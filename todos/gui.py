import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtSql import QSqlDatabase, QSqlQuery


SQL_PROJECTS = """
SELECT p.project_id, p.name,
    TRIM(CONCAT(IFNULL(u.first_name, ''), ' ', IFNULL(u.last_name, '')))
        AS manager_name
FROM projects p INNER JOIN users u ON p.manager_id = u.user_id
ORDER BY u.user_id, p.project_id
"""


class AppMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Todo Management")
        self.resize(640, 480)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Project", "Manager"])

        query = QSqlQuery(SQL_PROJECTS)
        query.exec_()
        project_id, project_name, project_manager = range(3)
        while query.next():
            rc = self.table.rowCount()
            self.table.setRowCount(rc + 1)

            self.table.setItem(
                rc, project_id, QTableWidgetItem(str(query.value(project_id)))
            )
            self.table.setItem(
                rc, project_name, QTableWidgetItem(query.value(project_name))
            )
            self.table.setItem(
                rc, project_manager, QTableWidgetItem(query.value(project_manager))
            )

        self.table.resizeColumnsToContents()
        self.setCentralWidget(self.table)


def create_db_connection():
    conn = QSqlDatabase.addDatabase("QMYSQL")
    conn.setDatabaseName("todos")
    conn.setHostName("127.0.0.1")
    conn.setPort(3306)
    conn.setUserName("sda")
    conn.setPassword("sda")

    if not conn.open():
        QMessageBox.critical(
            None,
            "Todo - ERROR!",
            "Could not connect to the DB {}".format(conn.lastError().databaseText()),
        )
        return False
    return True


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not create_db_connection():
        sys.exit(1)

    win = AppMainWindow()
    win.show()

    sys.exit(app.exec_())
