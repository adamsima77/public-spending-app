import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { takeUntilDestroyed, toObservable, toSignal } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import {
  MatAutocompleteModule,
  MatAutocompleteSelectedEvent,
} from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {
  debounceTime,
  distinctUntilChanged,
  EMPTY,
  filter,
  map,
  Observable,
  of,
  startWith,
  switchMap,
} from 'rxjs';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';

@Component({
  selector: 'app-filter-autocomplete',
  imports: [ReactiveFormsModule, MatAutocompleteModule, MatFormFieldModule, MatInputModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './filter-autocomplete.html',
  styleUrl: './filter-autocomplete.scss',
})
export class FilterAutocomplete {
  readonly label = input.required<string>();
  readonly control = input.required<FormControl<string>>();
  readonly search =
    input.required<(query: string, selectedId: string) => Observable<FilterOption[]>>();

  protected readonly text = new FormControl<string | FilterOption>('', { nonNullable: true });

  protected readonly options = toSignal(
    this.text.valueChanges.pipe(
      filter((v): v is string => typeof v === 'string'),
      startWith(''),
      debounceTime(250),
      distinctUntilChanged(),
      switchMap((q) => this.search()(q, this.control().value)),
    ),
    { initialValue: [] as FilterOption[] },
  );

  protected readonly displayWith = (v: string | FilterOption | null): string =>
    typeof v === 'string' ? v : (v?.label ?? '');

  constructor() {
    toObservable(this.control)
      .pipe(
        switchMap((c) => c.valueChanges.pipe(startWith(c.value))),
        distinctUntilChanged(),
        switchMap((id) => {
          if (!id) {
            return of(null);
          }

          const current = this.text.value;

          if (typeof current !== 'string' && current.value === id) {
            return EMPTY;
          }

          return this.search()('', id).pipe(
            map((opts) => opts.find((o) => o.value === id) ?? null),
          );
        }),
        takeUntilDestroyed(),
      )
      .subscribe((match) => {
        this.text.setValue(match ?? '', { emitEvent: false });
      });

    this.text.valueChanges.pipe(takeUntilDestroyed()).subscribe((v) => {
      if (v === '' && this.control().value) {
        this.control().setValue('');
      }
    });
  }

  protected onSelected(event: MatAutocompleteSelectedEvent): void {
    this.control().setValue((event.option.value as FilterOption).value);
  }
}
