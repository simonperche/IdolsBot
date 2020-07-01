"""Singleton classes representing databases.

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
            self.db = sqlite3.connect('./database.db')

    def connect(self, filename):
        self.db.close()
        self.db = sqlite3.connect(filename)

    def get_idol_ids(self, name):
        c = self.db.cursor()
        c.execute('''SELECT I.id FROM Idol AS I WHERE I.name = ? COLLATE NOCASE''', (name,))
        results = c.fetchall()
        c.close()

        ids = [r[0] for r in results]

        return ids

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
        """Return random idol id"""
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
        """Return idol information with dict {name, group, image} format"""

        c = self.db.cursor()
        c.execute('''SELECT I.name, G.name, Image.url
                     FROM Idol AS I
                     JOIN IdolGroups AS IG ON IG.id_idol = I.id
                     JOIN Groups AS G ON IG.id_groups = G.id
                     JOIN Image ON Image.id_idol = I.id
                     WHERE I.id = ?''', (id_idol,))
        idol = c.fetchall()[0]
        c.close()

        return {'name': idol[0], 'group': idol[1], 'image': idol[2]}


