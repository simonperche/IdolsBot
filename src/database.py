"""
Singleton classes representing databases.

These classes provide functions to access to data in idols and member database.
"""

import sqlite3


class DatabaseIdol:
    __instance = None

    @staticmethod
    def get():
        if DatabaseIdol.__instance is None:
            DatabaseIdol()
        return DatabaseIdol.__instance

    def __init__(self):
        """Virtually private constructor."""
        if DatabaseIdol.__instance is None:
            DatabaseIdol.__instance = self
            self.db = sqlite3.connect('./database_idol.db')

    def connect(self, filename):
        if self.db:
            self.db.close()
        self.db = sqlite3.connect(filename)

    def get_idol_ids(self, name):
        c = self.db.cursor()
        c.execute('''SELECT I.id FROM Idol AS I WHERE I.name = ? COLLATE NOCASE''', (name,))
        results = c.fetchall()
        c.close()

        ids = [r[0] for r in results]

        return ids

    def get_idol_group_id(self, name, group):
        """Return the idol with name and group or None otherwise."""
        c = self.db.cursor()
        c.execute('''SELECT I.id FROM Idol AS I
                     JOIN IdolGroups AS IG ON IG.id_idol = I.id 
                     JOIN Groups AS G ON IG.id_groups = G.id
                     WHERE G.name = ? COLLATE NOCASE
                     AND I.name = ? COLLATE NOCASE''', (group, name))
        id_idol = c.fetchone()
        c.close()

        return id_idol[0] if id_idol else None

    def get_group_members(self, group_name):
        c = self.db.cursor()
        c.execute('''SELECT I.name FROM Idol AS I
                     JOIN IdolGroups AS IG ON IG.id_idol = I.id 
                     JOIN Groups AS G ON IG.id_groups = G.id
                     WHERE G.name = ? COLLATE NOCASE''', (group_name,))
        results = c.fetchall()
        c.close()

        members = [r[0] for r in results]

        return members

    def get_random_idol_id(self):
        """Return random idol id."""
        c = self.db.cursor()
        c.execute('''SELECT Idol.id
                     FROM Idol
                     ORDER BY RANDOM() LIMIT 1''')
        random_idol = c.fetchall()
        c.close()

        # first [0] for the number of result (here only 1 because LIMIT)
        # second [0] for the column in result (here only 1 -> Idol.id)
        return random_idol[0][0]

    def get_idol_information(self, id_idol):
        """Return idol information with dict {name, group, image} format."""
        c = self.db.cursor()
        c.execute('''SELECT I.id, I.name, G.name, Image.url
                     FROM Idol AS I
                     JOIN IdolGroups AS IG ON IG.id_idol = I.id
                     JOIN Groups AS G ON IG.id_groups = G.id
                     JOIN Image ON Image.id_idol = I.id
                     WHERE I.id = ?''', (id_idol,))
        idol = c.fetchone()
        c.close()

        return {'id': idol[0], 'name': idol[1], 'group': idol[2], 'image': idol[3]}


