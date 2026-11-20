import { FormControl, FormGroup } from '@angular/forms';
import { NoticeResource } from '@generated';
import { PageParams } from '@shared/config/tables/models/paginated.model';

export type Notice = NoticeResource;

export type NoticeSort = 'title' | 'notice_id' | 'notice_type' | 'published_at' | 'issue_date';

export interface NoticeFilterValues {
  search: string;
  notice_type: string[];
  form_type: string[];
  procedure_id: number | null;
  is_latest: boolean | null;
  published_from: string | Date | null;
  published_to: string | Date | null;
}

export type NoticeFilterForm = FormGroup<{
  search: FormControl<string>;
  notice_type: FormControl<string[]>;
  form_type: FormControl<string[]>;
  procedure_id: FormControl<number | null>;
  is_latest: FormControl<boolean | null>;
  published_from: FormControl<string | Date | null>;
  published_to: FormControl<string | Date | null>;
}>;

export interface NoticeFilterParams {
  search?: string;
  'notice_type[]'?: string[];
  'form_type[]'?: string[];
  procedure_id?: number;
  is_latest?: boolean;
  published_from?: string;
  published_to?: string;
}

export type NoticeQueryParams = PageParams<NoticeSort> & NoticeFilterParams;
