from datetime import date
import os
from dataclasses import dataclass

@dataclass
class FieldInfo:
    field_name: str
    data_type: str
    nullable: bool
    primary_key: bool
    default_value: str

@dataclass
class ForeignKey:
    fk_schema: str
    fk_table: str
    fk_field: str
    local_field: str

fk_sql_template = """ALTER TABLE [{schema}].[{table_name}]  WITH CHECK ADD  CONSTRAINT [{fk_name}] FOREIGN KEY([{fld}])
REFERENCES [{fk_schema}].[{fk_table}] ([{fk_fld}])
GO

ALTER TABLE [{schema}].[{table_name}] CHECK CONSTRAINT [{fk_name}]
GO
"""

class TableSqlGenerator:
    
    def __init__(self, database, schema, table_name, description):
        self.database = database
        self.schema = schema
        self.table_name = table_name
        self.description = description
        self.__field_info_lst = []
        self.__audit_flds = []
        self.__foreign_keys = []
        
        template_file = './templates/create_table_template2.txt'
        f = open(template_file)
        self.table_template = f.read()
        f.close()
        
        # create audit fields
        self.__audit_flds.append(FieldInfo('CreatedDate', 'datetime', False, False, 'getdate()'))
        self.__audit_flds.append(FieldInfo('CreatedBy', 'varchar(30)', False, False, 'suser_name()'))
        self.__audit_flds.append(FieldInfo('LastUpdatedDate', 'datetime', False, False, 'getdate()'))
        self.__audit_flds.append(FieldInfo('LastUpdatedBy', 'varchar(30)', False, False, 'suser_name()'))
    
    def add_field_info(self, field_name,
                       data_type='varchar(100)', 
                       nullable=False,
                       primary_key=False,
                       default_value=None):
        fi = FieldInfo(field_name, data_type, nullable, primary_key, default_value)
        self.__field_info_lst.append(fi)
        
    def add_foreign_key(self, fk_schema, fk_table, fk_field, local_field):
        fk = ForeignKey(fk_schema, fk_table, fk_field, local_field)
        self.__foreign_keys.append(fk)

    def primary_key_fields(self):
        return [f for f in self.__field_info_lst if f.primary_key]
    
    def sql_field_defs(self, include_audit_fields=False):
        fld_defs = self.__field_info_lst
        if include_audit_fields:
            fld_defs += self.__audit_flds
        sql_fld_defs_sql = [f"[{f.field_name}] {f.data_type} {'' if f.nullable else 'NOT '}NULL {'' if f.default_value is None else 'DEFAULT ' + f.default_value}"\
                            for f in fld_defs]
        sql_fld_defs_sql = '\n\t,'.join(sql_fld_defs_sql)
        return sql_fld_defs_sql
    
    def sql_primary_key_fields(self):
        pk_flds_sql = [f"[{f.field_name}] ASC" for f in self.__field_info_lst if f.primary_key]
        pk_flds_sql = "\n\t,".join(pk_flds_sql)
        return pk_flds_sql
    
    def sql_foreign_keys(self):
        fk_sql = ''

        params = {'schema': self.schema, 
                  'table_name': self.table_name}

        for fk in self.__foreign_keys:
            params['fld'] = fk.local_field
            params['fk_name'] = f"FK_{self.table_name}_{fk.fk_table}"
            params['fk_schema'] = fk.fk_schema
            params['fk_table'] = fk.fk_table 
            params['fk_fld'] = fk.fk_field
            fk_sql += fk_sql_template.format(**params)
    
        return fk_sql
    
    def generate_sql(self, include_audit_fields = False):
        params = {
            'todays_date': date.today(),
            'database': self.database,
            'description': self.description,
            'schema': self.schema,
            'table_name': self.table_name,
            'sql_fld_defs': self.sql_field_defs(include_audit_fields),
            'pk_flds': self.sql_primary_key_fields(),
            'foreign_keys': self.sql_foreign_keys(),
            'default_values': ''
        }

        ddl = self.table_template.format(**params)
        return ddl
