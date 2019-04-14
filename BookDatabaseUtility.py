"""
:mod: 'BookDatabaseUtility'
~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:module:: BookDatabaseUtility
    :copyright: Copyright BitWorks LLC, All rights reserved.
    :license: MIT
    :synopsis: SQLAlchemy ORM engine, metadata, and utility functions for working with dynamic sqlite databases
    :description: Contains the following functions:

        makeEntityTable - creates table 'entities' - columns = entity_cik, parent_cik, entity_name
        makeFilingsTable - creates table 'filings####' - columns = entity_cik, q1, q2, q3, q4
        getAllTables - returns a list of all SQLAlchemy Table objects
        tableExists - determines whether a given table name exists in the database
        getEntityTreeInfo - returns list of tuples, where each tuple is a row [(entity_cik, parent_cik, entity_name)]
        getNameFromCik - uses a given cik to get an entity_name from the database
        updateEntityParent - updates the parent cik of a given child cik; used when user alters entity tree view hierarchy
        getEntityDict - returns a dict of the format {entity_name:entity_cik}, for all entities in database
        getFilingTreeInfo - returns list of strings, where each string corresponds to a filing available for viewing
        selectFromDatabase - given a cik and filing period, selects a Filing object from the database
        existsInDatabase - determines whether a given filing exists in the database
        manualExistsInDatabase - determines whether a given filing exists in the database, with input from user
        addToEntitiesTable - updates 'entities' table to include a given entity, if not present
        addToFilingsTable - updates a 'filings####' table to include a given filing, if not present
        addToDatabase - adds a given fact file to the database in the form of a pickled Filing object
        manualAddToDatabase - adds a given fact file to the database in the form of a pickled Filing object, with input from user
        countEntityAndChildren - determines the breadth and depth of an entity tree in the database, used for status bar updates
        removeEntityFromDatabase - removes a given entity (and all its children) from the database; currently an expensive function
        removeFilingFromDatabase - removes a given filing item (and all its children) from the database; currently also expensive
        updateEntityName - updates the name of an entity to that disclosed in the latest available filing
        getLastFiling - returns the latest filing for a particular entity
        renameEntityInDatabase(target_cik, new_entity_name) - manual replacement of the entity name with new_entity_name in the database
"""

try:
    import pickle, sys, os, datetime, logging
    database_utility_logger = logging.getLogger()
    from sqlalchemy import (create_engine, Table, Column, Integer, String, PickleType)
    from sqlalchemy.schema import MetaData
    from sqlalchemy.pool import NullPool
    # Tiered
    # from . import (BookFilingUtility)
    # Flat
    import BookFilingUtility
except Exception as err:
    database_utility_logger.error("{0}:BookDatabaseUtility import error:{1}".format(str(datetime.datetime.now()), str(err)))

def buildEngine(db_uri):
    try:
        global Engine
        global Global_metadata
        Engine = create_engine(os.path.join("sqlite:///{0}".format(db_uri)), poolclass = NullPool, echo = False)
        Global_metadata = MetaData(bind = Engine, reflect = True)
    except Exception as err:
        database_utility_logger.error("{0}:buildEngine():{1}".format(str(datetime.datetime.now()), str(err)))

def makeEntityTable():
    try:
        global Global_metadata
        ent = Table(
            "entities",
            Global_metadata,
            Column("entity_cik", Integer, primary_key = True),
            Column("parent_cik", Integer, nullable = True),
            Column("entity_name", String(60))
        )
        Global_metadata.create_all(Engine)
    except Exception as err:
        database_utility_logger.error("{0}:makeEntityTable():{1}".format(str(datetime.datetime.now()), str(err)))

    return

