import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { FilterOption } from '../models/filter-option.model';
import { FormControl } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-filter-select',
  imports: [MatFormFieldModule, MatSelectModule, ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './filter-select.html',
  styleUrl: './filter-select.scss',
})
export class FilterSelect<T = string> {
  readonly label = input.required<string>();
  readonly options = input.required<readonly FilterOption<T>[]>();
  readonly multiple = input(true);
  readonly control = input.required<FormControl<T[]>>();
}
