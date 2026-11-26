import { Component, computed, inject, input, output } from '@angular/core';
import { PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { TableColumn } from '@shared/config/tables/models/table-column.model';
import { PageMeta } from '@shared/config/tables/models/paginated.model';
import { ElementRef } from '@angular/core';
import { MatSortModule, Sort } from '@angular/material/sort';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { ProgressBar } from '@shared/ui/loaders/progress-bar/progress-bar';

@Component({
  imports: [
    ProgressBar,
    MatButtonModule,
    MatCardModule,
    RouterLink,
    MatPaginatorModule,
    MatProgressBarModule,
    MatTableModule,
    MatSortModule,
    MatIconModule,
  ],
  selector: 'app-data-table',
  styleUrl: './data-table.scss',
  templateUrl: './data-table.html',
})
export class DataTable<T> {
  readonly columns = input.required<TableColumn<T>[]>();
  readonly rows = input.required<T[]>();
  readonly loading = input(false);
  readonly error = input(false);
  readonly reload = input.required<() => boolean>();
  readonly rowKey = input<(row: T) => string | number>();
  protected readonly trackRow = (index: number, row: T): string | number =>
    this.rowKey()?.(row) ?? index;

  protected readonly minTableHeight = computed(() => 44 + (this.meta()?.perPage ?? 10) * 56);

  readonly meta = input<PageMeta>();
  readonly pageChange = output<PageEvent>();
  readonly rowLink = input<(row: T) => string | unknown[]>();

  protected readonly displayedColumns = computed(() => this.columns().map((c) => c.key));
  readonly pageSizeOptions = input([10, 25, 50, 100]);

  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);

  protected onPage(event: PageEvent): void {
    this.pageChange.emit(event);
    this.host.nativeElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  readonly sort = input<Sort>();
  readonly sortChange = output<Sort>();
}
