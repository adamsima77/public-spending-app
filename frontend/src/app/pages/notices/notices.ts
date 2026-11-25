import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  numberAttribute,
} from '@angular/core';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { Router } from '@angular/router';
import { PageEvent } from '@angular/material/paginator';
import { Sort } from '@angular/material/sort';
import { DataTable } from '@shared/ui/data-table/data-table';
import { PageHeaderData } from '@shared/ui/page-header/models/page-header.model';
import { NoticeFacade } from '@shared/facades/notice-facade/notice-facade';
import { NOTICE_PAGE_CONFIG } from '@shared/config/page-headers/notice-header.config';
import { NoticeFilters } from '@components/ui/notice-filters/notice-filters';
import { NOTICE_COLUMNS } from '@shared/config/tables/notice-table.config';
import { PageParams } from '@shared/config/tables/models/paginated.model';
import { paginatedSizes } from '@shared/config/tables/paginated-sizes.config';
import { Notice, NoticeSort } from '@shared/models/notices.model';
import { PageCardShellComponent } from '@shared/ui/wrappers/page-card-shell.component/page-card-shell.component';

@Component({
  imports: [PageCardShellComponent, DataTable, NoticeFilters],
  selector: 'app-notices',
  styleUrl: './notices.scss',
  templateUrl: './notices.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Notices {
  private readonly noticeFacade = inject(NoticeFacade);
  private readonly router = inject(Router);

  readonly page = input(1, { transform: (v: unknown): number => numberAttribute(v, 1) });
  readonly per_page = input(25, { transform: (v: unknown): number => numberAttribute(v, 25) });
  readonly sort = input<NoticeSort>();
  readonly direction = input<'asc' | 'desc' | null>(null);

  private readonly pageState = computed<PageParams<NoticeSort>>(() => ({
    page: this.page(),
    per_page: this.per_page(),
    sort: this.sort(),
    direction: this.direction(),
  }));

  protected readonly columns = NOTICE_COLUMNS;
  protected readonly rows = computed(() => this.notices()?.data ?? []);
  protected readonly meta = computed(() => this.notices()?.meta);
  protected readonly pageSizeOptions = paginatedSizes;
  protected readonly rowLink = (notice: Notice): (string | number)[] => ['/oznamenia', notice.id];
  protected readonly rowKey = (notice: Notice): number => notice.id;
  protected readonly noticeTypeFilters = toSignal(this.noticeFacade.getNoticeTypes(), {
    initialValue: [],
  });

  protected readonly formTypeFilters = toSignal(this.noticeFacade.getFormTypes(), {
    initialValue: [],
  });

  protected readonly filterForm = this.noticeFacade.getInitialFilterValues();

  private readonly noticeState = this.noticeFacade.connectNotices(this.pageState, this.filterForm);

  protected readonly notices = this.noticeState.notices;
  protected readonly loading = this.noticeState.loading;
  protected readonly hasActiveFilters = this.noticeState.hasActiveFilters;

  private readonly kpisResource = rxResource({
    stream: () => this.noticeFacade.getKpis(),
  });

  protected readonly pageHeaderData = computed<PageHeaderData>(() => {
    const kpis = this.kpisResource.hasValue() ? this.kpisResource.value() : undefined;

    return {
      ...NOTICE_PAGE_CONFIG,
      kpis: this.noticeFacade.toKpiCards(kpis),
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
