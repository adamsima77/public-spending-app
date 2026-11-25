import { computed, effect, inject, linkedSignal, Service, signal, Signal } from '@angular/core';
import { ActivatedRoute, Router, Params } from '@angular/router';
import { rxResource, takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import {
  debounceTime,
  distinctUntilChanged,
  map,
  Observable,
  switchMap,
  of,
  catchError,
  timer,
  filter,
  tap,
} from 'rxjs';
import { SettledContractService, SettledContractKpiResource } from '@generated';
import {
  BuyerFilter,
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
import { filtersEqual } from '@shared/utils/filters-equal.util';
import { KPI_PLACEHOLDER } from '@shared/ui/page-header/models/page-header.model';

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
    loading: Signal<boolean>;
    error: Signal<boolean>;
    reload: () => boolean;
    hasActiveFilters: Signal<boolean>;
    buyers: BuyerFilter;
  } {
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
        distinctUntilChanged(filtersEqual),
      ),
      { requireSync: true },
    );

    effect(() => {
      const filters = queryFilters();

      if (!filtersEqual(filters, this.normalizeFilterValues(filterForm.getRawValue()))) {
        filterForm.reset(filters, { emitEvent: false });
      }
    });

    filterForm.valueChanges
      .pipe(
        map((value) => this.normalizeFilterValues(value)),
        debounceTime(250),
        filter((value) => !filtersEqual(value, queryFilters())),
        tap((value) => {
          void this.router.navigate([], {
            queryParams: this.toQueryParams(value),
            queryParamsHandling: 'merge',
          });
        }),
        takeUntilDestroyed(),
      )
      .subscribe();

    const buyerId = computed(() => queryFilters().buyer_id);
    const buyerQuery = signal('');

    const buyerOptionsResource = rxResource({
      params: buyerQuery,
      stream: ({ params }) =>
        timer(250).pipe(
          switchMap(() => this.getBuyers(params, buyerId() ? Number(buyerId()) : null)),
        ),
    });

    const buyerOptions = linkedSignal<FilterOption[] | undefined, FilterOption[]>({
      source: buyerOptionsResource.value,
      computation: (value, previous) => value ?? previous?.value ?? [],
    });

    const selectedBuyerResource = rxResource({
      params: () => buyerId() || undefined,
      stream: ({ params: id }) =>
        this.getBuyers('', Number(id)).pipe(
          map((opts) => opts.find((o) => o.value === id) ?? null),
        ),
    });

    const selectedBuyer = linkedSignal<FilterOption | null | undefined, FilterOption | null>({
      source: selectedBuyerResource.value,
      computation: (value, previous) => (buyerId() ? (value ?? previous?.value ?? null) : null),
    });

    const buyers: BuyerFilter = {
      options: buyerOptions,
      selected: selectedBuyer,
      onQuery: (query) => {
        buyerQuery.set(query);
      },
    };

    const filterParams = computed(() => this.toFilterParams(queryFilters()));
    const requestParams = computed<SettledContractQueryParams>(() => ({
      ...pageState(),
      ...filterParams(),
    }));

    const settledContractsResource = rxResource({
      params: requestParams,
      stream: ({ params }) => this.getAllSettledContracts(params),
    });

    const settledContracts = linkedSignal<
      Paginated<SettledContract> | undefined,
      Paginated<SettledContract> | undefined
    >({
      source: () =>
        settledContractsResource.hasValue() ? settledContractsResource.value() : undefined,
      computation: (value, previous) => value ?? previous?.value,
    });

    return {
      settledContracts,
      loading: settledContractsResource.isLoading,
      error: computed(() => settledContractsResource.error() !== undefined),
      reload: () => settledContractsResource.reload(),
      hasActiveFilters: computed(() => {
        const f = filterParams();

        return (
          f.search !== undefined ||
          f.buyer_id !== undefined ||
          f.conclusion_from !== undefined ||
          f.conclusion_to !== undefined ||
          f.has_url !== undefined ||
          f.has_tenders !== undefined ||
          f.only_current !== undefined
        );
      }),
      buyers,
    };
  }

  private toQueryParams(v: SettledContractFilterValues): Params {
    return {
      search: this.emptyToNull(v.search),
      buyer_id: this.emptyToNull(v.buyer_id),
      conclusion_from: this.emptyToNull(v.conclusion_from),
      conclusion_to: this.emptyToNull(v.conclusion_to),
      has_url: v.has_url.length ? v.has_url : null,
      has_tenders: v.has_tenders.length ? v.has_tenders : null,
      only_current: v.only_current.length ? v.only_current : null,
      page: null,
    };
  }

  private emptyToNull<T extends string | Date | null>(value: T): T | null {
    return value === '' ? null : value;
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

  public toKpiCards(kpis?: SettledContractKpiResource): PageHeaderKpi[] {
    const nf = new Intl.NumberFormat('sk-SK');
    const pf = new Intl.NumberFormat('sk-SK', { maximumFractionDigits: 1 });
    const count = (value?: number): string =>
      value === undefined ? KPI_PLACEHOLDER : nf.format(value);
    const percent = (value?: number): string =>
      value === undefined ? KPI_PLACEHOLDER : `${pf.format(value)} %`;
    const change = Number(kpis?.contracts.change_pct);
    const changeLabel = Number.isFinite(change)
      ? ` (${change > 0 ? '+' : ''}${pf.format(change)} %)`
      : '';

    return [
      { label: 'Zmluvy', value: count(kpis?.contracts.total), icon: 'description' },
      {
        label: `Za posledných 30 dní${changeLabel}`,
        value: count(kpis?.contracts.last_30),
        icon: 'trending_up',
      },
      {
        label: 'S odkazom na zmluvu',
        value: percent(kpis?.coverage.with_url_pct),
        icon: 'link',
      },
      {
        label: 'Prepojené s ponukami',
        value: percent(kpis?.coverage.with_tenders_pct),
        icon: 'account_tree',
      },
      { label: 'Obstarávatelia', value: count(kpis?.reach.buyers), icon: 'account_balance' },
    ];
  }

  public getBuyers(search = '', selectedId: number | null = null): Observable<FilterOption[]> {
    return this.filterService
      .codelistsBuyers({ search: search || undefined, selected_id: selectedId ?? undefined })
      .pipe(
        map(({ data }) => data.map(({ id, name }) => ({ value: id, label: name }))),
        catchError(() => of([])),
      );
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
}
