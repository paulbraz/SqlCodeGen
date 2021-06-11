import os
from table_sql_generator import TableSqlGenerator

description = 'A table of employees'
tsg = TableSqlGenerator("HR", 'dbo', 'Employee', description)
tsg.add_field_info('ID', 'int', False, True, None)
tsg.add_field_info('FirstName', 'varchar(50)', False, False, None)
tsg.add_field_info('LastName', 'varchar(50)', False, False, None)

ddl = tsg.generate_sql(include_audit_fields=True)
print(ddl)

# Write the SQL file
sql_dir = './sql'
file_name = f"{tsg.schema}.{tsg.table_name}.sql"
file_path = os.path.join(sql_dir, file_name)
print(file_path)

f = open(file_path, 'w')
f.write(ddl)
f.close()
