import { computed, effect, inject, Service, Signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import { Observable } from 'rxjs';
import { debounceTime, distinctUntilChanged, map, skip, startWith, switchMap, tap } from 'rxjs';
import { OrganizationKpisResponse } from './models/organization-kpi.model';
import { OrganizationService } from '../../../generated/services/organization.service';
import { OrganizationKpisResource } from '../../../generated';
import {
  Organization,
  OrganizationFilterForm,
  OrganizationFilterParams,
  OrganizationFilterValues,
  OrganizationQueryParams,
  OrganizationRole,
  OrganizationSort,
} from './models/organizations.model';
import { PageHeaderKpi } from '../../../components/ui/page-header/page-header';
import { PageParams, Paginated } from '../../../config/tables/models/paginated.model';
import { FilterService } from '../../../generated';
import { CompanySizesResponse } from './models/company-sizes.model';
import { OrganizationCountryResponse } from './models/organization-country.model';

@Service()
export class OrganizationFacade {
  private readonly organizationService = inject(OrganizationService);
  private readonly filterService = inject(FilterService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

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
    hasActiveFilters: Signal<boolean>;
  } {
    const queryFilters = toSignal(
      this.route.queryParamMap.pipe(
        map((params) => ({
          search: params.get('search') ?? '',
          country: this.queryValues('country', params),
          company_size: this.queryValues('company_size', params),
          role: this.queryValues('role', params) as OrganizationRole[],
        })),
      ),
      { initialValue: null },
    );

    effect(() => {
      const filters = queryFilters();

      if (filters) {
        filterForm.reset(filters, { emitEvent: false });
      }
    });

    const filters = toSignal<OrganizationFilterParams>(
      filterForm.valueChanges.pipe(
        startWith(filterForm.getRawValue()),
        skip(1),
        map((value) => this.normalizeFilterValues(value)),
        tap(({ search, country, company_size: companySize, role }) => {
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
        }),
        debounceTime(250),
        distinctUntilChanged(
          (previous, current) => JSON.stringify(previous) === JSON.stringify(current),
        ),
        map((value) => this.toFilterParams(value)),
      ),
      { initialValue: undefined },
    );
    const filterParams = computed<OrganizationFilterParams>(
      () =>
        filters() ?? {
          search: undefined,
          'country[]': undefined,
          'company_size[]': undefined,
          'role[]': undefined,
        },
    );
    const requestParams = computed<OrganizationQueryParams>(() => ({
      ...pageState(),
      ...filterParams(),
    }));

    return {
      organizations: toSignal(
        toObservable(requestParams).pipe(switchMap((params) => this.getAllOrganizations(params))),
      ),
      hasActiveFilters: computed(() => {
        const activeFilters = filterParams();

        return [
          activeFilters.search?.trim(),
          activeFilters['country[]']?.length,
          activeFilters['company_size[]']?.length,
          activeFilters['role[]']?.length,
        ].some(Boolean);
      }),
    };
  }

  public getOrganizationKpis(): Observable<OrganizationKpisResource> {
    const response$: Observable<OrganizationKpisResponse> =
      this.organizationService.organizationKpis();

    return response$.pipe(map(({ data }) => data));
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

  public toKpiCards(kpis: OrganizationKpisResource): PageHeaderKpi[] {
    const nf = new Intl.NumberFormat('sk-SK');

    return [
      { label: 'Organizácie', value: nf.format(kpis.total_organizations), icon: 'business' },
      { label: 'Obstarávatelia', value: nf.format(kpis.buyers), icon: 'account_balance' },
      { label: 'Dodávatelia', value: nf.format(kpis.suppliers), icon: 'local_shipping' },
      { label: 'Krajiny', value: nf.format(kpis.countries), icon: 'public' },
      {
        label: 'Podiel MSP medzi dodávateľmi',
        value: kpis.sme_suppliers_pct !== null ? `${kpis.sme_suppliers_pct.toString()} %` : '-',
        icon: 'storefront',
      },
    ];
  }

  public getCompanySizes(): Observable<CompanySizesResponse> {
    return this.filterService.codelistsCompanySizes();
  }

  public getOrganizationCountries(): Observable<OrganizationCountryResponse> {
    return this.filterService.codelistsOrganizationCountries();
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
