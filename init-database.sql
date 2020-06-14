CREATE TABLE server (
	  discord_server_id BIGINT PRIMARY KEY
);

CREATE TABLE meeting (
    id INT PRIMARY KEY AUTO_INCREMENT,
    discord_server_id BIGINT NOT NULL,
    book TEXT,
    pages INT,
    meeting_date DATE
);
