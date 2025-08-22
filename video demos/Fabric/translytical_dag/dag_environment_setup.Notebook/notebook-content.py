# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

LakehouseName = 'dag_lakehouse1'
SQLDatabaseName ='dag_sqldatabase1'
SemanticModelNam = 'dag_SemanticModel3'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

%pip install -q semantic-link-labs
%pip install -q azure-storage-blob

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

import sempy_labs as labs
from sempy import fabric
import sempy
import pandas as pd 
import re
from azure.storage.blob import BlobClient
import json
from powerbiclient import Report
import sempy_labs.report._report_helper as helper

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

workspaceId = fabric.get_workspace_id()
workspaceName = sempy.fabric.resolve_workspace_name(workspaceId)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

lakehouses=labs.list_lakehouses()["Lakehouse Name"]
if LakehouseName in lakehouses.values:
    lakehouseId = notebookutils.lakehouse.getWithProperties(LakehouseName)["id"]
    print(f'{LakehouseName} already exists.  Choose a different name if you want to create a new lakehouse.')
else:
    try:
        lakehouseId = fabric.create_lakehouse(LakehouseName)
        print(f'{LakehouseName} create successfull in {workspaceName}')        
    except:
        False

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

try:
    LakehouseFolderPath = f'abfss://{workspaceId}@onelake.dfs.fabric.microsoft.com/{lakehouseId}/Files/dag_files'
    notebookutils.fs.mkdirs(LakehouseFolderPath)
