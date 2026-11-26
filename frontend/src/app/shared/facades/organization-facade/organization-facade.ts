import { computed, effect, inject, Service, Signal, linkedSignal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed, toSignal, rxResource } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { debounceTime, distinctUntilChanged, filter, map } from 'rxjs';
import { OrganizationKpisResponse } from './models/organization-kpi.model';
import { OrganizationService, OrganizationKpisResource, FilterService } from '@generated';
import {
  Organization,
  OrganizationFilterForm,
  OrganizationFilterParams,
  OrganizationFilterValues,
  OrganizationQueryParams,
  OrganizationRole,
  OrganizationSort,
} from '@shared/models/organizations.model';
import { PageHeaderKpi } from '@shared/ui/page-header/models/page-header.model';
import { PageParams, Paginated } from '@shared/config/tables/models/paginated.model';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';
import { filtersEqual } from '@shared/utils/filters-equal.util';
import { KPI_PLACEHOLDER } from '@shared/ui/page-header/models/page-header.model';

@Service()
export class OrganizationFacade {
  private readonly organizationService = inject(OrganizationService);
  private readonly filterService = inject(FilterService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly kpisResource = rxResource({
    stream: () => this.getOrganizationKpis(),
  });

  private readonly kpisState = {
    kpis: computed(() => (this.kpisResource.hasValue() ? this.kpisResource.value() : undefined)),
    loading: this.kpisResource.isLoading,
    error: computed(() => this.kpisResource.error() !== undefined),
    reload: () => this.kpisResource.reload(),
  };

  public getInitialFilterValues(): OrganizationFilterForm {
    const params = this.route.snapshot.queryParamMap;

    return new FormGroup({
      search: new FormControl(params.get('search') ?? '', { nonNullable: true }),
      country: new FormControl(this.queryValues('country'), { nonNullable: true }),
      company_size: new FormControl(this.queryValues('company_size'), { nonNullable: true }),
      role: new FormControl(this.queryValues('role') as OrganizationRole[], { nonNullable: true }),
    });
  }

  public connectOrganizations(
    pageState: Signal<PageParams<OrganizationSort>>,
    filterForm: OrganizationFilterForm,
  ): {
    organizations: Signal<Paginated<Organization> | undefined>;
    loading: Signal<boolean>;
    error: Signal<boolean>;
    reload: () => boolean;
    hasActiveFilters: Signal<boolean>;
  } {
    const queryFilters = toSignal(
      this.route.queryParamMap.pipe(
        map((params): OrganizationFilterValues => ({
          search: params.get('search') ?? '',
          country: this.queryValues('country', params),
          company_size: this.queryValues('company_size', params),
          role: this.queryValues('role', params) as OrganizationRole[],
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
        takeUntilDestroyed(),
      )
      .subscribe(({ search, country, company_size: companySize, role }) => {
        void this.router.navigate([], {
          queryParams: {
            search: search || null,
            country: country.length ? country : null,
            company_size: companySize.length ? companySize : null,
            role: role.length ? role : null,
            page: null,
          },
          queryParamsHandling: 'merge',
        });
      });

    const filterParams = computed(() => this.toFilterParams(queryFilters()));
    const requestParams = computed<OrganizationQueryParams>(() => ({
      ...pageState(),
      ...filterParams(),
    }));

    const organizationsResource = rxResource({
      params: requestParams,
      stream: ({ params }) => this.getAllOrganizations(params),
    });

    const organizations = linkedSignal<
      Paginated<Organization> | undefined,
      Paginated<Organization> | undefined
    >({
      source: () => (organizationsResource.hasValue() ? organizationsResource.value() : undefined),
      computation: (value, previous) => value ?? previous?.value,
    });

    return {
      organizations,
      loading: organizationsResource.isLoading,
      error: computed(() => organizationsResource.error() !== undefined),
      reload: () => organizationsResource.reload(),
      hasActiveFilters: computed(() => {
        const f = filterParams();

        return [
          f.search?.trim(),
          f['country[]']?.length,
          f['company_size[]']?.length,
          f['role[]']?.length,
        ].some(Boolean);
      }),
    };
  }

  public getOrganizationKpis(): Observable<OrganizationKpisResource> {
    const response$: Observable<OrganizationKpisResponse> =
      this.organizationService.organizationKpis();

    return response$.pipe(map(({ data }) => data));
  }

  public connectKpis(): typeof this.kpisState {
    return this.kpisState;
  }

  public getAllOrganizations(params: OrganizationQueryParams): Observable<Paginated<Organization>> {
    return this.organizationService.organizationsIndex(params).pipe(
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

  public toKpiCards(kpis?: OrganizationKpisResource): PageHeaderKpi[] {
    const nf = new Intl.NumberFormat('sk-SK');
    const count = (value?: number): string =>
      value === undefined ? KPI_PLACEHOLDER : nf.format(value);
    const smePct = kpis?.sme_suppliers_pct;

    return [
      { label: 'Organizácie', value: count(kpis?.total_organizations), icon: 'business' },
      { label: 'Obstarávatelia', value: count(kpis?.buyers), icon: 'account_balance' },
      { label: 'Dodávatelia', value: count(kpis?.suppliers), icon: 'local_shipping' },
      { label: 'Krajiny', value: count(kpis?.countries), icon: 'public' },
      {
        label: 'Podiel MSP medzi dodávateľmi',
        value: smePct === undefined || smePct === null ? KPI_PLACEHOLDER : `${smePct.toString()} %`,
        icon: 'storefront',
      },
    ];
  }

  public getCompanySizes(): Observable<FilterOption[]> {
    return this.filterService.codelistsCompanySizes().pipe(
      map(({ data }) =>
        data.map(({ code, label_sk: label }) => ({
          value: code,
          label,
        })),
      ),
    );
  }

  public getOrganizationCountries(): Observable<FilterOption[]> {
    return this.filterService.codelistsOrganizationCountries().pipe(
      map(({ data }) =>
        data.map(({ name }) => ({
          value: name,
          label: name,
        })),
      ),
    );
  }

  private toFilterParams({
    search,
    country,
    company_size: companySize,
    role,
  }: OrganizationFilterValues): OrganizationFilterParams {
    return {
      search: search || undefined,
      'country[]': country.length ? country : undefined,
      'company_size[]': companySize.length ? companySize : undefined,
      'role[]': role.length ? role : undefined,
    };
  }

  private normalizeFilterValues(
    value: Partial<OrganizationFilterValues>,
  ): OrganizationFilterValues {
    return {
      search: value.search ?? '',
      country: value.country ?? [],
      company_size: value.company_size ?? [],
      role: value.role ?? [],
    };
  }

  private queryValues(
    key: 'country' | 'company_size' | 'role',
    params = this.route.snapshot.queryParamMap,
  ): string[] {
    return params.getAll(key).length ? params.getAll(key) : params.getAll(`${key}[]`);
  }
}
