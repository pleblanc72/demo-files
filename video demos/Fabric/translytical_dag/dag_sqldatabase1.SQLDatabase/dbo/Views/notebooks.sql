
CREATE VIEW [dbo].[notebooks]
AS
SELECT 
	P.name
FROM dbo.dag_parameters p
LEFT OUTER JOIN dbo.dag_dependson d
	ON	p.$node_id = d.$from_id

GO

