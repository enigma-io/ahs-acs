import csv

from core import *


def generate_select_statement(table, old_vars, new_var, total_var):
    stmnt = "{vars} / NULLIF({total_var}, 0) as {new_var}"

    if isinstance(old_vars, list):
        old_vars = "({})".format(" + ".join(old_vars))

    stmnt_args = {
        "vars": old_vars,
        "total_var": total_var,
        "new_var": new_var
    }

    return stmnt.format(**stmnt_args)


def generate_acs_query():
    """
    Generate ACS query.
    """
    query = """
    SELECT {}.{},
    \t{}
    FROM {}
    \t{}
    """
    join_string = "INNER JOIN {} ON {}.{} = {}.{}"
    join_strings = []
    select_statements = []
    tables = []

    # build up tables + select statements
    for concept in AHS_ACS_MAPPING:
        acs = concept.get('acs')
        table_id = acs['table']
        total = acs['total']
        if table_id not in tables:
            tables.append(table_id)
        for new_var, old_vars in acs['map'].items():
            ss = generate_select_statement(table_id, old_vars, new_var, total)
            select_statements.append(ss)

    # pop the first table
    first_table = tables.pop(0)

    # generate join statements
    for table in tables:
        js = join_string.format(
            table, table, ACS_JOIN_VAR, first_table, ACS_JOIN_VAR)
        join_strings.append(js)

    # generate sql query
    q = query\
        .format(
            first_table, ACS_JOIN_VAR,
            ",\n\t".join(select_statements),
            first_table,
            "\n\t".join(join_strings)
        )

    return q


def generate_acs_csv_query():
    """
    Dump ACS query to a csv.
    """
    query = generate_acs_query()
    return "{}; COPY ({}) TO '{}' WITH CSV HEADER;"\
	.format(";".join(ACS_SETUP_QUERIES), query, ACS_FILEPATH)

if __name__ == '__main__':
    print generate_acs_csv_query()
