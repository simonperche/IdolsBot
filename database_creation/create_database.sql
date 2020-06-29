CREATE TABLE Idol (
id INT PRIMARY KEY AUTOINCREMENT,
name TEXT,
url TEXT);

CREATE TABLE Group (
id INT PRIMARY KEY AUTOINCREMENT,
name TEXT);

CREATE TABLE IdolGroup (
id_group INT,
id_idol INT,
FOREIGN KEY (id_group) REFERENCES Group(id),
FOREIGN KEY (id_idol) REFERENCES Idol(id),
PRIMARY KEY (id_group, id_idol));

CREATE TABLE Image (
url TEXT PRIMARY KEY,
id_idol INT,
FOREIGN KEY (id_idol) REFERENCES Idol(id));