except NameError:
    print("Check workspace to verify creation of Lakehouse.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

sqldatabases = labs.list_sql_databases()["Database Name"]
createdb = False
for db in sqldatabases:
    if SQLDatabaseName == re.sub(r'-.*', '', sqldatabases.values[0]):
        createdb = True

if createdb:
    df = pd.concat([fabric.list_items(workspace=workspaceId) for ws in fabric.list_workspaces(f"name eq '{workspaceName}'").query('`Is On Dedicated Capacity` == True').Id], ignore_index=True) 
    sqldatabaseid = df.loc[df['Display Name'] == SQLDatabaseName, 'Id'].iloc[0]
    print(f'{SQLDatabaseName} already exists.  Choose a different name if you want to create a new warehouse.')
else:
    try:
        labs.create_sql_database(SQLDatabaseName)
        print(f'{SQLDatabaseName} create successfull in {workspaceName}')     
    except:
        False   

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC DROP TABLE IF EXISTS dbo.dag_parameters;
# MAGIC 
# MAGIC CREATE TABLE dbo.dag_parameters
# MAGIC (
# MAGIC 	[id] integer primary key,
# MAGIC 	[name] varchar(150) NOT NULL,
# MAGIC 	[path] varchar(300) NOT NULL,
# MAGIC 	[timeoutPerCellInSeconds] int NOT NULL,
# MAGIC 	[args] varchar(500),
# MAGIC 	[retry] int,
# MAGIC 	[retryIntervalInSeconds] int,
# MAGIC ) AS NODE;
# MAGIC 
# MAGIC DROP TABLE IF EXISTS dbo.dag_dependson;
# MAGIC 
# MAGIC CREATE TABLE dbo.dag_dependson AS EDGE;


# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC DROP PROC IF EXISTS dbo.dag_Generate;
# MAGIC DROP PROC IF EXISTS dbo.dag_addNewNode;
# MAGIC DROP PROC IF EXISTS dbo.dag_addNewEdge;
# MAGIC DROP VIEW IF EXISTS dbo.DAG_Graph;
# MAGIC DROP VIEW IF EXISTS dbo.notebooks;

# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC CREATE PROC dbo.dag_Generate
# MAGIC @timeoutInSeconds int = 43200,
# MAGIC @concurrency int = 5
# MAGIC AS
# MAGIC 
# MAGIC DECLARE
# MAGIC 	@json varchar(max)
# MAGIC 
# MAGIC SELECT @json = 
# MAGIC 	(SELECT 
# MAGIC 		p.name,
# MAGIC 		p.path,
# MAGIC 		p.timeoutPerCellInSeconds,
# MAGIC 		p.args,
# MAGIC 		p.retry,
# MAGIC 		(
# MAGIC 			SELECT 
# MAGIC 					JSON_ARRAY(STRING_AGG(dag_parameters.name, ', ')) AS dependencies 
# MAGIC 			FROM dbo.dag_parameters, dag_parameters dag_parameters2, dbo.dag_dependson
# MAGIC 			WHERE MATCH 
# MAGIC 				(dag_parameters2 - (dag_dependson) -> dag_parameters) AND
# MAGIC 				p.Id = dag_parameters2.id
# MAGIC 			GROUP BY
# MAGIC 				dag_parameters2.id
# MAGIC 		)  dependencies
# MAGIC 	FROM dbo.dag_parameters p
# MAGIC 	FOR JSON PATH, ROOT('activities')
# MAGIC 	)
# MAGIC 
# MAGIC SELECT @json =
# MAGIC (
# MAGIC 	SELECT JSON_MODIFY
# MAGIC 	(
# MAGIC 		@json,
# MAGIC 		'$.timeoutInSeconds', @timeoutInSeconds
# MAGIC 	)
# MAGIC )
# MAGIC 
# MAGIC SELECT @json =
# MAGIC (
# MAGIC 	SELECT JSON_MODIFY
# MAGIC 	(
# MAGIC 		@json,
# MAGIC 		'$.concurrency', @concurrency
# MAGIC 	)
# MAGIC )
# MAGIC 
# MAGIC SELECT @json

# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC CREATE PROC dbo.dag_addNewNode
# MAGIC @name varchar(150),
# MAGIC @path varchar(300),
# MAGIC @timeoutPerCellInSeconds int,
# MAGIC @args varchar(500) = NULL,
# MAGIC @retry int,
# MAGIC @retryIntervalInSeconds int
# MAGIC AS
# MAGIC DECLARE @id int
# MAGIC 
# MAGIC SELECT 
# MAGIC 	@id = COALESCE(MAX(id), 0) + 1
# MAGIC FROM dbo.dag_parameters
# MAGIC 
# MAGIC INSERT INTO dbo.dag_parameters(id, [name], [path], timeoutPerCellInSeconds, args, retry, retryIntervalInSeconds)
# MAGIC VALUES(@id, @name, @path, @timeoutPerCellInSeconds, @args, @retry, @retryIntervalInSeconds)
# MAGIC 
# MAGIC SELECT @id
# MAGIC GO

# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC CREATE PROC dbo.dag_addNewEdge
# MAGIC @nodeName varchar(150),
# MAGIC @edgeName varchar(150)
# MAGIC AS
# MAGIC 
# MAGIC DECLARE
# MAGIC 	@nodeid int,
# MAGIC 	@edgeid int
# MAGIC 
# MAGIC SELECT 
# MAGIC 	@nodeid = id
# MAGIC FROM dbo.dag_parameters
# MAGIC 	WHERE
# MAGIC 		[name] = @nodeName
# MAGIC 
# MAGIC SELECT 
# MAGIC 	@edgeid = id
# MAGIC FROM dbo.dag_parameters
# MAGIC 	WHERE
# MAGIC 		[name] = @edgeName
# MAGIC 
# MAGIC INSERT INTO dbo.dag_dependson
# MAGIC VALUES(
# MAGIC 	(SELECT $node_id FROM dbo.dag_parameters WHERE ID = @edgeid),
# MAGIC 	(SELECT $node_id FROM dbo.dag_parameters WHERE ID = @nodeid)
# MAGIC )


# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC CREATE VIEW [dbo].[DAG_Graph]
# MAGIC AS
# MAGIC SELECT 
# MAGIC 	dag_parameters2.name AS [Edge],
# MAGIC 	dag_parameters.name As [Node]
# MAGIC FROM dbo.dag_parameters, dag_parameters dag_parameters2, dbo.dag_dependson
# MAGIC WHERE MATCH (dag_parameters2 - (dag_dependson) -> dag_parameters)


# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# MAGIC %%tsql -artifact {SQLDatabaseName} -type SQLDatabase
# MAGIC CREATE VIEW [dbo].[notebooks]
# MAGIC AS
# MAGIC SELECT 
# MAGIC 	P.name
# MAGIC FROM dbo.dag_parameters p
# MAGIC LEFT OUTER JOIN dbo.dag_dependson d
# MAGIC 	ON	p.$node_id = d.$from_id

# METADATA ********************

# META {
# META   "language": "sql",
# META   "language_group": "jupyter_python"
# META }
