
CREATE PROC dbo.dag_Generate
@timeoutInSeconds int = 43200,
@concurrency int = 5
AS

DECLARE
	@json varchar(max)

SELECT @json = 
	(SELECT 
		p.name,
		p.path,
		p.timeoutPerCellInSeconds,
		p.args,
		p.retry,
		(
			SELECT 
					JSON_ARRAY(STRING_AGG(dag_parameters.name, ', ')) AS dependencies 
			FROM dbo.dag_parameters, dag_parameters dag_parameters2, dbo.dag_dependson
			WHERE MATCH 
				(dag_parameters2 - (dag_dependson) -> dag_parameters) AND
				p.Id = dag_parameters2.id
			GROUP BY
				dag_parameters2.id
		)  dependencies
	FROM dbo.dag_parameters p
	FOR JSON PATH, ROOT('activities')
	)

SELECT @json =
(
	SELECT JSON_MODIFY
	(
		@json,
		'$.timeoutInSeconds', @timeoutInSeconds
	)
)

SELECT @json =
(
	SELECT JSON_MODIFY
	(
		@json,
		'$.concurrency', @concurrency
	)
)

SELECT @json

GO

