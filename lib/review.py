from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError('Year must be more than 2000 and an integer.')

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value
        else:
            raise ValueError('Summary shouldn\'t be an empty string')

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        sql = 'SELECT id FROM employees WHERE id = ?;'
        CURSOR.execute(sql, (value,))
        row = CURSOR.fetchone()
        if row:
            self._employee_id = value
        else:
            raise ValueError('Employee id must exist in the employees table')

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of the new row.
        Save the object in the local dictionary using the table row's PK as dictionary key"""
        if self.id is None:
            sql = 'INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?);'
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            CONN.commit()
            Review.all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        return cls(id=row[0], year=row[1], summary=row[2], employee_id=row[3])

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to its db row retrieved by id."""
       
        row = CURSOR.execute('SELECT * FROM reviews WHERE id = ?', (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = 'UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?;'
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute."""
        sql = 'DELETE FROM reviews WHERE id = ?;'
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        if self.id in Review.all:
            del Review.all[self.id]

        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = 'SELECT * FROM reviews;'
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        reviews = []
        for row in rows:
            reviews.append(cls.instance_from_db(row))
        return reviews
