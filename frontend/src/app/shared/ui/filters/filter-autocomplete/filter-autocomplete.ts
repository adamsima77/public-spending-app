import { ChangeDetectionStrategy, Component, input, output, linkedSignal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import {
  MatAutocompleteModule,
  MatAutocompleteSelectedEvent,
} from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
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
  readonly options = input.required<readonly FilterOption[]>();
  readonly selected = input<FilterOption | null>(null);

  readonly queryChange = output<string>();

  protected readonly text = linkedSignal(() => this.selected()?.label ?? '');

  protected readonly displayWith = (o: FilterOption | null): string => o?.label ?? '';

  protected onInput(event: Event): void {
    const query = (event.target as HTMLInputElement).value;

    this.text.set(query);
    this.queryChange.emit(query);

    if (!query) {
      this.control().setValue('');
    }
  }

  protected onSelected(event: MatAutocompleteSelectedEvent): void {
    const option = event.option.value as FilterOption;

    this.text.set(option.label);
    this.control().setValue(option.value);
  }
}
