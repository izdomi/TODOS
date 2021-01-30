CREATE TABLE IF NOT EXISTS `users` (
  `user_id`    INT         NOT NULL AUTO_INCREMENT,
  `username`   VARCHAR(32) NOT NULL,
  `first_name` VARCHAR(64) NOT NULL,
  `last_name`  VARCHAR(64) NULL,
  CONSTRAINT pk_users_user_id PRIMARY KEY(user_id),
  CONSTRAINT uix_users_username UNIQUE(username)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `projects` (
  `project_id` INT NOT NULL AUTO_INCREMENT,
  `name`       VARCHAR(128) NOT NULL,
  `manager_id` INT NOT NULL,
  CONSTRAINT pk_projects_project_id PRIMARY KEY(project_id),
  CONSTRAINT fk_projects_manager_id FOREIGN KEY(manager_id) REFERENCES users(user_id)
             ON DELETE CASCADE ON UPDATE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `members` (
  `project_id` INT NOT NULL,
  `user_id`    INT NOT NULL,
  CONSTRAINT pk_members PRIMARY KEY(project_id, user_id),
  CONSTRAINT fk_members_project_id FOREIGN KEY(project_id) REFERENCES projects(project_id)
             ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_members_user_id FOREIGN KEY(user_id) REFERENCES users(user_id)
             ON DELETE CASCADE ON UPDATE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `tasks` (
  `task_id`    INT          NOT NULL AUTO_INCREMENT,
  `title`      VARCHAR(128) NOT NULL,
  `status`     VARCHAR(12)  NOT NULL DEFAULT 'PENDING',
  `hours`      INT          NULL,
  `started`    DATETIME     NULL,
  `finished`   DATETIME     NULL,
  `project_id` INT          NOT NULL,
  `user_id`    INT          NOT NULL,
  CONSTRAINT pk_tasks_task_id PRIMARY KEY(task_id),
  CONSTRAINT fk_tasks_project_id FOREIGN KEY(project_id) REFERENCES projects(project_id)
             ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_tasks_user_id FOREIGN KEY(user_id) REFERENCES users(user_id)
             ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT chk_tasks_status CHECK(status IN ('PENDING', 'PROGRESS', 'FINISHED'))
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