class DatabaseDeck:
    __instance = None

    @staticmethod
    def get():
        if DatabaseDeck.__instance is None:
            DatabaseDeck()
        return DatabaseDeck.__instance

    def __init__(self):
        """Virtually private constructor."""
        if DatabaseDeck.__instance is None:
            DatabaseDeck.__instance = self
            self.db = sqlite3.connect('./database_deck.db')
            self.create_if_not_exist()

    def create_if_not_exist(self):
        c = self.db.cursor()
        # Query to check if the schema exists
        c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Server' ''')

        if c.fetchone()[0] != 1:
            with open('create_database_deck.sql', 'r') as f:
                print("Creating database deck schema...")
                query = f.read()

                c = self.db.cursor()
                c.executescript(query)
                self.db.commit()
                c.close()

    def connect(self, filename):
        if self.db:
            self.db.close()
        self.db = sqlite3.connect(filename)

    def add_to_deck(self, id_server, id_idol, id_member):
        self.create_server_if_not_exist(id_server)
        self.create_member_if_not_exist(id_member)
        c = self.db.cursor()
        c.execute('''INSERT INTO Deck(id_server, id_idol, id_member)
                     VALUES(?, ?, ?)''', (id_server, id_idol, id_member))
        self.db.commit()
        c.close()

        self.update_last_claim(id_server, id_member)

    def update_last_claim(self, id_server, id_member):
        c = self.db.cursor()
        c.execute('''INSERT OR IGNORE INTO MemberInformation(id_server, id_member)
                     VALUES (?, ?)''', (id_server, id_member))
        c.execute('''UPDATE MemberInformation
                     SET last_claim = datetime('now', 'localtime')
                     WHERE id_server = ? AND id_member = ?''', (id_server, id_member))
        self.db.commit()
        c.close()

    def get_server_configuration(self, id_server):
        self.create_server_if_not_exist(id_server)
        c = self.db.cursor()
        c.execute('''SELECT claim_interval, time_to_claim, rolls_per_hour FROM Server WHERE id = ?''', (id_server,))
        config = c.fetchone()
        c.close()

        return {'claim_interval': config[0], 'time_to_claim': config[1], 'rolls_per_hour': config[2]}

    def get_last_claim(self, id_server, id_member):
        """Return last claim date or -1 otherwise."""
        c = self.db.cursor()
        c.execute('''SELECT last_claim
                     FROM MemberInformation
                     WHERE id_server = ? AND id_member = ?''', (id_server, id_member))
        last_claim = c.fetchone()
        c.close()

        return last_claim[0]

    def create_server_if_not_exist(self, id_server):
        c = self.db.cursor()
        c.execute('''INSERT OR IGNORE INTO Server(id) VALUES (?)''', (id_server,))
        self.db.commit()
        c.close()

    def create_member_if_not_exist(self, id_member):
        c = self.db.cursor()
        c.execute('''INSERT OR IGNORE INTO Member(id) VALUES (?)''', (id_member,))
        self.db.commit()
        c.close()

    def create_member_information_if_not_exist(self, id_server, id_member):
        c = self.db.cursor()
        c.execute('''INSERT OR IGNORE INTO MemberInformation(id_server, id_member)
                                     VALUES (?, ?)''', (id_server, id_member))
        self.db.commit()
        c.close()

    def set_claiming_interval(self, id_server, interval):
        self.create_server_if_not_exist(id_server)
        c = self.db.cursor()
        c.execute('''UPDATE Server
                     SET claim_interval = ?
                     WHERE id = ?''', (interval, id_server))
        self.db.commit()
        c.close()

    def set_nb_rolls_per_hour(self, id_server, nb_rolls):
        self.create_server_if_not_exist(id_server)
        c = self.db.cursor()
        c.execute('''UPDATE Server
                     SET rolls_per_hour = ?
                     WHERE id = ?''', (nb_rolls, id_server))
        self.db.commit()
        c.close()

    def set_time_to_claim(self, id_server, time_to_claim):
        self.create_server_if_not_exist(id_server)
        c = self.db.cursor()
        c.execute('''UPDATE Server
                     SET time_to_claim = ?
                     WHERE id = ?''', (time_to_claim, id_server))
        self.db.commit()
        c.close()

    def get_user_deck(self, id_server, id_member):
        """Return a list of idol ids."""
        c = self.db.cursor()
        c.execute('''SELECT id_idol
                     FROM Deck
                     WHERE id_server = ? AND id_member = ?''', (id_server, id_member))
        ids = c.fetchall()
        c.close()
        return [id_idol[0] for id_idol in ids]

    def get_last_roll(self, id_server, id_member):
        """Return last roll date or None otherwise."""
        c = self.db.cursor()
        c.execute('''SELECT last_roll
                     FROM MemberInformation
                     WHERE id_server = ? AND id_member = ?''', (id_server, id_member))
        last_roll = c.fetchone()
        c.close()

        if not last_roll:
            return None

        return last_roll[0]

    def update_last_roll(self, id_server, id_member):
        c = self.db.cursor()
        self.create_member_information_if_not_exist(id_server, id_member)
        c.execute('''UPDATE MemberInformation
                     SET last_roll = datetime('now', 'localtime')
                     WHERE id_server = ? AND id_member = ?''', (id_server, id_member))
        self.db.commit()
        c.close()

    def get_nb_rolls(self, id_server, id_member):
        c = self.db.cursor()
        c.execute('''SELECT nb_rolls
                     FROM MemberInformation
                     WHERE id_server = ? AND id_member = ?''', (id_server, id_member))
        nb_rolls = c.fetchone()
        c.close()

        if not nb_rolls:
            return 0

        return nb_rolls[0]

    def set_nb_rolls(self, id_server, id_member, value):
        c = self.db.cursor()
        self.create_member_information_if_not_exist(id_server, id_member)
        c.execute('''UPDATE MemberInformation
                     SET nb_rolls = ?
                     WHERE id_server = ? AND id_member = ?''', (value, id_server, id_member))
        self.db.commit()
        c.close()

    def get_rolls_per_hour(self, id_server):
        self.create_server_if_not_exist(id_server)
        c = self.db.cursor()
        c.execute('''SELECT rolls_per_hour FROM Server WHERE id = ?''', (id_server,))
        rolls_per_hour = c.fetchone()
        c.close()

        return rolls_per_hour[0]

    def get_time_to_claim(self, id_server):
        self.create_server_if_not_exist(id_server)
        c = self.db.cursor()
        c.execute('''SELECT time_to_claim FROM Server WHERE id = ?''', (id_server,))
        time_to_claim = c.fetchone()
        c.close()

        return time_to_claim[0]
