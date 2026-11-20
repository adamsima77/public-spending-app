import { NoticeResource } from '@generated';
import { TableColumn } from '@shared/config/tables/models/table-column.model';

export const NOTICE_COLUMNS: TableColumn<NoticeResource>[] = [
  {
    key: 'title',
    header: 'Názov oznámenia',
    value: (n) => n.title ?? 'Bez názvu',
    primary: true,
    sortable: true,
  },
  {
    key: 'notice_id',
    header: 'Číslo oznámenia',
    value: (n) => n.notice_id,
    sortable: true,
  },
  {
    key: 'notice_type',
    header: 'Typ oznámenia',
    value: (n) => n.notice_type_definition?.code ?? n.notice_type ?? '—',
    sortable: true,
  },
  {
    key: 'published_at',
    header: 'Zverejnené',
    value: (n) => (n.published_at ? new Date(n.published_at).toLocaleDateString('sk-SK') : '—'),
    sortable: true,
  },
  {
    key: 'notice_version',
    header: 'Verzia',
    value: (n) => `v${n.notice_version.toString()}${n.is_latest ? ' (aktuálna)' : ''}`,
  },
];
