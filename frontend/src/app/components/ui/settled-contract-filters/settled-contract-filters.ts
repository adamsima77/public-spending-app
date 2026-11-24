import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { startWith, switchMap } from 'rxjs';
import { FilterBar } from '@shared/ui/filters/filter-bar/filter-bar';
import { SearchField } from '@shared/ui/filters/search-field/search-field';
import { FilterChips } from '@shared/ui/filters/filter-chips/filter-chips';
import { FilterDateRange } from '@shared/ui/filters/filter-date-range/filter-date-range';
import { FilterAutocomplete } from '@shared/ui/filters/filter-autocomplete/filter-autocomplete';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';
import { BuyerFilter } from '@shared/models/settled-contracts.model';
import { SettledContractFilterForm } from '@shared/models/settled-contracts.model';

@Component({
  selector: 'app-settled-contract-filters',
  imports: [FilterBar, SearchField, FilterAutocomplete, FilterDateRange, FilterChips],
  templateUrl: './settled-contract-filters.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettledContractFilters {
  readonly form = input.required<SettledContractFilterForm>();
  readonly buyers = input.required<BuyerFilter>();

  protected readonly yesNo: FilterOption[] = [
    { value: '1', label: 'Áno' },
    { value: '0', label: 'Nie' },
  ];

  protected readonly currentOnly: FilterOption[] = [{ value: '1', label: 'Len aktuálne' }];

  private readonly value = toSignal(
    toObservable(this.form).pipe(switchMap((f) => f.valueChanges.pipe(startWith(f.value)))),
  );

  protected readonly hasActive = computed(() =>
    Object.values(this.value() ?? {}).some((v) =>
      Array.isArray(v) ? v.length > 0 : v !== null && v !== '',
    ),
  );

  protected reset(): void {
    this.form().reset({
      search: '',
      buyer_id: '',
      conclusion_from: '',
      conclusion_to: '',
      has_url: [],
      has_tenders: [],
      only_current: [],
    });
  }
}
