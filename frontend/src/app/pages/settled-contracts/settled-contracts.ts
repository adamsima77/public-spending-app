import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  numberAttribute,
} from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { PageEvent } from '@angular/material/paginator';
import { Sort } from '@angular/material/sort';
import { Router } from '@angular/router';
import { PageHeaderData } from '@shared/ui/page-header/models/page-header.model';
import { SettledContractFacade } from '@shared/facades/settled-contract-facade/settled-contract-facade';
import { SETTLED_CONTRACTS_PAGE_CONFIG } from '@shared/config/page-headers/settled-contract-header.config';
import { DataTable } from '@shared/ui/data-table/data-table';
import { settledContractColumns } from '@shared/config/tables/settled-contract-table.config';
import { PageParams } from '@shared/config/tables/models/paginated.model';
import { paginatedSizes } from '@shared/config/tables/paginated-sizes.config';
import { SettledContract, SettledContractSort } from '@shared/models/settled-contracts.model';
import { SettledContractFilters } from '@components/ui/settled-contract-filters/settled-contract-filters';
import { PageCardShellComponent } from '@shared/ui/wrappers/page-card-shell.component/page-card-shell.component';

@Component({
  imports: [PageCardShellComponent, DataTable, SettledContractFilters],
  selector: 'app-settled-contracts',
  styleUrl: './settled-contracts.scss',
  templateUrl: './settled-contracts.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettledContracts {
  private readonly facade = inject(SettledContractFacade);
  private readonly router = inject(Router);

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

  protected readonly columns = settledContractColumns;
  protected readonly rows = computed(() => this.settledContracts()?.data ?? []);
  protected readonly meta = computed(() => this.settledContracts()?.meta);
  protected readonly pageSizeOptions = paginatedSizes;
  protected readonly rowLink = (c: SettledContract): (string | number)[] => ['/zmluvy', c.id];
  protected readonly rowKey = (c: SettledContract): number => c.id;
  protected readonly filterForm = this.facade.getInitialFilterValues();

  private readonly state = this.facade.connectSettledContracts(this.pageState, this.filterForm);

  protected readonly settledContracts = this.state.settledContracts;
  protected readonly loading = this.state.loading;
  protected readonly hasActiveFilters = this.state.hasActiveFilters;
  protected readonly buyers = this.state.buyers;

  private readonly kpisResource = rxResource({
    stream: () => this.facade.getSettledContractKpis(),
  });

  protected readonly pageHeaderData = computed<PageHeaderData>(() => {
    const kpis = this.kpisResource.hasValue() ? this.kpisResource.value() : undefined;

    return {
      ...SETTLED_CONTRACTS_PAGE_CONFIG,
      kpis: this.facade.toKpiCards(kpis),
      loading: this.kpisResource.isLoading(),
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
