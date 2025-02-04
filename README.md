Here's a SQL stored procedure that retrieves SQL Server Agent jobs along with their latest execution details, including failure information and error messages:

```sql
CREATE PROCEDURE dbo.GetServerAgentJobStatus
AS
BEGIN
    SELECT
        j.name AS JobName,
        msdb.dbo.agent_datetime(ja.last_run_date, ja.last_run_time) AS LastRunDateTime,
        CASE
            WHEN ja.last_run_outcome IS NULL THEN 'Never run'
            WHEN ja.last_run_outcome = 0 THEN 'Failed'
            WHEN ja.last_run_outcome = 1 THEN 'Succeeded'
            WHEN ja.last_run_outcome = 3 THEN 'Canceled'
            ELSE 'Unknown'
        END AS LastRunStatus,
        COALESCE(failed_step.message, job_outcome.message) AS ErrorMessage
    FROM
        msdb.dbo.sysjobs j
        LEFT JOIN msdb.dbo.sysjobactivity ja 
            ON j.job_id = ja.job_id
            AND ja.session_id = (SELECT MAX(session_id) FROM msdb.dbo.syssessions)
        LEFT JOIN msdb.dbo.sysjobhistory job_outcome
            ON j.job_id = job_outcome.job_id
            AND ja.last_run_date = job_outcome.run_date
            AND ja.last_run_time = job_outcome.run_time
            AND job_outcome.step_id = 0
        OUTER APPLY (
            SELECT TOP 1
                jh.message
            FROM
                msdb.dbo.sysjobhistory jh
            WHERE
                jh.job_id = j.job_id
                AND jh.run_date = ja.last_run_date
                AND jh.run_time = ja.last_run_time
                AND jh.step_id > 0
                AND jh.run_status = 0
            ORDER BY
                jh.step_id ASC
        ) AS failed_step
    ORDER BY
        JobName;
END;
GO
```

**Features:**
1. Lists all SQL Server Agent jobs
2. Shows last execution time using SQL Server Agent's internal datetime format
3. Provides execution status (Never run/Failed/Succeeded/Canceled/Unknown)
4. Displays error messages from either:
   - The first failed step in the job (most specific error)
   - The job outcome message if no specific step failed
5. Handles jobs that have never been executed

**Usage:**
```sql
EXEC dbo.GetServerAgentJobStatus;
```

**Required Permissions:**
- User must have access to the `msdb` database
- Requires membership in the `SQLAgentReaderRole` or similar privileges

**Output Columns:**
- **JobName**: Name of the SQL Server Agent job
- **LastRunDateTime**: Last execution time in datetime format
- **LastRunStatus**: Status of the last execution
- **ErrorMessage**: Relevant error message if the job failed (NULL if successful)

**Notes:**
- The procedure uses SQL Server's built-in `agent_datetime` function to properly convert Agent's date/time storage format
- Error messages are prioritized from specific failed steps before falling back to general job outcome messages
- Handles jobs that have never been executed by showing "Never run" status
- Results are ordered alphabetically by job name

To use this procedure, simply execute it in the context of the `msdb` database or from any database with proper permissions to access system tables in `msdb`.
