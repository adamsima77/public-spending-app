export interface PageMeta {
  total: number;
  currentPage: number;
  perPage: number;
  lastPage: number;
}

export interface Paginated<T> {
  data: T[];
  meta: PageMeta;
}

export interface PageParams<TSort extends string = string> {
  page: number;
  per_page: number;
  sort?: TSort | null;
  direction?: 'asc' | 'desc' | null;
}