def makeFilingsTable(target_name):
    try:
        global Global_metadata
        fil = Table(
            target_name,
            Global_metadata,
            Column("entity_cik", Integer, primary_key = True),
            Column("q1", PickleType, nullable = True),
            Column("q2", PickleType, nullable = True),
            Column("q3", PickleType, nullable = True),
            Column("q4", PickleType, nullable = True)
        )
        Global_metadata.create_all(Engine)
    except Exception as err:
        database_utility_logger.error("{0}:makeFilingsTable():{1}".format(str(datetime.datetime.now()), str(err)))

    return

def getAllTables():
    try:
        local_metadata = MetaData(bind = Engine, reflect = True)
        tables = []

        for table in local_metadata.sorted_tables:
            tables.append(table)

        return tables
    except Exception as err:
        database_utility_logger.error("{0}:getAllTables():{1}".format(str(datetime.datetime.now()), str(err)))

def tableExists(target_table_name):
    try:
        tables = getAllTables()
        for table in tables:
            if table.name == target_table_name:
                return True
        return False
    except Exception as err:
        database_utility_logger.error("{0}:tableExists():{1}".format(str(datetime.datetime.now()), str(err)))

def getEntityTreeInfo():
    try:
        connection = Engine.connect()
        table_select = []
        entity_list = []
        tables = getAllTables()
        for table in tables:
            if table.name == "entities":
                try:
                    select_stmt = table.select()
                    table_select = connection.execute(select_stmt).fetchall()
                except Exception as err:
                    pass

        for entry in table_select:
            entity_list.append(entry)

        connection.close()

        return entity_list
    except Exception as err:
        database_utility_logger.error("{0}:getEntityTreeInfo():{1}".format(str(datetime.datetime.now()), str(err)))

def getNameFromCik(target_cik):
    try:
        connection = Engine.connect()
        entity_name = None
        tables = getAllTables()
        for table in tables:
            if table.name == "entities":
                try:
                    select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                    table_select = connection.execute(select_stmt).fetchall()
                    entity_name = table_select[0][2]
                except Exception as err:
                    pass
        connection.close()

        return entity_name
    except Exception as err:
        database_utility_logger.error("{0}:getNameFromCik():{1}".format(str(datetime.datetime.now()), str(err)))

def updateEntityParent(target_child_cik, target_parent_cik):
    try:
        target_child_cik = int(target_child_cik)
    except Exception as err:
        pass
    try:
        target_parent_cik = int(target_parent_cik)
    except Exception as err:
        pass
    try:
        connection = Engine.connect()

        tables = getAllTables()
        for table in tables:
            if table.name == "entities":
                try:
                    update_stmt = table.update().where(table.columns.entity_cik == target_child_cik).values(parent_cik = target_parent_cik)
                    table_update = connection.execute(update_stmt)
                except Exception as err:
                    pass

        connection.close()

        try:
            if table_update.last_updated_params() is not None:
                return_val = True
            else:
                return_val = False
        except Exception as err:
            return_val = False

        return return_val
    except Exception as err:
        database_utility_logger.error("{0}:updateEntityParent() body:{1}".format(str(datetime.datetime.now()), str(err)))

