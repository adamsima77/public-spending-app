import { FormControl, FormGroup } from '@angular/forms';
import { SettledContractIndex$Params, SettledContractResource } from '@generated';
import { PageParams } from '@shared/config/tables/models/paginated.model';
import { Signal } from '@angular/core';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';

export type SettledContract = SettledContractResource;

export type SettledContractSort = NonNullable<SettledContractIndex$Params['sort']>;

export interface SettledContractFilterValues {
  search: string;
  buyer_id: string;
  conclusion_from: string | Date | null;
  conclusion_to: string | Date | null;
  has_url: string[];
  has_tenders: string[];
  only_current: string[];
}

export type SettledContractFilterForm = FormGroup<{
  search: FormControl<string>;
  buyer_id: FormControl<string>;
  conclusion_from: FormControl<string | Date | null>;
  conclusion_to: FormControl<string | Date | null>;
  has_url: FormControl<string[]>;
  has_tenders: FormControl<string[]>;
  only_current: FormControl<string[]>;
}>;

export type SettledContractFilterParams = Pick<
  SettledContractIndex$Params,
  | 'search'
  | 'buyer_id'
  | 'conclusion_from'
  | 'conclusion_to'
  | 'has_url'
  | 'has_tenders'
  | 'only_current'
>;

export interface BuyerFilter {
  options: Signal<FilterOption[]>;
  selected: Signal<FilterOption | null>;
  onQuery: (query: string) => void;
}

export type SettledContractQueryParams = PageParams<SettledContractSort> &
  SettledContractFilterParams;
