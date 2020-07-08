CREATE TABLE ActiveImage(
id_server INT,
id_idol INT,
current_image INT,
FOREIGN KEY (id_server) REFERENCES Server(id),
PRIMARY KEY(id_server, id_idol)
)