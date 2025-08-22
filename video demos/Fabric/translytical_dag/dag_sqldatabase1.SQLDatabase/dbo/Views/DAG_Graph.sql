
CREATE VIEW [dbo].[DAG_Graph]
AS
SELECT 
	dag_parameters2.name AS [Edge],
	dag_parameters.name As [Node]
FROM dbo.dag_parameters, dag_parameters dag_parameters2, dbo.dag_dependson
WHERE MATCH (dag_parameters2 - (dag_dependson) -> dag_parameters)

GO

