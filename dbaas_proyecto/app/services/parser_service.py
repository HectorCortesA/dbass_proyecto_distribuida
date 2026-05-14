# app/services/parser_service.py

from app.services.database_service import (
    create_database,
    list_databases,
    delete_database
)

from app.services.table_service import (
    create_table,
    list_tables,
    delete_table
)

from app.services.crud_service import (
    insert_data,
    find_data,
    update_data,
    delete_data
)


def parse_key_values(values):

    data = {}

    for item in values:

        if "=" in item:

            key, value = item.split("=")

            data[key] = value

    return data


def execute_command(user_id: str, command: str):

    parts = command.split()

    if len(parts) == 0:

        return {
            "error": "Comando vacío"
        }

    action = parts[0]

    # DATABASES

    if action == "creardb":

        db_name = parts[1]

        return create_database(
            user_id,
            db_name
        )

    elif action == "listardb":

        return list_databases(user_id)

    elif action == "eliminardb":

        db_name = parts[1]

        return delete_database(
            user_id,
            db_name
        )

    # TABLES

    elif action == "creartable":

        db_name = parts[1]

        table_name = parts[2]

        return create_table(
            user_id,
            db_name,
            table_name
        )

    elif action == "listartables":

        db_name = parts[1]

        return list_tables(
            user_id,
            db_name
        )

    elif action == "eliminartable":

        db_name = parts[1]

        table_name = parts[2]

        return delete_table(
            user_id,
            db_name,
            table_name
        )

    # CRUD

    elif action == "insertardatos":

        db_name = parts[1]

        table_name = parts[2]

        data = parse_key_values(parts[3:])

        return insert_data(
            user_id,
            db_name,
            table_name,
            data
        )

    elif action == "buscar":

        db_name = parts[1]

        table_name = parts[2]

        filters = parse_key_values(parts[3:])

        return find_data(
            user_id,
            db_name,
            table_name,
            filters
        )

    elif action == "actualizar":

        db_name = parts[1]

        table_name = parts[2]

        document_id = parts[3]

        data = parse_key_values(parts[4:])

        return update_data(
            user_id,
            db_name,
            table_name,
            document_id,
            data
        )

    elif action == "eliminar":

        db_name = parts[1]

        table_name = parts[2]

        document_id = parts[3]

        return delete_data(
            user_id,
            db_name,
            table_name,
            document_id
        )

    else:

        return {
            "error": "Comando no reconocido"
        }