def getEntityDict():
    try:
        connection = Engine.connect()
        entity_dict = {} #key = entity_name, value = entity_cik
        tables = getAllTables()
        for table in tables:
            if table.name == "entities":
                try:
                    select_stmt = table.select()
                    table_select = connection.execute(select_stmt).fetchall()
                    for entry in table_select:
                        try:
                            entity_dict[entry[2]] = entry[0]
                        except Exception as err:
                            database_utility_logger.error("{0}:getEntityDict() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                except Exception as err:
                    database_utility_logger.error("{0}:getEntityDict() middle:{1}".format(str(datetime.datetime.now()), str(err)))
        connection.close()

        return entity_dict
    except Exception as err:
        database_utility_logger.error("{0}:getEntityDict() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def getFilingTreeInfo(target_cik):
    try:
        target_cik = int(target_cik)
        connection = Engine.connect()
        filings = []
        tables = getAllTables()
        for table in tables:
            if table.name.startswith("filings"):
                try:
                    select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                    table_select = connection.execute(select_stmt).fetchall()
                    if len(table_select) > 0:
                        if table_select[0][1] is not None:
                            filings.append(table.name[-4:] + "-Q1")
                        if table_select[0][2] is not None:
                            filings.append(table.name[-4:] + "-Q2")
                        if table_select[0][3] is not None:
                            filings.append(table.name[-4:] + "-Q3")
                        if table_select[0][4] is not None:
                            filings.append(table.name[-4:] + "-Q4")
                except Exception as err:
                    database_utility_logger.error("{0}:getFilingTreeInfo() inner:{1}".format(str(datetime.datetime.now()), str(err)))
        connection.close()

        return filings
    except Exception as err:
        database_utility_logger.error("{0}:getFilingTreeInfo() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def selectFromDatabase(target_cik, target_period):
    try:
        connection = Engine.connect()
        target_cik = int(target_cik)
        tables = getAllTables()
        select_result = None
        for table in tables:
            if table.name == "filings{0}".format(target_period[2:6]):
                if target_period[0:2] == "q1":
                    try:
                        select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                        select_result = connection.execute(select_stmt).first() #SA RowProxy
                        if select_result is not None:
                            try:
                                if select_result.items()[1][1] is not None:
                                    select_result = pickle.loads(select_result.items()[1][1]) #1st: col #; 2nd: 0 = key, 1 = val
                                else:
                                    select_result = None
                            except Exception as err:
                                database_utility_logger.error("{0}:selectFromDatabase() q1 inner:{1}".format(str(datetime.datetime.now()), str(err)))
                                select_result = None
                    except Exception as err:
                        database_utility_logger.error("{0}:selectFromDatabase() q1 outer:{1}".format(str(datetime.datetime.now()), str(err)))
                        select_result = None
                elif target_period[0:2] == "q2":
                    try:
                        select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                        select_result = connection.execute(select_stmt).first()
                        if select_result is not None:
                            try:
                                if select_result.items()[2][1] is not None:
                                    select_result = pickle.loads(select_result.items()[2][1])
                                else:
                                    select_result = None
                            except Exception as err:
                                database_utility_logger.error("{0}:selectFromDatabase() q2 inner:{1}".format(str(datetime.datetime.now()), str(err)))
                                select_result = None
                    except Exception as err:
                        database_utility_logger.error("{0}:selectFromDatabase() q2 outer:{1}".format(str(datetime.datetime.now()), str(err)))
                        select_result = None
                elif target_period[0:2] == "q3":
                    try:
                        select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                        select_result = connection.execute(select_stmt).first()
                        if select_result is not None:
                            try:
                                if select_result.items()[3][1] is not None:
                                    select_result = pickle.loads(select_result.items()[3][1])
                                else:
                                    select_result = None
                            except Exception as err:
                                database_utility_logger.error("{0}:selectFromDatabase() q3 inner:{1}".format(str(datetime.datetime.now()), str(err)))
                                select_result = None
                    except Exception as err:
                        database_utility_logger.error("{0}:selectFromDatabase() q3 outer:{1}".format(str(datetime.datetime.now()), str(err)))
                        select_result = None
                elif target_period[0:2] == "q4":
                    try:
                        select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                        select_result = connection.execute(select_stmt).first()
                        if select_result is not None:
                            try:
                                if select_result.items()[4][1] is not None:
                                    select_result = pickle.loads(select_result.items()[4][1])
                                else:
                                    select_result = None
                            except Exception as err:
                                database_utility_logger.error("{0}:selectFromDatabase() q4 inner:{1}".format(str(datetime.datetime.now()), str(err)))
                                select_result = None
                    except Exception as err:
                        database_utility_logger.error("{0}:selectFromDatabase() q4 outer:{1}".format(str(datetime.datetime.now()), str(err)))
                        select_result = None
                else:
                    select_result = None
        connection.close()

        return select_result
    except Exception as err:
        database_utility_logger.error("{0}:selectFromDatabase() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def existsInDatabase(target_fact_uri, target_cik = None):
    try:
        return_vals = []
        filing = BookFilingUtility.parseFactFile(target_fact_uri)
        entity_cik_list, entity_parent_cik, entity_name, filing_period = BookFilingUtility.getFilingInfo(filing)
        cell_list = []
        if target_cik is not None:
            cell = selectFromDatabase(target_cik, filing_period)
            if cell is not None:
                return_vals.append((target_cik, filing_period, cell))
        else:
            if len(entity_cik_list) >= 1:
                for entity_cik in entity_cik_list:
                    cell = selectFromDatabase(entity_cik, filing_period)
                    cell_list.append((entity_cik, filing_period, cell))
        for item in cell_list:
            if item[2] is not None:
                return_vals.append(item)

        return return_vals
    except Exception as err:
        database_utility_logger.error("{0}:existsInDatabase():{1}".format(str(datetime.datetime.now()), str(err)))

def manualExistsInDatabase(manual_cik, manual_period):
    try:
        cell = selectFromDatabase(manual_cik, manual_period)

        if cell is None:
            return False
        else:
            return True
    except Exception as err:
        database_utility_logger.error("{0}:manualExistsInDatabase():{1}".format(str(datetime.datetime.now()), str(err)))

def addToEntitiesTable(target_entity_cik, target_parent_cik, target_entity_name):
    try:
        connection = Engine.connect()
        tables = getAllTables()
        present = False
        for table in tables:
            if table.name == "entities":
                try:
                    select_stmt = table.select().where(table.columns.entity_cik == target_entity_cik)
                    select_result = connection.execute(select_stmt).first()
                    if select_result is not None:
                        present = True
                    else:
                        insert_stmt = table.insert().values(entity_cik = target_entity_cik,
                                                            parent_cik = target_parent_cik,
                                                            entity_name = target_entity_name)
                        insert_result = connection.execute(insert_stmt)
                        present = True
                except Exception as err:
                    database_utility_logger.error("{0}:addToEntitiesTable() inner:{1}".format(str(datetime.datetime.now()), str(err)))
        connection.close()

        return present
    except Exception as err:
        database_utility_logger.error("{0}:addToEntitiesTable() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def addToFilingsTable(target_table_name, target_entity_cik, target_quarter, target_filing):
    try:
        target_filing = pickle.dumps(target_filing)
        connection = Engine.connect()
        tables = getAllTables()
        present = False
        for table in tables:
            if table.name == target_table_name:
                try:
                    select_stmt = table.select().where(table.columns.entity_cik == target_entity_cik)
                    select_result = connection.execute(select_stmt).first()
                except Exception as err:
                    database_utility_logger.error("{0}:addToFilingsTable() select:{1}".format(str(datetime.datetime.now()), str(err)))
                if select_result is not None:
                    if target_quarter == "q1":
                        try:
                            update_stmt = table.update().where(table.columns.entity_cik == target_entity_cik).values(q1 = target_filing)
                            update_result = connection.execute(update_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result == None q1:{1}".format(str(datetime.datetime.now()), str(err)))
                    elif target_quarter == "q2":
                        try:
                            update_stmt = table.update().where(table.columns.entity_cik == target_entity_cik).values(q2 = target_filing)
                            update_result = connection.execute(update_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result == None q2:{1}".format(str(datetime.datetime.now()), str(err)))
                    elif target_quarter == "q3":
                        try:
                            update_stmt = table.update().where(table.columns.entity_cik == target_entity_cik).values(q3 = target_filing)
                            update_result = connection.execute(update_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result == None q3:{1}".format(str(datetime.datetime.now()), str(err)))
                    elif target_quarter == "q4":
                        try:
                            update_stmt = table.update().where(table.columns.entity_cik == target_entity_cik).values(q4 = target_filing)
                            update_result = connection.execute(update_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result == None q4:{1}".format(str(datetime.datetime.now()), str(err)))
                else:
                    if target_quarter == "q1":
                        try:
                            insert_stmt = table.insert().values(entity_cik = target_entity_cik, q1 = target_filing)
                            insert_result = connection.execute(insert_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result != None q1:{1}".format(str(datetime.datetime.now()), str(err)))
                    elif target_quarter == "q2":
                        try:
                            insert_stmt = table.insert().values(entity_cik = target_entity_cik, q2 = target_filing)
                            insert_result = connection.execute(insert_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result != None q2:{1}".format(str(datetime.datetime.now()), str(err)))
                    elif target_quarter == "q3":
                        try:
                            insert_stmt = table.insert().values(entity_cik = target_entity_cik, q3 = target_filing)
                            insert_result = connection.execute(insert_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result != None q3:{1}".format(str(datetime.datetime.now()), str(err)))
                    elif target_quarter == "q4":
                        try:
                            insert_stmt = table.insert().values(entity_cik = target_entity_cik, q4 = target_filing)
                            insert_result = connection.execute(insert_stmt)
                            present = True
                        except Exception as err:
                            database_utility_logger.error("{0}:addToFilingsTable() select_result != None q4:{1}".format(str(datetime.datetime.now()), str(err)))
        connection.close

        return present
    except Exception as err:
        database_utility_logger.error("{0}:addToFilingsTable() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def addToDatabase(target_fact_uri, target_cik = None):
    try:
        filing = BookFilingUtility.parseFactFile(target_fact_uri)
        target_cik_list, target_parent_cik, target_name, filing_period = BookFilingUtility.getFilingInfo(filing)
        if target_cik is not None:
            target_cik = int(target_cik)
        else:
            if len(target_cik_list) >= 1:
                target_cik = int(target_cik_list[0])
        filing_year = filing_period[2:6]
        filing_quarter = filing_period[0:2]
        filing_table_name = "filings" + filing_year

        if target_cik == None:
            return

        tables = getAllTables()
        filings_table_found = False

        for table in tables:
            if table.name == filing_table_name:
                filings_table_found = True
        if not filings_table_found:
            makeFilingsTable(filing_table_name)

        addToEntitiesTable(target_cik, target_parent_cik, target_name)
        addToFilingsTable(filing_table_name, target_cik, filing_quarter, filing)
        updateEntityName(target_cik)
    except Exception as err:
        database_utility_logger.error("{0}:addToDatabase():{1}".format(str(datetime.datetime.now()), str(err)))

    return

def manualAddToDatabase(manual_cik, manual_name, manual_period, target_fact_uri):
    try:
        filing = BookFilingUtility.parseFactFile(target_fact_uri)
        target_cik = int(manual_cik)
        target_parent_cik = None
        target_name = str(manual_name)
        manual_period = str(manual_period)
        filing_year = manual_period[2:6]
        filing_quarter = manual_period[0:2]
        filing_table_name = "filings" + filing_year
        tables = getAllTables()
        filings_table_found = False

        for table in tables:
            if table.name == filing_table_name:
                filings_table_found = True
        if not filings_table_found:
            makeFilingsTable(filing_table_name)

        addToEntitiesTable(target_cik, target_parent_cik, target_name)
        addToFilingsTable(filing_table_name, target_cik, filing_quarter, filing)
        updateEntityName(target_cik)
    except Exception as err:
        database_utility_logger.error("{0}:manualAddToDatabase():{1}".format(str(datetime.datetime.now()), str(err)))

    return

def countEntityAndChildren(target_cik, count = 0):
    try:
        connection = Engine.connect()
        target_cik = int(target_cik)
        tables = getAllTables()
        if len(tables) > 0:
            for table in tables:
                if table.exists() is True:
                    if table.name == "entities":
                        try:
                            entity_sel_stmt = table.select().where(table.columns.entity_cik == target_cik)
                            entity_sel_result = connection.execute(entity_sel_stmt).fetchall()
                            if entity_sel_result is not None:
                                count += len(entity_sel_result)
                            children_sel_stmt = table.select().where(table.columns.parent_cik == target_cik)
                            children_sel_result = connection.execute(children_sel_stmt).fetchall()
                        except Exception as err:
                            database_utility_logger.error("{0}:countEntityAndChildren() inner:{1}".format(str(datetime.datetime.now()), str(err)))
        if children_sel_result is not None:
            for result in children_sel_result:
                count += countEntityAndChildren(result.entity_cik)
        connection.close()

        return count
    except Exception as err:
        database_utility_logger.error("{0}:countEntityAndChildren() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def removeEntityFromDatabase(book_main_window, target_cik, call = 0, total_items = 0):
    try:
        call += 1
        if call == 1:
            total_items = countEntityAndChildren(target_cik)
            if total_items != 0:
                progress = int(100 * call / total_items)
        else:
            if total_items != 0:
                progress = int(100 * call / total_items)
        book_main_window.updateProgressBar(progress)
        children_sel_result = None
        connection = Engine.connect()
        target_cik = int(target_cik)
        tables = getAllTables()
        if len(tables) > 0:
            for table in tables:
                if table.exists() is True:
                    if table.name == "entities":
                        try:
                            parent_del_stmt = table.delete().where(table.columns.entity_cik == target_cik)
                            parent_del_result = connection.execute(parent_del_stmt)
                            children_sel_stmt = table.select().where(table.columns.parent_cik == target_cik)
                            children_sel_result = connection.execute(children_sel_stmt).fetchall()
                        except Exception as err:
                            pass
                    else:
                        try:
                            generic_del_stmt = table.delete().where(table.columns.entity_cik == target_cik)
                            generic_del_result = connection.execute(generic_del_stmt)
                        except Exception as err:
                            pass
        if children_sel_result is not None:
            for result in children_sel_result:
                call = removeEntityFromDatabase(book_main_window, result.entity_cik,
                                         call = call, total_items = total_items)
        if len(tables) > 0:
            for table in tables:
                if table.exists() is True:
                    try:
                        generic_sel_stmt = table.select()
                        generic_sel_result = connection.execute(generic_sel_stmt).first()
                        if generic_sel_result is None and table.name != "entities":
                            table.drop(bind = Engine)
                    except Exception as err:
                        pass

        if call == total_items:
            connection.execute("VACUUM")
            book_main_window.resetProgressBar()
        connection.close()

        return call
    except Exception as err:
        database_utility_logger.error("{0}:removeEntityFromDatabase():{1}".format(str(datetime.datetime.now()), str(err)))

def removeFilingFromDatabase(book_main_window, target_cik, target_period, call = 0, total_items = 0):
    try:
        call += 1
        total_items = 3
        progress = int(100 * call / total_items)
        book_main_window.updateProgressBar(progress)
        connection = Engine.connect()
        target_cik = int(target_cik)
        target_period = str(target_period)
        if len(target_period) == 6:
            target_quarter = target_period[0:2]
            target_year = target_period[2:6]
            target_table_name = "filings" + target_year
        elif len(target_period) == 4:
            target_year = target_period
            target_table_name = "filings" + target_year
        tables = getAllTables()
        if len(tables) > 0:
            for table in tables:
                if table.exists() is True:
                    if table.name == target_table_name:
                        try:
                            if len(target_period) == 6:
                                if target_quarter == "q1":
                                    del_stmt = table.update().where(table.columns.entity_cik == target_cik).values(q1 = None)
                                elif target_quarter == "q2":
                                    del_stmt = table.update().where(table.columns.entity_cik == target_cik).values(q2 = None)
                                elif target_quarter == "q3":
                                    del_stmt = table.update().where(table.columns.entity_cik == target_cik).values(q3 = None)
                                elif target_quarter == "q4":
                                    del_stmt = table.update().where(table.columns.entity_cik == target_cik).values(q4 = None)
                            elif len(target_period) == 4:
                                del_stmt = table.delete().where(table.columns.entity_cik == target_cik)
                            connection.execute(del_stmt)
                        except Exception as err:
                            database_utility_logger.error("{0}:removeFilingFromDatabase() delete:{1}".format(str(datetime.datetime.now()), str(err)))
            for table in tables:
                if table.exists() is True:
                    try:
                        generic_sel_stmt = table.select()
                        generic_sel_result = connection.execute(generic_sel_stmt).first()
                        if generic_sel_result is None and table.name != "entities":
                            table.drop(bind = Engine)
                    except Exception as err:
                        database_utility_logger.error("{0}:removeFilingFromDatabase() table_drop:{1}".format(str(datetime.datetime.now()), str(err)))

        call += 1
        progress = int(100 * call / total_items)
        book_main_window.updateProgressBar(progress)
        connection.execute("VACUUM")
        call += 1
        progress = int(100 * call / total_items)
        book_main_window.updateProgressBar(progress)
        book_main_window.resetProgressBar()
        connection.close()

        return True
    except Exception as err:
        database_utility_logger.error("{0}:removeFilingFromDatabase() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def updateEntityName(target_cik):
    try:
        connection = Engine.connect()
        last_filing = getLastFiling(target_cik)
        target_entity_cik_list, entity_parent_cik, new_entity_name, filing_period = BookFilingUtility.getFilingInfo(last_filing)
        tables = getAllTables()
        for table in tables:
            if table.name == "entities":
                try:
                    update_stmt = table.update().where(table.columns.entity_cik == target_cik).values(entity_name = new_entity_name)
                    update_result = connection.execute(update_stmt)
                except Exception as err:
                    database_utility_logger.error("{0}:updateEntityName() inner:{1}".format(str(datetime.datetime.now()), str(err)))
        connection.close()
    except Exception as err:
        database_utility_logger.error("{0}:updateEntityName() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    return

def getLastFiling(target_cik):
    try:
        connection = Engine.connect()
        tables = getAllTables()
        select_result = None
        target_cik = int(target_cik)
        for table in reversed(tables):
            if table.name.startswith("filings"):
                try:
                    select_stmt = table.select().where(table.columns.entity_cik == target_cik)
                    select_result = connection.execute(select_stmt).first() #SA RowProxy
                    if select_result is not None: # entity is in table
                        try:
                            for col in reversed(select_result.items()):
                                if col[1] is not None: # latest filing
                                    select_result = pickle.loads(col[1]) # [0 = key, 1 = val]
                                    return select_result
                                else:
                                    pass
                        except Exception as err:
                            database_utility_logger.error("{0}:getLastFiling() inner:{1}".format(str(datetime.datetime.now()), str(err)))
                            select_result = None
                except Exception as err:
                    database_utility_logger.error("{0}:getLastFiling() middle:{1}".format(str(datetime.datetime.now()), str(err)))
                    select_result = None
        connection.close()

        return select_result
    except Exception as err:
        database_utility_logger.error("{0}:getLastFiling() outer:{1}".format(str(datetime.datetime.now()), str(err)))

def renameEntityInDatabase(target_cik, new_entity_name):
    try:
        target_cik = int(target_cik)
        new_entity_name = str(new_entity_name)
        connection = Engine.connect()
        tables = getAllTables()
        for table in tables:
            if table.name == "entities":
                try:
                    update_stmt = table.update().where(table.columns.entity_cik == target_cik).values(entity_name = new_entity_name)
                    update_result = connection.execute(update_stmt)
                except Exception as err:
                    database_utility_logger.error("{0}:renameEntityInDatabase() inner:{1}".format(str(datetime.datetime.now()), str(err)))

        connection.close()
    except Exception as err:
        database_utility_logger.error("{0}:renameEntityInDatabase() outer:{1}".format(str(datetime.datetime.now()), str(err)))

    return
