import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id int NOT NULL ,
            Name varchar(255) NOT NULL,
            language varchar(3),
            phone  varchar(30) NULL,
            kirim int NULL,
            chiqim int NULL,
            start_count int DEFAULT 0,
            plan varchar(10) DEFAULT 'free',
            pro_token varchar(255) NULL,
            ai_usage_count int DEFAULT 0,
            PRIMARY KEY (id)
            );
        """
        self.execute(sql, commit=True)

    def create_table_kirim(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Kirim (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summa varchar(255) NOT NULL,
            izoh varchar(255) NULL,
            kategoriya varchar(255),
            user_id int NOT NULL
            
            );
        """
        self.execute(sql, commit=True)
    def create_table_chiqim(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Chiqim (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summa varchar(255) NOT NULL,
            izoh varchar(255) NULL,
            kategoriya varchar(255),
            user_id int NOT NULL
            
            );
        """
        self.execute(sql, commit=True)
    
    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, name: str, language: str = 'uz', phone: str = None, kirim: int = None, chiqim: int = None, start_count: int = 1): # pyright: ignore[reportArgumentType]
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"
        
        sql = """
        INSERT INTO Users(id, Name, language, phone, kirim, chiqim, start_count) VALUES(?, ?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, parameters=(id, name, language, phone, kirim, chiqim, start_count), commit=True)

    def add_chiqim(self,  summa: str, izoh: str, kategoriya: str, user_id: int ): # pyright: ignore[reportArgumentType]
            # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"
            
            sql = """
            INSERT INTO Chiqim(summa, izoh, kategoriya, user_id) VALUES(?, ?, ?, ?)
            """
            self.execute(sql, parameters=(summa, izoh, kategoriya, user_id), commit=True)

    def add_kirim(self, summa: str, izoh: str, kategoriya: str, user_id: int): # pyright: ignore[reportArgumentType]
            # SQL_EXAMPLE = "INSERT INTO Kirim(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"
            
            sql = """
            INSERT INTO Kirim(summa, izoh, kategoriya, user_id) VALUES(?, ?, ?, ?)
            """
            self.execute(sql, parameters=(summa, izoh, kategoriya, user_id), commit=True)

    def recreate_kirim_table(self):
        """
        Drop and recreate the Kirim table with correct schema
        """
        # Drop existing table
        self.execute("DROP TABLE IF EXISTS Kirim", commit=True)
        
        # Create new table with correct schema
        self.create_table_kirim()

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def update_user_phone(self, phone, id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET phone=? WHERE id=?
        """
        return self.execute(sql, parameters=(phone, id), commit=True)

    def update_user_start_count(self, user_id: int):
        """
        Increment the start count for a user
        """
        sql = """
        UPDATE Users SET start_count = start_count + 1 WHERE id = ?
        """
        return self.execute(sql, parameters=(user_id,), commit=True)

    def get_user_start_count(self, user_id: int):
        """
        Get the current start count for a user
        """
        sql = """
        SELECT start_count FROM Users WHERE id = ?
        """
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else 0

    def get_user_ai_usage_count(self, user_id: int):
        """
        Get user's AI usage count
        """
        sql = """
        SELECT ai_usage_count FROM Users WHERE id = ?
        """
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else 0

    def increment_ai_usage_count(self, user_id: int):
        """
        Increment user's AI usage count
        """
        sql = """
        UPDATE Users SET ai_usage_count = ai_usage_count + 1 WHERE id = ?
        """
        return self.execute(sql, parameters=(user_id,), commit=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def get_user_chiqim(self, user_id: int):
        """
        Get all expenses for a specific user
        """
        sql = """
        SELECT * FROM Chiqim WHERE user_id = ? ORDER BY id DESC LIMIT 10
        """
        return self.execute(sql, parameters=(user_id,), fetchall=True)

    def get_user_kirim(self, user_id: int):
        """
        Get all income for a specific user
        """
        sql = """
        SELECT * FROM Kirim WHERE user_id = ? ORDER BY id DESC LIMIT 10
        """
        return self.execute(sql, parameters=(user_id,), fetchall=True)

    def get_latest_chiqim(self, user_id: int):
        """
        Get the latest expense for a specific user
        """
        sql = """
        SELECT * FROM Chiqim WHERE user_id = ? ORDER BY id DESC LIMIT 1
        """
        return self.execute(sql, parameters=(user_id,), fetchone=True)

    def get_latest_kirim(self, user_id: int):
        """
        Get the latest income for a specific user
        """
        sql = """
        SELECT * FROM Kirim WHERE user_id = ? ORDER BY id DESC LIMIT 1
        """
        return self.execute(sql, parameters=(user_id,), fetchone=True)

    def add_start_count_column(self):
        """
        Add start_count column to existing Users table if it doesn't exist
        """
        try:
            sql = """
            ALTER TABLE Users ADD COLUMN start_count int DEFAULT 0
            """
            self.execute(sql, commit=True)
            print("start_count column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("start_count column already exists")
            else:
                print(f"Error adding start_count column: {e}")

    def add_plan_columns(self):
        """
        Add plan and pro_token columns to existing Users table if they don't exist
        """
        try:
            sql = """
            ALTER TABLE Users ADD COLUMN plan varchar(10) DEFAULT 'free'
            """
            self.execute(sql, commit=True)
            print("plan column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("plan column already exists")
            else:
                print(f"Error adding plan column: {e}")
        
        try:
            sql = """
            ALTER TABLE Users ADD COLUMN pro_token varchar(255) NULL
            """
            self.execute(sql, commit=True)
            print("pro_token column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("pro_token column already exists")
            else:
                print(f"Error adding pro_token column: {e}")

    def update_user_plan(self, user_id: int, plan: str, pro_token: str = None):
        """
        Update user's plan and pro token
        """
        sql = """
        UPDATE Users SET plan = ?, pro_token = ? WHERE id = ?
        """
        return self.execute(sql, parameters=(plan, pro_token, user_id), commit=True)

    def get_user_plan(self, user_id: int):
        """
        Get user's current plan
        """
        sql = """
        SELECT plan, pro_token FROM Users WHERE id = ?
        """
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        if result:
            return result[0], result[1]  # plan, pro_token
        return 'free', None

    def create_table_tokens(self):
        """
        Create table for managing pro tokens
        """
        sql = """
        CREATE TABLE IF NOT EXISTS ProTokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token varchar(255) NOT NULL UNIQUE,
            is_used BOOLEAN DEFAULT FALSE,
            used_by int NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_at TIMESTAMP NULL
        );
        """
        self.execute(sql, commit=True)

    def add_pro_token(self, token: str, created_by: int = None):
        """
        Add a new pro token to the system
        """
        sql = """
        INSERT INTO ProTokens(token, created_by) VALUES(?, ?)
        """
        try:
            self.execute(sql, parameters=(token, created_by), commit=True)
            return True
        except Exception as e:
            print(f"Error adding pro token: {e}")
            return False

    def validate_pro_token(self, token: str):
        """
        Validate and mark a pro token as used
        """
        # Check if token exists and is not used
        sql = """
        SELECT id FROM ProTokens WHERE token = ? AND is_used = FALSE
        """
        result = self.execute(sql, parameters=(token,), fetchone=True)
        
        if result:
            # Mark token as used
            sql = """
            UPDATE ProTokens SET is_used = TRUE, used_at = CURRENT_TIMESTAMP WHERE token = ?
            """
            self.execute(sql, parameters=(token,), commit=True)
            return True
        return False

    def add_admin_columns(self):
        """
        Add admin column to existing Users table if it doesn't exist
        """
        try:
            sql = """
            ALTER TABLE Users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
            """
            self.execute(sql, commit=True)
            print("is_admin column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("is_admin column already exists")
            else:
                print(f"Error adding is_admin column: {e}")

    def add_ai_usage_column(self):
        """
        Add AI usage count column to existing Users table if it doesn't exist
        """
        try:
            sql = """
            ALTER TABLE Users ADD COLUMN ai_usage_count int DEFAULT 0
            """
            self.execute(sql, commit=True)
            print("ai_usage_count column added successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ai_usage_count column already exists")
            else:
                print(f"Error adding ai_usage_count column: {e}")

    def add_pro_token_created_by_column(self):
        """
        Add created_by column to existing ProTokens table if it doesn't exist
        """
        try:
            sql = """
            ALTER TABLE ProTokens ADD COLUMN created_by int NULL
            """
            self.execute(sql, commit=True)
            print("created_by column added to ProTokens successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("created_by column already exists in ProTokens")
            else:
                print(f"Error adding created_by column to ProTokens: {e}")

    def add_pro_token_is_active_column(self):
        """
        Add is_active column to existing ProTokens table if it doesn't exist
        """
        try:
            sql = """
            ALTER TABLE ProTokens ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """
            self.execute(sql, commit=True)
            print("is_active column added to ProTokens successfully")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("is_active column already exists in ProTokens")
            else:
                print(f"Error adding is_active column to ProTokens: {e}")

    def create_admin_table(self):
        """
        Create table for managing admins
        """
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id int NOT NULL UNIQUE,
            username varchar(255) NULL,
            added_by int NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        );
        """
        self.execute(sql, commit=True)

    def create_admin_tokens_table(self):
        """
        Create table for managing admin tokens
        """
        sql = """
        CREATE TABLE IF NOT EXISTS AdminTokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token varchar(255) NOT NULL UNIQUE,
            created_by int NOT NULL,
            used_by int NULL,
            used_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """
        self.execute(sql, commit=True)

    def add_admin(self, user_id: int, added_by: int = None, username: str = None):
        """
        Add a user as admin
        """
        try:
            # Add to Admins table
            sql = """
            INSERT INTO Admins(user_id, added_by, username) VALUES(?, ?, ?)
            """
            self.execute(sql, parameters=(user_id, added_by, username), commit=True)
            
            # Update Users table
            sql = """
            UPDATE Users SET is_admin = TRUE WHERE id = ?
            """
            self.execute(sql, parameters=(user_id,), commit=True)
            return True
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False

    def remove_admin(self, user_id: int):
        """
        Remove admin privileges from user
        """
        try:
            # Remove from Admins table
            sql = """
            DELETE FROM Admins WHERE user_id = ?
            """
            self.execute(sql, parameters=(user_id,), commit=True)
            
            # Update Users table
            sql = """
            UPDATE Users SET is_admin = FALSE WHERE id = ?
            """
            self.execute(sql, parameters=(user_id,), commit=True)
            return True
        except Exception as e:
            print(f"Error removing admin: {e}")
            return False

    def is_admin(self, user_id: int):
        """
        Check if user is admin
        """
        sql = """
        SELECT is_admin FROM Users WHERE id = ?
        """
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else False

    def get_all_admins(self):
        """
        Get all admins
        """
        sql = """
        SELECT u.id, u.Name, a.username, a.created_at 
        FROM Users u 
        JOIN Admins a ON u.id = a.user_id 
        WHERE u.is_admin = TRUE
        ORDER BY a.created_at DESC
        """
        return self.execute(sql, fetchall=True)

    def add_admin_token(self, token: str, created_by: int):
        """
        Add a new admin token
        """
        sql = """
        INSERT INTO AdminTokens (token, created_by) VALUES (?, ?)
        """
        return self.execute(sql, parameters=(token, created_by), commit=True)

    def validate_admin_token(self, token: str):
        """
        Validate admin token and mark as used
        """
        sql = """
        SELECT id, created_by FROM AdminTokens 
        WHERE token = ? AND is_active = TRUE AND used_by IS NULL
        """
        result = self.execute(sql, parameters=(token,), fetchone=True)
        return result

    def use_admin_token(self, token: str, used_by: int):
        """
        Mark admin token as used
        """
        sql = """
        UPDATE AdminTokens 
        SET used_by = ?, used_at = CURRENT_TIMESTAMP, is_active = FALSE 
        WHERE token = ?
        """
        return self.execute(sql, parameters=(used_by, token), commit=True)

    def get_all_admin_tokens(self):
        """
        Get all admin tokens
        """
        sql = """
        SELECT token, created_by, used_by, used_at, created_at, is_active 
        FROM AdminTokens 
        ORDER BY created_at DESC
        """
        return self.execute(sql, fetchall=True)

    def deactivate_admin_token(self, token: str):
        """
        Deactivate an admin token
        """
        sql = """
        UPDATE AdminTokens SET is_active = FALSE WHERE token = ?
        """
        return self.execute(sql, parameters=(token,), commit=True)

    def get_all_pro_tokens(self):
        """
        Get all PRO tokens
        """
        sql = """
        SELECT token, created_by, used_by, used_at, created_at, is_active 
        FROM ProTokens 
        ORDER BY created_at DESC
        """
        return self.execute(sql, fetchall=True)

    def get_all_users(self):
        """
        Get all users with their info
        """
        sql = """
        SELECT id, Name, phone, language, plan, is_admin, start_count 
        FROM Users 
        ORDER BY id DESC
        """
        return self.execute(sql, fetchall=True)

    def get_user_count(self):
        """
        Get total user count
        """
        sql = """
        SELECT COUNT(*) FROM Users
        """
        result = self.execute(sql, fetchone=True)
        return result[0] if result else 0

    def get_pro_user_count(self):
        """
        Get pro user count
        """
        sql = """
        SELECT COUNT(*) FROM Users WHERE plan = 'pro'
        """
        result = self.execute(sql, fetchone=True)
        return result[0] if result else 0

    def get_free_user_count(self):
        """
        Get free user count
        """
        sql = """
        SELECT COUNT(*) FROM Users WHERE plan = 'free'
        """
        result = self.execute(sql, fetchone=True)
        return result[0] if result else 0


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")