import os
import mysql.connector
import hashlib


class Cnn:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.cnn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

    def __del__(self):
        self.cnn.close()

    def create(self, sql: str, data):
        cursor = self.cnn.cursor(buffered=True, dictionary=True)

        if isinstance(data, list):
            cursor.executemany(sql, data)
        
        elif isinstance(data, dict):
            cursor.execute(sql, data)

        id = cursor.lastrowid
        self.cnn.commit()
        cursor.close()
        return id

    def read(self, sql: str, params: dict = {}, onlyFirstRow: bool = False):
        cursor = self.cnn.cursor(buffered=True, dictionary=True)
        cursor.execute(sql, params)
        if onlyFirstRow: 
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        cursor.close()
        return result
    
    def update(self, sql: str, mysqlParams: dict):
        cursor = self.cnn.cursor(buffered=True, dictionary=True)
        cursor.execute(sql, mysqlParams)
        affectedRows = cursor.rowcount
        self.cnn.commit()
        cursor.close()
        return affectedRows
    
    def delete(self, sql: str, params: dict = {}):
        cursor = self.cnn.cursor(buffered=True, dictionary=True)
        cursor.execute(sql, params)
        affectedRows = cursor.rowcount
        self.cnn.commit()
        cursor.close()
        return affectedRows


class SqlBuilder:
    def __init__(self, table: str):
        self.table = table

    def insert(self, data):
        if isinstance(data, dict):
            keys = list(data.keys())
        elif isinstance(data, list):
            keys = list(data[0].keys())

        values = []
        for key in keys:
            values.append(f"%({key})s")

        sql = f"INSERT INTO {self.table} ({','.join(keys)}) VALUES({','.join(values)})"
        return sql
    
    def update(self, data: dict):
        pairs = []
        for key in data:
            pairs.append(f"{key} = %({key})s")

        return f"UPDATE `{self.table}` SET {','.join(pairs)}"
    
    def delete(self):
        return f"DELETE FROM `{self.table}`"
    
    def whereCondition(self, params: list):
        result = 'WHERE'
        usedParamNames = []

        for condition in params:
            # Define param name:
            paramName = f"{condition['paramName']}"
            paramAlias = f"param_{condition['paramName']}"

            # Define logical operator:
            logicalOperator = condition['logicalOperator']
            
            # Define comparison operator:
            comparisonOperator = condition['comparisonOperator']

            # Define condition's value:
            if isinstance(condition['value'], list):
                comparisonOperator = "IN" if comparisonOperator != "NOT IN" else comparisonOperator

                # Find next:
                next = 0
                while True:
                    if not f"{paramAlias}_{next}" in usedParamNames:
                        break
                    
                    next = next + 1

                joinedValues = []
                for i in range(0, len(condition['value'])):
                    inParamName = f"{paramAlias}_{i + next}"
                    usedParamNames.append(inParamName)
                    joinedValues.append(f"%({inParamName})s")

                value = f"({','.join(joinedValues)})"

                if len(condition['value']) < 1: 
                    value = '1'
                    paramName = ''
                    paramAlias = ''
                    logicalOperator = ''
                    comparisonOperator = ''

            else: 
                value = f" %({paramAlias})s" if condition['value'] is not None else ''

            # Set logical operator:
            if not logicalOperator == None:
                result = f"{result} {logicalOperator}"

            result = f"{result} {paramName} {comparisonOperator}{value}"

        return result


