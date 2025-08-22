
CREATE PROC dbo.dag_addNewEdge
@nodeName varchar(150),
@edgeName varchar(150)
AS

DECLARE
	@nodeid int,
	@edgeid int

SELECT 
	@nodeid = id
FROM dbo.dag_parameters
	WHERE
		[name] = @nodeName

SELECT 
	@edgeid = id
FROM dbo.dag_parameters
	WHERE
		[name] = @edgeName

INSERT INTO dbo.dag_dependson
VALUES(
	(SELECT $node_id FROM dbo.dag_parameters WHERE ID = @edgeid),
	(SELECT $node_id FROM dbo.dag_parameters WHERE ID = @nodeid)
)

GO

