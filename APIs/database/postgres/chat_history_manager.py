import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import configparser
from llama_index.storage.chat_store.postgres import PostgresChatStore


class PostgreSQLDatabaseManager:
    def __init__(self, config_file):
        """
        Initializes the PostgreSQLDatabaseManager with the configuration file.
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.connection = None

    def load_config(self):
        """
        Loads the database configuration from an INI file.
        """
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            if 'postgresql' not in config:
                raise Exception("Section 'postgresql' not found in the configuration file.")
            return config['postgresql']
        except Exception as e:
            raise Exception(f"Error loading configuration file: {e}")

    def connect_to_server(self):
        """
        Establishes a connection to the PostgreSQL server using the configuration.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config.getint('port')
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print("Connected to the PostgreSQL server successfully.")
        except psycopg2.Error as e:
            raise Exception(f"Error connecting to the PostgreSQL server: {e}")

    def create_database(self, database_name):
        """
        Creates a new database on the PostgreSQL server if it does not already exist.
        """
        if not self.connection:
            raise Exception("No active connection to the PostgreSQL server.")
        try:
            with self.connection.cursor() as cursor:
                # Check if the database already exists
                cursor.execute(
                    sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [database_name]
                )
                if cursor.fetchone():
                    print(f"Database '{database_name}' already exists.")
                    return

                # Create the database if it does not exist
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
                print(f"Database '{database_name}' created successfully.")
        except psycopg2.Error as e:
            raise Exception(f"Error creating database '{database_name}': {e}")

    def close_connection(self):
        """
        Closes the connection to the PostgreSQL server.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Connection to the PostgreSQL server closed.")

    def __del__(self):
        """
        Ensures the connection is closed when the object is deleted.
        """
        self.close_connection()


class ChatStoreInitializer:
    def __init__(self, config_file, database_name):
        self.db_manager = PostgreSQLDatabaseManager(config_file=config_file)
        self.database_name = database_name

    def initialize_chat_store(self):
        """
        Ensures the chat store database exists and initializes the PostgresChatStore.
        """
        try:
            self.db_manager.connect_to_server()
            self.db_manager.create_database(self.database_name)
        except Exception as e:
            raise Exception(f"Error during chat store initialization: {e}")
        finally:
            self.db_manager.close_connection()

        # Initialize the PostgresChatStore
        uri = f"postgresql+asyncpg://{self.db_manager.config['user']}:{self.db_manager.config['password']}@{self.db_manager.config['host']}:{self.db_manager.config['port']}/{self.database_name}"
        chat_store = PostgresChatStore.from_uri(uri=uri)
        print("PostgresChatStore initialized successfully.")
        return chat_store
