import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { NoticeFilterForm } from '@shared/models/notices.model';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';
import { FilterBar } from '@shared/ui/filters/filter-bar/filter-bar';
import { FilterSelect } from '@shared/ui/filters/filter-select/filter-select';
import { SearchField } from '@shared/ui/filters/search-field/search-field';
import { FilterDateRange } from '@shared/ui/filters/filter-date-range/filter-date-range';

@Component({
  imports: [
    ReactiveFormsModule,
    MatSlideToggleModule,
    FilterBar,
    SearchField,
    FilterSelect,
    FilterDateRange,
  ],
  selector: 'app-notice-filters',
  styleUrl: './notice-filters.scss',
  templateUrl: './notice-filters.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NoticeFilters {
  readonly form = input.required<NoticeFilterForm>();
  readonly noticeTypes = input.required<readonly FilterOption[]>();
  readonly formTypes = input.required<readonly FilterOption[]>();
  readonly hasActive = input(false);

  protected reset(): void {
    this.form().reset({
      search: '',
      notice_type: [],
      form_type: [],
      procedure_id: null,
      published_from: '',
      published_to: '',
    });
  }
}
