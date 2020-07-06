CREATE TABLE Server (
id INT PRIMARY KEY
);

CREATE TABLE Idol (
id INT PRIMARY KEY
);

CREATE TABLE Member (
id INT PRIMARY KEY
);

CREATE TABLE Deck (
id_server INT,
id_idol INT,
id_member INT,
FOREIGN KEY (id_server) REFERENCES Server(id),
FOREIGN KEY (id_idol) REFERENCES Idol(id),
FOREIGN KEY (id_member) REFERENCES Member(id),
PRIMARY KEY (id_server, id_idol)
);

CREATE TABLE Wishlist (
id_server INT,
id_idol INT,
id_member INT,
FOREIGN KEY (id_server) REFERENCES Server(id),
FOREIGN KEY (id_idol) REFERENCES Idol(id),
FOREIGN KEY (id_member) REFERENCES Member(id),
PRIMARY KEY (id_server, id_idol, id_member)
)