import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  numberAttribute,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { Sort } from '@angular/material/sort';
import { PageHeader } from '@shared/ui/page-header/page-header';
import { PageHeaderData } from '@shared/ui/page-header/models/page-header.model';
import { SettledContractFacade } from '@shared/facades/settled-contract-facade/settled-contract-facade';
import { SETTLED_CONTRACTS_PAGE_CONFIG } from '@shared/config/page-headers/settled-contract-header.config';
import { DataTable } from '@shared/ui/data-table/data-table';
import { settledContractColumns } from '@shared/config/tables/settled-contract-table.config';
import { PageParams } from '@shared/config/tables/models/paginated.model';
import { paginatedSizes } from '@shared/config/tables/paginated-sizes.config';
import { SettledContract, SettledContractSort } from '@shared/models/settled-contracts.model';
import { SettledContractFilters } from '@components/ui/settled-contract-filters/settled-contract-filters';
import { Router } from '@angular/router';

@Component({
  imports: [
    PageHeader,
    DataTable,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    SettledContractFilters,
  ],
  selector: 'app-settled-contracts',
  styleUrl: './settled-contracts.scss',
  templateUrl: './settled-contracts.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettledContracts {
  private readonly facade = inject(SettledContractFacade);
  private readonly router = inject(Router);
  private readonly kpis = toSignal(this.facade.getSettledContractKpis());

  readonly page = input(1, { transform: (v: unknown): number => numberAttribute(v, 1) });
  readonly per_page = input(25, { transform: (v: unknown): number => numberAttribute(v, 25) });
  readonly sort = input<SettledContractSort>();
  readonly direction = input<'asc' | 'desc' | null>(null);
  private readonly pageState = computed<PageParams<SettledContractSort>>(() => ({
    page: this.page(),
    per_page: this.per_page(),
    sort: this.sort(),
    direction: this.direction(),
  }));

  protected readonly searchBuyers = this.facade.searchBuyers;

  protected readonly columns = settledContractColumns;
  protected readonly rows = computed(() => this.settledContracts()?.data ?? []);
  protected readonly meta = computed(() => this.settledContracts()?.meta);
  protected readonly pageSizeOptions = paginatedSizes;
  protected readonly rowLink = (c: SettledContract): (string | number)[] => ['/zmluvy', c.id];

  protected readonly filterForm = this.facade.getInitialFilterValues();

  private readonly state = this.facade.connectSettledContracts(this.pageState, this.filterForm);

  protected readonly settledContracts = this.state.settledContracts;
  protected readonly hasActiveFilters = this.state.hasActiveFilters;

  protected readonly pageHeaderData = computed<PageHeaderData>(() => {
    const kpis = this.kpis();

    return {
      ...SETTLED_CONTRACTS_PAGE_CONFIG,
      kpis: kpis ? this.facade.toKpiCards(kpis) : undefined,
      loading: !kpis,
    };
  });

  protected readonly sortState = computed<Sort | undefined>(() => {
    const active = this.sort();

    return active ? { active, direction: this.direction() ?? 'asc' } : undefined;
  });

  protected onPageChange(event: PageEvent): void {
    void this.router.navigate([], {
      queryParams: { page: event.pageIndex + 1, per_page: event.pageSize },
      queryParamsHandling: 'merge',
    });
  }

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
}
