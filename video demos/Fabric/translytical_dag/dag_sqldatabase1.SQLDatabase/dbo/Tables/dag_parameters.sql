CREATE TABLE [dbo].[dag_parameters] (
    [id]                      INT           NOT NULL,
    [name]                    VARCHAR (150) NOT NULL,
    [path]                    VARCHAR (300) NOT NULL,
    [timeoutPerCellInSeconds] INT           NOT NULL,
    [args]                    VARCHAR (500) NULL,
    [retry]                   INT           NULL,
    [retryIntervalInSeconds]  INT           NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    INDEX [GRAPH_UNIQUE_INDEX_7CCDEE78269A4162B5DEAF3467355FA7] UNIQUE NONCLUSTERED ($node_id)
) AS NODE;


GO

