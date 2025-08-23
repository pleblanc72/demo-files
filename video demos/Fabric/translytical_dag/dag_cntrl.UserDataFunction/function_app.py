import fabric.functions as fn

udf = fn.UserDataFunctions()

@udf.connection(argName="graphSQL", alias="dagsqldatabase1")
@udf.connection(argName="lakeFolder", alias="daglakehouse1")
@udf.function()
def export_DAG(graphSQL: fn.FabricSqlConnection, lakeFolder: fn.FabricLakehouseClient) -> str:

    #Connect to SQL Database
    sqlConnection = graphSQL.connect()

    #Open the connection to the SQL Database and Execute the dag_Generate proc that genenerates the DAG string
    cursor = sqlConnection.cursor()
    cursor.execute("EXEC dbo.dag_Generate")

    #Get the result from the previous query
    rows = cursor.fetchall()

    #Intialize, populate and remove some unccessary characters from the value returned by the proc
    dag_string = str
    dag_string =  str(rows[0])
    dag_string = dag_string.replace("',)", "").replace("('","")

    #Open connection to the Lakehouse
    lhFileConnection = lakeFolder.connectToFiles()

    #Initialize the txtFileName variable with the path and name of the file.
    txtFileName = "dag_files/DAG.txt"
    
    #Get and updload the file to the lakehouse
    txtFile = lhFileConnection.get_file_client(txtFileName)
    txtFile.upload_data(dag_string, overwrite=True)
    
    #Close all open connections
    cursor.close()
    sqlConnection.close()
    txtFile.close()
    lhFileConnection.close()

    #Return completion prompt
    return f"The DAG containing {dag_string} will be written to a file named {txtFileName} in the {lakeFolder.alias_name} Lakehouse."


@udf.connection(argName="graphSQL", alias="dagsqldatabase1")
@udf.function()
def add_DAG_node(graphSQL: fn.FabricSqlConnection,  name: str, path: str, timeoutPerCellInSeconds: int, retry: int, retryIntervalInSeconds: int) -> str:
    
    #Connect to SQL Database
    sqlConnection = graphSQL.connect()

    #Open the connection to the SQL Database and Execute the dag_Generate proc that genenerates the DAG string
    cursor = sqlConnection.cursor()

    insert_node_query = f"EXEC dag_addNewNode @name = '{name}', @path = '{path}', @timeoutPerCellInSeconds = {timeoutPerCellInSeconds}, @retry = {retry}, @retryIntervalInSeconds = {retryIntervalInSeconds}"

    cursor.execute(insert_node_query)

    sqlConnection.commit()
    cursor.close()
    sqlConnection.close()
    return f"Node added to Graph {insert_node_query}"

@udf.connection(argName="graphSQL", alias="dagsqldatabase1")
@udf.function()
def add_DAG_edge(graphSQL: fn.FabricSqlConnection,  nodeName: str, edgeName: str) -> str:
    
    #Connect to SQL Database
    sqlConnection = graphSQL.connect()

    #Open the connection to the SQL Database and Execute the dag_Generate proc that genenerates the DAG string
    cursor = sqlConnection.cursor()

    insert_node_query = f"EXEC dag_addNewEdge @nodeName = '{nodeName}', @edgeName = '{edgeName}'"

    cursor.execute(insert_node_query)

    sqlConnection.commit()
    cursor.close()
    sqlConnection.close()
    return f"Edge added to Graph {insert_node_query}"