import sys
import os

import sqlite3


def main():
    connection = sqlite3.connect('database_orig.db')
    connection_new = sqlite3.connect('database_new.db')

    c_new = connection_new.cursor()
    c = connection.cursor()

    c_new.execute('''SELECT url
                     FROM Idol''')
    res = c_new.fetchall()

    urls = [url[0] for url in res]

    for url in urls:
        c.execute('''SELECT url FROM Idol WHERE url = ?''', (url,))
        old_url = c.fetchone()

        if old_url:  # Existing idol
            # Only update url of images
            old_url = old_url[0]
            c.execute(''' SELECT id FROM Idol WHERE url = ? ''', (old_url,))
            id_old_idol = c.fetchone()[0]
            c.execute('''DELETE FROM Image
                         WHERE id_idol = ? ''', (id_old_idol,))

            c_new.execute(''' SELECT I.url 
                              FROM Image AS I
                              JOIN Idol ON Idol.id = I.id_idol
                              WHERE Idol.url = ? ''', (url,))
            res = c_new.fetchall()
            image_urls = [g[0] for g in res]
            for img_url in image_urls:
                c.execute(''' INSERT OR IGNORE INTO Image(url, id_idol) VALUES (?, ?) ''', (img_url, id_old_idol,))
        else:  # New idol
            c_new.execute(''' SELECT id, name FROM Idol WHERE url = ? ''', (url,))
            id_idol, name = c_new.fetchone()

            c_new.execute(''' SELECT G.name 
                              FROM Groups AS G 
                              JOIN IdolGroups AS IG ON IG.id_groups = G.id
                              WHERE IG.id_idol = ? ''', (id_idol,))
            res = c_new.fetchall()
            name_groups = [g[0] for g in res]

            c.execute(''' INSERT INTO Idol(name, url) VALUES (?, ?) ''',
                      (name, url,))

            c.execute(''' SELECT id FROM Idol WHERE url = ? ''', (url,))
            id_old_idol = c.fetchone()[0]

            for group in name_groups:
                c.execute(''' INSERT OR IGNORE INTO Groups(name) VALUES (?) ''', (group,))
                c.execute(''' SELECT id FROM Groups WHERE name = ? ''', (group,))
                id_old_group = c.fetchone()[0]

                c.execute(''' INSERT INTO IdolGroups(id_idol, id_groups) VALUES (?, ?) ''',
                          (id_old_idol, id_old_group,))

            # Images
            c_new.execute(''' SELECT url 
                              FROM Image
                              WHERE id_idol = ? ''', (id_idol,))
            res = c_new.fetchall()
            image_urls = [g[0] for g in res]
            for img_url in image_urls:
                c.execute(''' INSERT OR IGNORE INTO Image(url, id_idol) VALUES (?, ?) ''', (img_url, id_old_idol,))

        print(f'New : {url}')
        print(f'Old : {old_url}')

    c.execute('''UPDATE Deck SET current_image = 0 ''')
    c_new.close()
    connection.commit()
    c.close()


if __name__ == "__main__":
    main()
