import { OrganizationResource } from '@generated';
import { TableColumn } from './models/table-column.model';

export const organizationColumns: TableColumn<OrganizationResource>[] = [
  { key: 'name', header: 'Názov', value: (o) => o.name, primary: true, sortable: true },
  { key: 'cin', header: 'IČO', value: (o) => o.cin, sortable: true },
  { key: 'town', header: 'Mesto', value: (o) => o.town, sortable: true },
  { key: 'country', header: 'Krajina', value: (o) => o.country },
  { key: 'company_size', header: 'Veľkosť', value: (o) => o.company_size },
];
