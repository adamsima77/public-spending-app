import { OrganizationResource, OrganizationsIndex$Params } from '../../../../generated';
import { PageParams } from '../../../../config/tables/models/paginated.model';
import { FormControl, FormGroup } from '@angular/forms';

export type Organization = OrganizationResource;

export type OrganizationSort = NonNullable<OrganizationsIndex$Params['sort']>;

export type OrganizationQueryParams = PageParams<OrganizationSort> &
  Partial<OrganizationsIndex$Params>;

export type OrganizationFilterParams = Pick<
  OrganizationsIndex$Params,
  'search' | 'country[]' | 'company_size[]' | 'role[]'
>;

export type OrganizationRole = NonNullable<OrganizationFilterParams['role[]']>[number];

export interface OrganizationFilterValues {
  search: string;
  country: string[];
  company_size: string[];
  role: OrganizationRole[];
}

export interface OrganizationFilterControls {
  search: FormControl<string>;
  country: FormControl<string[]>;
  company_size: FormControl<string[]>;
  role: FormControl<OrganizationRole[]>;
}

export type OrganizationFilterForm = FormGroup<OrganizationFilterControls>;
