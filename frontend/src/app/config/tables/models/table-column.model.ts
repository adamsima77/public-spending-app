export interface TableColumn<T> {
  key: string;
  header: string;
  value: (row: T) => string | number | null;
  primary?: boolean;
  sortable?: boolean;
}
