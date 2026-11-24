import { computed, DestroyRef, effect, inject, Service, Signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed, toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import {
  debounceTime,
  distinctUntilChanged,
  map,
  Observable,
  switchMap,
  of,
  catchError,
} from 'rxjs';
import { SettledContractService, SettledContractKpiResource } from '@generated';
import {
  SettledContract,
  SettledContractFilterForm,
  SettledContractFilterParams,
  SettledContractFilterValues,
  SettledContractQueryParams,
  SettledContractSort,
} from '@shared/models/settled-contracts.model';
import { PageHeaderKpi } from '@shared/ui/page-header/models/page-header.model';
import { PageParams, Paginated } from '@shared/config/tables/models/paginated.model';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';
import { FilterService } from '@generated';

@Service()
export class SettledContractFacade {
  private readonly settledContractService = inject(SettledContractService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly filterService = inject(FilterService);

  public getInitialFilterValues(): SettledContractFilterForm {
    const params = this.route.snapshot.queryParamMap;

    return new FormGroup({
      search: new FormControl(params.get('search') ?? '', { nonNullable: true }),
      buyer_id: new FormControl(params.get('buyer_id') ?? '', { nonNullable: true }),
      conclusion_from: new FormControl<string | Date | null>(params.get('conclusion_from') ?? '', {
        nonNullable: true,
      }),
      conclusion_to: new FormControl<string | Date | null>(params.get('conclusion_to') ?? '', {
        nonNullable: true,
      }),
      has_url: new FormControl(params.getAll('has_url'), { nonNullable: true }),
      has_tenders: new FormControl(params.getAll('has_tenders'), { nonNullable: true }),
      only_current: new FormControl(params.getAll('only_current'), { nonNullable: true }),
    });
  }

  public connectSettledContracts(
    pageState: Signal<PageParams<SettledContractSort>>,
    filterForm: SettledContractFilterForm,
  ): {
    settledContracts: Signal<Paginated<SettledContract> | undefined>;
    hasActiveFilters: Signal<boolean>;
  } {
    const destroyRef = inject(DestroyRef);

    const queryFilters = toSignal(
      this.route.queryParamMap.pipe(
        map((params): SettledContractFilterValues => ({
          search: params.get('search') ?? '',
          buyer_id: params.get('buyer_id') ?? '',
          conclusion_from: params.get('conclusion_from') ?? '',
          conclusion_to: params.get('conclusion_to') ?? '',
          has_url: params.getAll('has_url'),
          has_tenders: params.getAll('has_tenders'),
          only_current: params.getAll('only_current'),
        })),
        distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      ),
      { requireSync: true },
    );

    effect(() => {
      const filters = queryFilters();

      if (
        JSON.stringify(filters) !==
        JSON.stringify(this.normalizeFilterValues(filterForm.getRawValue()))
      ) {
        filterForm.reset(filters, { emitEvent: false });
      }
    });

    filterForm.valueChanges
      .pipe(
        map((value) => this.normalizeFilterValues(value)),
        debounceTime(250),
        distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
        takeUntilDestroyed(destroyRef),
      )
      .subscribe((v) => {
        void this.router.navigate([], {
          queryParams: {
            search: v.search || null,
            buyer_id: v.buyer_id || null,
            conclusion_from: v.conclusion_from ?? null,
            conclusion_to: v.conclusion_to ?? null,
            has_url: v.has_url.length ? v.has_url : null,
            has_tenders: v.has_tenders.length ? v.has_tenders : null,
            only_current: v.only_current.length ? v.only_current : null,
            page: null,
          },
          queryParamsHandling: 'merge',
        });
      });

    const filterParams = computed(() => this.toFilterParams(queryFilters()));
    const requestParams = computed<SettledContractQueryParams>(() => ({
      ...pageState(),
      ...filterParams(),
    }));

    return {
      settledContracts: toSignal(
        toObservable(requestParams).pipe(
          switchMap((params) => this.getAllSettledContracts(params)),
        ),
      ),
      hasActiveFilters: computed(() => Object.values(filterParams()).some((v) => v !== null)),
    };
  }

  public getSettledContractKpis(): Observable<SettledContractKpiResource> {
    return this.settledContractService.settledContractKpis().pipe(map(({ data }) => data));
  }

  public getAllSettledContracts(
    params: SettledContractQueryParams,
  ): Observable<Paginated<SettledContract>> {
    return this.settledContractService.settledContractIndex(params).pipe(
      map(({ data, meta }) => ({
        data,
        meta: {
          total: meta.total,
          currentPage: meta.current_page,
          perPage: meta.per_page,
          lastPage: meta.last_page,
        },
      })),
    );
  }

  public toKpiCards(kpis: SettledContractKpiResource): PageHeaderKpi[] {
    const nf = new Intl.NumberFormat('sk-SK');
    const pf = new Intl.NumberFormat('sk-SK', { maximumFractionDigits: 1 });
    const change = Number(kpis.contracts.change_pct);
    const changeLabel = Number.isFinite(change)
      ? ` (${change > 0 ? '+' : ''}${pf.format(change)} %)`
      : '';

    return [
      { label: 'Zmluvy', value: nf.format(kpis.contracts.total), icon: 'description' },
      {
        label: `Za posledných 30 dní${changeLabel}`,
        value: nf.format(kpis.contracts.last_30),
        icon: 'trending_up',
      },
      {
        label: 'S odkazom na zmluvu',
        value: `${pf.format(kpis.coverage.with_url_pct)} %`,
        icon: 'link',
      },
      {
        label: 'Prepojené s ponukami',
        value: `${pf.format(kpis.coverage.with_tenders_pct)} %`,
        icon: 'account_tree',
      },
      { label: 'Obstarávatelia', value: nf.format(kpis.reach.buyers), icon: 'account_balance' },
    ];
  }

  private toFilterParams(v: SettledContractFilterValues): SettledContractFilterParams {
    return {
      search: v.search || undefined,
      buyer_id: v.buyer_id ? Number(v.buyer_id) : undefined,
      conclusion_from: this.normalizeDate(v.conclusion_from) || undefined,
      conclusion_to: this.normalizeDate(v.conclusion_to) || undefined,
      has_url: this.toFlag(v.has_url),
      has_tenders: this.toFlag(v.has_tenders),
      only_current: v.only_current.length ? true : undefined,
    };
  }

  private toFlag(values: string[]): boolean | undefined {
    return values.length === 1 ? values[0] === '1' : undefined;
  }

  private normalizeFilterValues(
    value: Partial<SettledContractFilterValues>,
  ): SettledContractFilterValues {
    return {
      search: value.search ?? '',
      buyer_id: value.buyer_id ?? '',
      conclusion_from: this.normalizeDate(value.conclusion_from),
      conclusion_to: this.normalizeDate(value.conclusion_to),
      has_url: value.has_url ?? [],
      has_tenders: value.has_tenders ?? [],
      only_current: value.only_current ?? [],
    };
  }

  private normalizeDate(value: unknown): string {
    if (typeof value === 'string') {
      const parts = value.split('-');

      if (
        parts.length === 3 &&
        parts[0].length === 4 &&
        parts[1].length === 2 &&
        parts[2].length === 2 &&
        parts.every((part) => Number.isInteger(Number(part)))
      ) {
        return value;
      }

      const parsed = new Date(value);

      if (Number.isNaN(parsed.getTime())) {
        return '';
      }

      value = parsed;
    }

    if (value instanceof Date && !Number.isNaN(value.getTime())) {
      const year = value.getFullYear();
      const month = String(value.getMonth() + 1).padStart(2, '0');
      const day = String(value.getDate()).padStart(2, '0');

      return `${year.toString()}-${month}-${day}`;
    }

    return '';
  }

  public getBuyers(search = '', selectedId: number | null = null): Observable<FilterOption[]> {
    return this.filterService
      .codelistsBuyers({ search: search || undefined, selected_id: selectedId ?? undefined })
      .pipe(
        map(({ data }) => data.map(({ id, name }) => ({ value: id, label: name }))),
        catchError(() => of([])),
      );
  }

  public readonly searchBuyers = (query: string, selectedId: string): Observable<FilterOption[]> =>
    this.getBuyers(query, selectedId ? Number(selectedId) : null);
}
