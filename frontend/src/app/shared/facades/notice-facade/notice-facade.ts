import { computed, DestroyRef, effect, inject, Service, Signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed, toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup } from '@angular/forms';
import { debounceTime, distinctUntilChanged, map, Observable, switchMap } from 'rxjs';
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
import { PageHeaderKpi } from '@shared/ui/page-header/page-header';
import { PageParams, Paginated } from '@shared/config/tables/models/paginated.model';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';

@Service()
export class NoticeFacade {
  private readonly noticeService = inject(NoticeService);
  private readonly filterService = inject(FilterService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

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

  public connectNotices(
    pageState: Signal<PageParams<NoticeSort>>,
    filterForm: NoticeFilterForm,
  ): {
    notices: Signal<Paginated<Notice> | undefined>;
    hasActiveFilters: Signal<boolean>;
  } {
    const destroyRef = inject(DestroyRef);

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
      .subscribe(
        ({
          search,
          notice_type: noticeType,
          form_type: formType,
          procedure_id: procedureId,
          is_latest: isLatest,
          published_from: publishedFrom,
          published_to: publishedTo,
        }) => {
          void this.router.navigate([], {
            queryParams: {
              search: search || null,
              'notice_type[]': noticeType.length ? noticeType : null,
              'form_type[]': formType.length ? formType : null,
              procedure_id: procedureId ?? null,
              is_latest: isLatest ?? null,
              published_from: publishedFrom ?? null,
              published_to: publishedTo ?? null,
              page: null,
            },
            queryParamsHandling: 'merge',
          });
        },
      );

    const filterParams = computed(() => this.toFilterParams(queryFilters()));
    const requestParams = computed<NoticeQueryParams>(() => ({
      ...pageState(),
      ...filterParams(),
    }));

    return {
      notices: toSignal(
        toObservable(requestParams).pipe(switchMap((params) => this.getAllNotices(params))),
      ),
      hasActiveFilters: computed(() => {
        const f = filterParams();

        return [
          f.search?.trim(),
          f['notice_type[]']?.length,
          f['form_type[]']?.length,
          f.procedure_id !== undefined,
          f.is_latest !== undefined,
          f.published_from,
          f.published_to,
        ].some(Boolean);
      }),
    };
  }

  public getKpis(): Observable<NoticeKpiResource> {
    const response$: Observable<NoticeKpisModel> = this.noticeService.noticeKpis();

    return response$.pipe(map(({ data }) => data));
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

  public toKpiCards(kpis: NoticeKpiResource): PageHeaderKpi[] {
    const nf = new Intl.NumberFormat('sk-SK');
    const pf = new Intl.NumberFormat('sk-SK', { maximumFractionDigits: 1 });

    return [
      {
        label: 'Oznámenia celkom',
        value: nf.format(kpis.notices.total),
        icon: 'description',
      },
      {
        label: 'Časti zákaziek',
        value: nf.format(kpis.lots.total),
        icon: 'layers',
      },
      {
        label: 'Úspešnosť pridelenia',
        value: kpis.award_rate.percent !== null ? `${pf.format(kpis.award_rate.percent)} %` : '—',
        icon: 'check_circle',
      },
      {
        label: 'Priemer ponúk na časť',
        value: pf.format(kpis.competition.avg_bids_per_lot),
        icon: 'groups',
      },
      {
        label: 'Financované z EÚ',
        value: kpis.eu_funding.percent !== null ? `${pf.format(kpis.eu_funding.percent)} %` : '—',
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
