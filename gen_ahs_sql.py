import copy
import csv

from core import *

# null values in the AHS
NULL_CAT_VALUES = "('-6', '-7', '-8', '-9', 'B')"
NULL_NUM_VALUES = "(-6, -7, -8, -9)"

# mapping of ahs => acs variables


def categorical_when_clause(orig_var, values):
    """
    Generate a when clause to merge one or more
    categories.
    """
    stmnt = "{orig_var}::text = '{value}'"
    # standardize list
    if not isinstance(values, list):
        values = [values]
    clauses = []
    for value in values:
        clause_kwargs = {
            'orig_var': orig_var,
            'value': value
        }
        clauses.append(stmnt.format(**clause_kwargs))

    return " OR ".join(clauses)


def continous_when_clause(orig_var, values):
    """
    Generate a when clause to generate a binary indicator
    for a continuous variables which falls within a given range.
    """
    range_stmnt = "{orig_var} >= {v1} AND {orig_var} <= {v2}"
    val_stmtnt = "{orig_var} = {v1}"

    # standardize list
    if not isinstance(values, list):
        values = [values]

    if len(values) == 1:
        return val_stmtnt.format(orig_var=orig_var, v1=values[0])
    elif len(values) == 2:
        return range_stmnt.format(orig_var=orig_var, v1=values[0], v2=values[1])


def case_statement(orig_var, new_var, type, values):
    """
    Generate a case statment to turn categorical variables
    in the AHS into binary indicators.
    """
    stmnt =\
        """
    CASE
        WHEN {when_clause} THEN '1'
        WHEN {null_clause}
        ELSE {orig_var}
    END AS {new_var}
    """
    if type == 'categorical':
        when_clause = categorical_when_clause(orig_var, values)
        null_clause = "{orig_var}::text NOT IN {null_values} THEN '0'"\
            .format(orig_var=orig_var, null_values=NULL_CAT_VALUES)
    elif type == 'continuous':
        when_clause = continous_when_clause(orig_var, values)
        null_clause = "{orig_var} NOT IN {null_values} THEN '0'"\
            .format(orig_var=orig_var, null_values=NULL_NUM_VALUES)
    else:
        raise ValueError('type must be "categorical" or "continuous"')

    stmt_kwargs = {
        'orig_var': orig_var,
        'new_var': new_var,
        'when_clause': when_clause,
        'null_clause': null_clause
    }
    return stmnt.format(**stmt_kwargs)


def generate_ahs_query():
    """
    Generate AHS query.
    """
    query =\
        """
        SELECT
            {0},
            {1}
        FROM ahs.tnewhouse
        """

    stmnts = []
    for concept in AHS_ACS_MAPPING:
        orig_var = concept['ahs']['var']
        type = concept['ahs']['type']
        for new_var, values in concept['ahs']['map'].items():
            stmnt = case_statement(orig_var, new_var, type, values)
            stmnts.append(stmnt)

    q = query.format("\n,".join(AHS_ADD_VARS), ",\n".join(stmnts))
    return q


def generate_ahs_csv_query():
    query = generate_ahs_query()
    return "COPY ({}) TO '{}' WITH CSV HEADER;".format(query, AHS_FILEPATH)

if __name__ == '__main__':
    print generate_ahs_csv_query()
