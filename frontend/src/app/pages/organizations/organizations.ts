import { Component, computed, inject, input, numberAttribute } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { PageEvent } from '@angular/material/paginator';
import { PageHeader, PageHeaderData } from '../../components/ui/page-header/page-header';
import { OrganizationFacade } from './organization-facade/organization-facade';
import { ORGANIZATIONS_PAGE_CONFIG } from '../../config/page-headers/organization-header.config';
import { DataTable } from '../../components/ui/data-table/data-table';
import { organizationColumns } from '../../config/tables/organization-table.config';
import { PageParams } from '../../config/tables/models/paginated.model';
import { paginatedSizes } from '../../config/tables/paginated-sizes.config';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule } from '@angular/forms';
import { Sort } from '@angular/material/sort';
import {
  Organization,
  OrganizationFilterForm,
  OrganizationSort,
} from './organization-facade/models/organizations.model';
import { MatCardModule } from '@angular/material/card';
import { roleOptions } from '../../config/filters/organization-role.config';
import { LucideSearch } from '@lucide/angular';

@Component({
  imports: [
    PageHeader,
    DataTable,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    LucideSearch,
  ],
  selector: 'app-organizations',
  styleUrl: './organizations.scss',
  templateUrl: './organizations.html',
})
export class Organizations {
  private readonly organizationFacade = inject(OrganizationFacade);
  private readonly router = inject(Router);
  private readonly kpis = toSignal(this.organizationFacade.getOrganizationKpis());
  readonly page = input(1, { transform: (v: unknown): number => numberAttribute(v, 1) });
  readonly per_page = input(25, { transform: (v: unknown): number => numberAttribute(v, 25) });
  readonly sort = input<OrganizationSort>();
  readonly direction = input<'asc' | 'desc' | null>(null);
  private readonly pageState = computed<PageParams<OrganizationSort>>(() => ({
    page: this.page(),
    per_page: this.per_page(),
    sort: this.sort(),
    direction: this.direction(),
  }));

  protected readonly columns = organizationColumns;
  protected readonly rows = computed(() => this.organizations()?.data ?? []);
  protected readonly meta = computed(() => this.organizations()?.meta);
  protected readonly pageSizeOptions = paginatedSizes;
  protected readonly rowLink = (org: Organization): (string | number)[] => ['/organizacie', org.id];
  protected readonly roleFilterOptions = roleOptions;
  protected readonly companySizeFilters = toSignal(this.organizationFacade.getCompanySizes());
  protected readonly countryFilters = toSignal(this.organizationFacade.getOrganizationCountries());
  protected readonly filterForm: OrganizationFilterForm =
    this.organizationFacade.getInitialFilterValues();

  private readonly organizationState = this.organizationFacade.connectOrganizations(
    this.pageState,
    this.filterForm,
  );

  protected readonly organizations = this.organizationState.organizations;

  protected readonly pageHeaderData = computed<PageHeaderData>(() => {
    const kpis = this.kpis();

    return {
      ...ORGANIZATIONS_PAGE_CONFIG,
      kpis: kpis ? this.organizationFacade.toKpiCards(kpis) : undefined,
      loading: !kpis,
    };
  });

  protected onPageChange(event: PageEvent): void {
    void this.router.navigate([], {
      queryParams: { page: event.pageIndex + 1, per_page: event.pageSize },
      queryParamsHandling: 'merge',
    });
  }

  protected readonly sortState = computed<Sort | undefined>(() => {
    const active = this.sort();

    return active ? { active, direction: this.direction() ?? 'asc' } : undefined;
  });

  protected onSortChange(sort: Sort): void {
    void this.router.navigate([], {
      queryParams: {
        sort: sort.direction ? sort.active : null,
        direction: sort.direction || null,
        page: null,
      },
      queryParamsHandling: 'merge',
    });
  }

  protected readonly hasActiveFilters = this.organizationState.hasActiveFilters;

  protected clearSearch(): void {
    this.filterForm.controls.search.reset();
  }

  protected resetFilters(): void {
    this.filterForm.reset({
      search: '',
      country: [],
      company_size: [],
      role: [],
    });
  }
}
