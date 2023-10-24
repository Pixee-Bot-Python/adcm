import React from 'react';
import { useDispatch, useStore } from '@hooks';
import { columns, loginsAuditInactiveResults } from './AuditLoginsTable.constants';
import { Table, TableCell, TableRow } from '@uikit';
import { setSortParams } from '@store/adcm/audit/auditLogins/auditLoginsTableSlice';
import { SortParams } from '@models/table';
import DateTimeCell from '@commonComponents/Table/Cells/DateTimeCell';
import { orElseGet } from '@utils/checkUtils';

const AuditLoginsTable = () => {
  const dispatch = useDispatch();

  const auditLogins = useStore(({ adcm }) => adcm.auditLogins.auditLogins);
  const isLoading = useStore(({ adcm }) => adcm.auditLogins.isLoading);
  const sortParams = useStore(({ adcm }) => adcm.auditLoginsTable.sortParams);

  const handleSorting = (sortParams: SortParams) => {
    dispatch(setSortParams(sortParams));
  };

  return (
    <Table variant="tertiary" isLoading={isLoading} columns={columns} sortParams={sortParams} onSorting={handleSorting}>
      {auditLogins.map((auditLogin) => (
        <TableRow key={auditLogin.id} isInactive={loginsAuditInactiveResults.includes(auditLogin.result)}>
          <TableCell>{orElseGet(auditLogin.user?.name)}</TableCell>
          <TableCell>{orElseGet(auditLogin.result)}</TableCell>
          <DateTimeCell value={orElseGet(auditLogin.time)} />
        </TableRow>
      ))}
    </Table>
  );
};

export default AuditLoginsTable;
