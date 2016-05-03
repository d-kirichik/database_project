# noinspection SqlNoDataSourceInspectionForFile
CREATE TABLE `Users`(
	`id` MEDIUMINT(11) NOT NULL AUTO_INCREMENT,
	`username` VARCHAR (30),
	`about` TEXT,
	`name` VARCHAR (30),
  `email` VARCHAR (30) NOT NULL,
	`isAnonymous` BOOL NOT NULL DEFAULT False,
	PRIMARY KEY (`id`),
  UNIQUE KEY (`email`)
) ENGINE = MYISAM;


CREATE TABLE `Forums`(
	`id` MEDIUMINT(11) NOT NULL AUTO_INCREMENT,
	`name` VARCHAR (30) NOT NULL,
    `slug` VARCHAR (30) NOT NULL,
    `user` VARCHAR (30) NOT NULL,
	PRIMARY KEY (`id`),
  UNIQUE KEY (`slug`),
    UNIQUE KEY (`name`),
    CONSTRAINT FOREIGN KEY (`user`) REFERENCES `Users` (`email`) ON DELETE CASCADE
) ENGINE = MYISAM;


CREATE TABLE `Threads` (
    `id` MEDIUMINT(11) NOT NULL AUTO_INCREMENT,
    `forum` VARCHAR (30) NOT NULL,
    `title` VARCHAR (50) NOT NULL,
    `isClosed` BOOL NOT NULL DEFAULT False,
    `user` VARCHAR (30) NOT NULL,
    `date` DATETIME NOT NULL,
    `message` TEXT NOT NULL,
    `slug` VARCHAR (50) NOT NULL,
    `isDeleted` BOOL NOT NULL DEFAULT False,
    PRIMARY KEY (`id`),
    CONSTRAINT FOREIGN KEY (`forum`) REFERENCES `Forums` (`slug`) ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (`user`) REFERENCES `Users` (`email`) ON DELETE CASCADE
) ENGINE = MYISAM;

CREATE TABLE `Posts` (
	`id` MEDIUMINT(11) NOT NULL AUTO_INCREMENT,
    `date` DATETIME NOT NULL,
    `thread` MEDIUMINT(11) NOT NULL,
    `message` TEXT NOT NULL,
    `user` VARCHAR (30) NOT NULL,
    `forum` VARCHAR (30) NOT NULL,
	`parent` MEDIUMINT(11),
	`isApproved` BOOL NOT NULL DEFAULT False,
	`isHighlighted` BOOL NOT NULL DEFAULT False,
	`isEdited` BOOL NOT NULL DEFAULT False,
	`isSpam` BOOL NOT NULL DEFAULT False,
	`isDeleted` BOOL NOT NULL DEFAULT False,
	PRIMARY KEY (`id`),
    CONSTRAINT FOREIGN KEY (`forum`) REFERENCES `Forums` (`slug`) ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (`user`) REFERENCES `Users` (`email`) ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (`thread`) REFERENCES `Threads` (`id`) ON DELETE CASCADE
) ENGINE = MYISAM;

CREATE TABLE `Followers` (
    `id` MEDIUMINT(11) NOT NULL AUTO_INCREMENT,
    `follower_mail` VARCHAR (30) NOT NULL,
    `followee_mail` VARCHAR (30) NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT FOREIGN KEY (`follower_mail`) REFERENCES `Users` (`email`) ON DELETE CASCADE,
    CONSTRAINT FOREIGN KEY (`followee_mail`) REFERENCES `Users` (`email`) ON DELETE CASCADE
) ENGINE = MYISAM;