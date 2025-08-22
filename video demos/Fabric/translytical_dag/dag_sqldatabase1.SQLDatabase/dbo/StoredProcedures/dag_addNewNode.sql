
CREATE PROC dbo.dag_addNewNode
@name varchar(150),
@path varchar(300),
@timeoutPerCellInSeconds int,
@args varchar(500) = NULL,
@retry int,
@retryIntervalInSeconds int
AS
DECLARE @id int

SELECT 
	@id = COALESCE(MAX(id), 0) + 1
FROM dbo.dag_parameters

INSERT INTO dbo.dag_parameters(id, [name], [path], timeoutPerCellInSeconds, args, retry, retryIntervalInSeconds)
VALUES(@id, @name, @path, @timeoutPerCellInSeconds, @args, @retry, @retryIntervalInSeconds)

SELECT @id

GO

