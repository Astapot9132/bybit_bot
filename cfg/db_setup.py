import os

import psycopg2
import dotenv

dotenv.load_dotenv()
# создает тестовую базу данных и добавляет в нее тестового пользователя в качестве администратора
# поправьте название стандартной базы из подключения к которой будет создаваться новая
# в данный момент стандартная postgres
DB_HOST = os.getenv('POSTGRES_TEST_HOST')
DB_PORT = os.getenv('POSTGRES_TEST_PORT')
DB_NAME = os.getenv('POSTGRES_TEST_NAME')
DB_USER = os.getenv('POSTGRES_TEST_ADMIN')
DB_PASSWORD = os.getenv('POSTGRES_TEST_PASSWORD')
DB_ADMIN_DATABASE = 'postgres'
POSTGRES_LOGIN = os.getenv('POSTGRES_TEST_LOGIN')
POSTGRES_LOGIN_PASSWORD = os.getenv('POSTGRES_TEST_PASSWORD')


def add_bd():
    try:

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_ADMIN_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cur = conn.cursor()



        # Создаем БАЗУ ДАННЫХ
        try:
            cur.execute(
                f"""
                CREATE DATABASE {DB_NAME};
                """
            )
            print("База данных создана!")

        except Exception as e:
            print(e)


        cur.close()
        conn.close()

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при создании базы данных:", error)






def add_users(users: list[tuple]):
    # Привилегии для пользователей
    for user in users:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )
            conn.autocommit = True
            cur = conn.cursor()

            try:
                cur.execute(
                    f"""
                    CREATE ROLE {user[0]} WITH
                        SUPERUSER
                        CREATEDB
                        CREATEROLE
                        INHERIT
                        LOGIN
                        REPLICATION
                        BYPASSRLS
                        CONNECTION LIMIT -1
                        PASSWORD '{user[1]}';
                """
                )
                print(f"Пользователь {user[0]} создан")
            except Exception as e:
                print(e)

            cur.execute(
                f"""
                GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {user[0]};
                """
            )


            cur.execute(
                f""" GRANT ALL PRIVILEGES ON SCHEMA public TO {user[0]};
                    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {user[0]};
                    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {user[0]};
                    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO {user[0]};"""
            )

            print(f'Права выданы для пользователя {user[0]}')
            cur.close()
            conn.close()
        except Exception as e:
            print(e)

add_bd()
add_users([(POSTGRES_LOGIN, POSTGRES_LOGIN_PASSWORD)])