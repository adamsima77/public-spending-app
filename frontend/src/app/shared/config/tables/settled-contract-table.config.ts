import { SettledContractResource } from '@generated';
import { TableColumn } from '@shared/config/tables/models/table-column.model';

const dateFormat = new Intl.DateTimeFormat('sk-SK');

export const settledContractColumns: TableColumn<SettledContractResource>[] = [
  {
    key: 'title',
    header: 'Názov',
    value: (c) => c.title ?? c.contract_number,
    primary: true,
    sortable: true,
  },
  {
    key: 'contract_number',
    header: 'Číslo zmluvy',
    value: (c) => (c.title ? c.contract_number : null),
    sortable: true,
  },
  {
    key: 'conclusion_date',
    header: 'Dátum uzavretia',
    value: (c) => (c.conclusion_date ? dateFormat.format(new Date(c.conclusion_date)) : null),
    sortable: true,
  },
  {
    key: 'contract_url',
    header: 'Odkaz na zmluvu',
    value: (c) => (c.contract_url ? 'Áno' : 'Nie'),
  },
];
