import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { OrganizationFilterForm } from '@shared/models/organizations.model';
import { FilterBar } from '@shared/ui/filters/filter-bar/filter-bar';
import { SearchField } from '@shared/ui/filters/search-field/search-field';
import { FilterSelect } from '@shared/ui/filters/filter-select/filter-select';
import { FilterChips } from '@shared/ui/filters/filter-chips/filter-chips';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';

@Component({
  selector: 'app-organization-filters',
  imports: [FilterBar, SearchField, FilterSelect, FilterChips],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './organization-filters.html',
})
export class OrganizationFilters {
  readonly form = input.required<OrganizationFilterForm>();
  readonly countries = input.required<readonly FilterOption[]>();
  readonly companySizes = input.required<readonly FilterOption[]>();
  readonly roles = input.required<readonly FilterOption[]>();
  readonly hasActive = input(false);

  protected reset(): void {
    this.form().reset({ search: '', country: [], company_size: [], role: [] });
  }
}
