import { computed, effect, inject, Service, Signal, linkedSignal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed, toSignal, rxResource } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import { debounceTime, distinctUntilChanged, filter, map, Observable } from 'rxjs';
import { NoticeKpiResource, NoticeService, FilterService } from '@generated';
import { NoticeKpisModel } from '@shared/facades/notice-facade/models/notice-kpis.model';
import {
  Notice,
  NoticeFilterForm,
  NoticeFilterParams,
  NoticeFilterValues,
  NoticeQueryParams,
  NoticeSort,
} from '@shared/models/notices.model';
import { PageHeaderKpi } from '@shared/ui/page-header/models/page-header.model';
import { PageParams, Paginated } from '@shared/config/tables/models/paginated.model';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';
import { filtersEqual } from '@shared/utils/filters-equal.util';
import { Params } from '@angular/router';
import { KPI_PLACEHOLDER } from '@shared/ui/page-header/models/page-header.model';

@Service()
export class NoticeFacade {
  private readonly noticeService = inject(NoticeService);
  private readonly filterService = inject(FilterService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly kpisResource = rxResource({
    stream: () => this.getKpis(),
  });

  private readonly kpisState = {
    kpis: computed(() => (this.kpisResource.hasValue() ? this.kpisResource.value() : undefined)),
    loading: this.kpisResource.isLoading,
    error: computed(() => this.kpisResource.error() !== undefined),
    reload: () => this.kpisResource.reload(),
  };

  public getInitialFilterValues(): NoticeFilterForm {
    const params = this.route.snapshot.queryParamMap;

    return new FormGroup({
      search: new FormControl(params.get('search') ?? '', { nonNullable: true }),
      notice_type: new FormControl(this.queryValues('notice_type', params), { nonNullable: true }),
      form_type: new FormControl(this.queryValues('form_type', params), { nonNullable: true }),
      procedure_id: new FormControl<number | null>(this.queryNumber('procedure_id', params)),
      is_latest: new FormControl<boolean | null>(this.queryBoolean('is_latest', params)),
      published_from: new FormControl<string | Date | null>(params.get('published_from') ?? '', {
        nonNullable: true,
      }),
      published_to: new FormControl<string | Date | null>(params.get('published_to') ?? '', {
        nonNullable: true,
      }),
    });
  }

  private toQueryParams(v: NoticeFilterValues): Params {
    return {
      search: v.search || null,
      'notice_type[]': v.notice_type.length ? v.notice_type : null,
      'form_type[]': v.form_type.length ? v.form_type : null,
      procedure_id: v.procedure_id ?? null,
      is_latest: v.is_latest ?? null,
      published_from: this.emptyToNull(v.published_from),
      published_to: this.emptyToNull(v.published_to),
      page: null,
    };
  }

  public connectNotices(
    pageState: Signal<PageParams<NoticeSort>>,
    filterForm: NoticeFilterForm,
  ): {
    notices: Signal<Paginated<Notice> | undefined>;
    loading: Signal<boolean>;
    error: Signal<boolean>;
    reload: () => boolean;
    hasActiveFilters: Signal<boolean>;
  } {
    const queryFilters = toSignal(
      this.route.queryParamMap.pipe(
        map((params): NoticeFilterValues => ({
          search: params.get('search') ?? '',
          notice_type: this.queryValues('notice_type', params),
          form_type: this.queryValues('form_type', params),
          procedure_id: this.queryNumber('procedure_id', params),
          is_latest: this.queryBoolean('is_latest', params),
          published_from: params.get('published_from') ?? '',
          published_to: params.get('published_to') ?? '',
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
      .subscribe((value) => {
        void this.router.navigate([], {
          queryParams: this.toQueryParams(value),
          queryParamsHandling: 'merge',
        });
      });

    const filterParams = computed(() => this.toFilterParams(queryFilters()));
    const requestParams = computed<NoticeQueryParams>(() => ({
      ...pageState(),
      ...filterParams(),
    }));

    const noticesResource = rxResource({
      params: requestParams,
      stream: ({ params }) => this.getAllNotices(params),
    });

    const notices = linkedSignal<Paginated<Notice> | undefined, Paginated<Notice> | undefined>({
      source: () => (noticesResource.hasValue() ? noticesResource.value() : undefined),
      computation: (value, previous) => value ?? previous?.value,
    });

    return {
      notices,
      loading: noticesResource.isLoading,
      error: computed(() => noticesResource.error() !== undefined),
      reload: () => noticesResource.reload(),
      hasActiveFilters: computed(() => {
        const f = filterParams();

        return (
          f.search !== undefined ||
          f['notice_type[]'] !== undefined ||
          f['form_type[]'] !== undefined ||
          f.procedure_id !== undefined ||
          f.is_latest !== undefined ||
          f.published_from !== undefined ||
          f.published_to !== undefined
        );
      }),
    };
  }

  public getKpis(): Observable<NoticeKpiResource> {
    const response$: Observable<NoticeKpisModel> = this.noticeService.noticeKpis();

    return response$.pipe(map(({ data }) => data));
  }

  public connectKpis(): typeof this.kpisState {
    return this.kpisState;
  }

  public getAllNotices(params: NoticeQueryParams): Observable<Paginated<Notice>> {
    return this.noticeService.noticesIndex(params).pipe(
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

  public toKpiCards(kpis?: NoticeKpiResource): PageHeaderKpi[] {
    const nf = new Intl.NumberFormat('sk-SK');
    const pf = new Intl.NumberFormat('sk-SK', { maximumFractionDigits: 1 });
    const count = (value?: number): string =>
      value === undefined ? KPI_PLACEHOLDER : nf.format(value);
    const decimal = (value?: number): string =>
      value === undefined ? KPI_PLACEHOLDER : pf.format(value);
    const percent = (value?: number | null): string =>
      value === undefined || value === null ? KPI_PLACEHOLDER : `${pf.format(value)} %`;

    return [
      { label: 'Oznámenia celkom', value: count(kpis?.notices.total), icon: 'description' },
      { label: 'Časti zákaziek', value: count(kpis?.lots.total), icon: 'layers' },
      {
        label: 'Úspešnosť pridelenia',
        value: percent(kpis?.award_rate.percent),
        icon: 'check_circle',
      },
      {
        label: 'Priemer ponúk na časť',
        value: decimal(kpis?.competition.avg_bids_per_lot),
        icon: 'groups',
      },
      {
        label: 'Financované z EÚ',
        value: percent(kpis?.eu_funding.percent),
        icon: 'euro',
      },
    ];
  }

  private toFilterParams({
    search,
    notice_type: noticeType,
    form_type: formType,
    procedure_id: procedureId,
    is_latest: isLatest,
    published_from: publishedFrom,
    published_to: publishedTo,
  }: NoticeFilterValues): NoticeFilterParams {
    return {
      search: search || undefined,
      'notice_type[]': noticeType.length ? noticeType : undefined,
      'form_type[]': formType.length ? formType : undefined,
      procedure_id: procedureId ?? undefined,
      is_latest: isLatest ?? undefined,
      published_from: this.normalizeDate(publishedFrom) || undefined,
      published_to: this.normalizeDate(publishedTo) || undefined,
    };
  }

  private normalizeFilterValues(value: Partial<NoticeFilterValues>): NoticeFilterValues {
    return {
      search: value.search ?? '',
      notice_type: value.notice_type ?? [],
      form_type: value.form_type ?? [],
      procedure_id: value.procedure_id ?? null,
      is_latest: value.is_latest ?? null,
      published_from: this.normalizeDate(value.published_from),
      published_to: this.normalizeDate(value.published_to),
    };
  }

  private normalizeDate(value: unknown): string {
    if (typeof value === 'string') {
      const dateParts = value.split('-');

      if (
        dateParts.length === 3 &&
        dateParts[0].length === 4 &&
        dateParts[1].length === 2 &&
        dateParts[2].length === 2 &&
        dateParts.every((part) => Number.isInteger(Number(part)))
      ) {
        return value;
      }

      const parsed = new Date(value);

      if (!Number.isNaN(parsed.getTime())) {
        value = parsed;
      } else {
        return '';
      }
    }

    if (value instanceof Date && !Number.isNaN(value.getTime())) {
      const year = value.getFullYear();
      const month = String(value.getMonth() + 1).padStart(2, '0');
      const day = String(value.getDate()).padStart(2, '0');

      return `${year.toString()}-${month}-${day}`;
    }

    return '';
  }

  private emptyToNull<T extends string | Date | null>(value: T): T | null {
    return value === '' ? null : value;
  }

  private queryValues(
    key: 'notice_type' | 'form_type',
    params = this.route.snapshot.queryParamMap,
  ): string[] {
    return params.getAll(key).length ? params.getAll(key) : params.getAll(`${key}[]`);
  }

  private queryNumber(
    key: 'procedure_id',
    params = this.route.snapshot.queryParamMap,
  ): number | null {
    const raw = params.get(key);

    if (!raw) {
      return null;
    }

    const parsed = Number(raw);

    return Number.isFinite(parsed) ? parsed : null;
  }

  private queryBoolean(
    key: 'is_latest',
    params = this.route.snapshot.queryParamMap,
  ): boolean | null {
    const raw = params.get(key);

    if (raw === 'true' || raw === '1') {
      return true;
    }

    if (raw === 'false' || raw === '0') {
      return false;
    }

    return null;
  }

  public getNoticeTypes(): Observable<FilterOption[]> {
    return this.filterService.codelistsNoticeTypes().pipe(
      map(({ data }) =>
        data.map(({ code, label_sk: label }) => ({
          value: code,
          label,
        })),
      ),
    );
  }

  public getFormTypes(): Observable<FilterOption[]> {
    return this.filterService.codelistsFormTypes().pipe(
      map(({ data }) =>
        data.map(({ code, label_sk: label }) => ({
          value: code,
          label,
        })),
      ),
    );
  }
}