class GetDao:
    def __init__(self, tableName: str, cnn: Cnn = None):
        self.table = tableName
        self.filters = []
        self.persistence = {}
        self.sqlbuilder = SqlBuilder(tableName)
        if cnn == None:
            self.cnn = Cnn(
                host=os.getenv('DBHOST'),
                port=int(os.getenv('DBPORT')),
                database=os.getenv('DBNAME'),
                user=os.getenv('DBUSER'),
                password=os.getenv('DBPASS')
            )
        else: self.cnn = cnn

    def find(self, sql: str = '', debug = False, onlyFirstRow = False):
        if not hasattr(self, 'table'):
            raise Exception(
                "You must define the operating table using 'Dao.getTable()'")

        userDefinedParams = True
        if sql == '':
            sql = f"SELECT * FROM `{self.table}`{(' '+self.sqlbuilder.whereCondition(self.filters)) if len(self.filters) > 0 else ''}"
            userDefinedParams = False

        if debug: return {'SQL':sql, 'Params': self.prepareParams(userDefinedParams)}

        queryHash = self.findQueryHash(sql)
        if not queryHash in self.persistence:
            self.persistence[queryHash] = self.cnn.read(sql, self.prepareParams(userDefinedParams), onlyFirstRow)

        result = self.persistence[queryHash]
        return result
    
    def first(self, sql: str = '', debug = False):
        return self.find(sql, debug, True)

    def insert(self, data, debug = False):
        if not hasattr(self, 'table'):
            raise Exception(
                "You must define the operating table using 'Dao.getTable(tableName:str)'")

        sql = self.sqlbuilder.insert(data)

        if debug: return {'SQL':sql, 'Data': data}

        lastId = self.cnn.create(sql, data)

        tbKeyName = self.findTableKey()
        if isinstance(data, dict):
            data[tbKeyName] = lastId
        elif isinstance(data, list):
            for obj in data:
                obj[tbKeyName] = lastId
                lastId = lastId + 1

        return data
    
    def update(self, data: dict, debug = False):
        if not hasattr(self, 'table'):
            raise Exception(
                "You must define the operating table using 'Dao.getTable(tableName:str)'")
        
        sql = f"{self.sqlbuilder.update(data)}{(' '+self.sqlbuilder.whereCondition(self.filters)) if len(self.filters) > 0 else ''}"

        mysqlParams = data
        mysqlParams.update(self.prepareParams())
        if debug: 
            return {'SQL':sql, 'Params': mysqlParams}

        affectedRows = self.cnn.update(sql, mysqlParams)
        return affectedRows

    def delete(self, debug = False):
        if not hasattr(self, 'table'):
            raise Exception(
                "You must define the operating table using 'Dao.getTable()'")
        
        sql = f"{self.sqlbuilder.delete()}{(' '+self.sqlbuilder.whereCondition(self.filters)) if len(self.filters) > 0 else ''}"

        if debug: return {'SQL':sql, 'Params': self.prepareParams()}

        affectedRows = self.cnn.delete(sql, self.prepareParams())
        return affectedRows

    def filter(self, paramName: str):
        self.filters.append({
            'paramName': paramName,
            'logicalOperator': None,
            'comparisonOperator': None,
            'value': None
        })

        return self
    
    def _and(self, paramName: str):
        if len(self.filters) == 0:
            raise Exception(
                "You can only call this method after calling 'filter()' first.")
        
        self.filters.append({
            'paramName': paramName,
            'logicalOperator': 'AND',
            'comparisonOperator': None,
            'value': None
        })

        return self
    
    def _or(self, paramName: str):
        if len(self.filters) == 0:
            raise Exception(
                "You can only call this method after calling 'filter()' first.")
        
        self.filters.append({
            'paramName': paramName,
            'logicalOperator': 'OR',
            'comparisonOperator': None,
            'value': None
        })

        return self

    def equalsTo(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = 'IS NULL' if value == None else '='

        return self

    def notEqualsTo(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = 'IS NOT NULL' if value == None else '!='

        return self

    def biggerThan(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = '>'

        return self

    def lessThan(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = '<'

        return self

    def biggerOrEqualsTo(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = '>='

        return self

    def lessOrEqualsTo(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = '<='

        return self

    def like(self, value):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = f"%{value}%"
        self.filters[i]['comparisonOperator'] = 'LIKE'

        return self

    def _in(self, value: list):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = 'IN'

        return self

    def _notIn(self, value: list):
        i = len(self.filters)
        if i == 0 or self.filters[i - 1]['value'] != None:
            raise Exception("This method can only be called right after one of the filtering methods.")
        
        i = i - 1

        self.filters[i]['value'] = value
        self.filters[i]['comparisonOperator'] = 'NOT IN'

        return self
    
    def prepareParams(self, userDefinedParams: bool = False):
        params = {}
        for condition in self.filters:
            if isinstance(condition['value'], list):
                # Find next:
                next = 0
                while True:
                    if not f"{'param_' if not userDefinedParams else '' }{condition['paramName']}_{next}" in params:
                        break
                    
                    next = next + 1

                for i in range(0, len(condition['value'])):
                    val = condition['value'][i]
                    params[f"{'param_' if not userDefinedParams else '' }{condition['paramName']}_{i + next}"] = val

            else: params[f"{'param_' if not userDefinedParams else '' }{condition['paramName']}"] = condition['value']

        return params
    
    def findQueryHash(self, sql: str):
        result = sql.replace('param_', '')
        params = self.prepareParams()

        for key in params:
            val = params[key]
            key = key.replace('param_', '')
            if isinstance(val, list):
                for i in range(0, len(val)):
                    result = result.replace(f"%({key}_{i})s", str(val[i]))
            else:
                result = result.replace(f"%({key})s", str(val))

        result = hashlib.md5(result.encode())
        return result.hexdigest()

    def findTableKey(self):
        tbinfo = self.first(f"SHOW keys FROM {self.table}")
        return tbinfo['Column_name']
