import { Link, generatePath } from 'react-router-dom';
import { Table, TableRow, TableCell, IconButton } from '@uikit';
import { useDispatch, useStore } from '@hooks';
import { columns } from './JobsTable.constants';
import { setSortParams } from '@store/adcm/jobs/jobsTableSlice';
import { SortParams } from '@uikit/types/list.types';
import { openRestartDialog, openStopDialog } from '@store/adcm/jobs/jobsActionsSlice';
import { AdcmJobStatus } from '@models/adcm';
import JobsStatusCell from '../../../common/Table/Cells/JobsStatusCell/JobsStatusCell';
import { secondsToDuration } from '@utils/date/timeConvertUtils';
import DateTimeCell from '@commonComponents/Table/Cells/DateTimeCell';
import JobObjectsCell from '@commonComponents/Table/Cells/JobObjectsCell/JobObjectsCell';

const JobsTable = () => {
  const dispatch = useDispatch();
  const jobs = useStore((s) => s.adcm.jobs.jobs);
  const isLoading = useStore((s) => s.adcm.jobs.isLoading);
  const sortParams = useStore((s) => s.adcm.jobsTable.sortParams);

  const handleRestartClick = (id: number) => () => {
    dispatch(openRestartDialog(id));
  };

  const handleStopClick = (id: number) => () => {
    dispatch(openStopDialog(id));
  };

  const handleSorting = (sortParams: SortParams) => {
    dispatch(setSortParams(sortParams));
  };

  return (
    <Table
      isLoading={isLoading}
      columns={columns}
      sortParams={sortParams}
      onSorting={handleSorting}
      variant="secondary"
    >
      {jobs.map((job) => {
        return (
          <TableRow key={job.id}>
            <TableCell>{job.id}</TableCell>
            <JobsStatusCell status={job.status}>
              <Link to={generatePath('/jobs/:jobId', { jobId: job.id + '' })} className="text-link">
                {job.displayName}
              </Link>
            </JobsStatusCell>
            <TableCell>{job.status}</TableCell>
            <JobObjectsCell objects={job.objects} />
            <TableCell>{secondsToDuration(job.duration)}</TableCell>
            <DateTimeCell value={job.startTime} />
            <DateTimeCell value={job.endTime} />
            <TableCell hasIconOnly align="center">
              {job.status !== AdcmJobStatus.Success && (
                <IconButton icon="g1-return" size={32} title="Restart job" onClick={handleRestartClick(job.id)} />
              )}
              {job.status === AdcmJobStatus.Success && (
                <IconButton icon="g1-stop" title="Stop the job" size={32} onClick={handleStopClick(job.id)} />
              )}
            </TableCell>
          </TableRow>
        );
      })}
    </Table>
  );
};

export default JobsTable;
