import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { FilterOption } from '../models/filter-option.model';

@Component({
  selector: 'app-filter-chips',
  imports: [ReactiveFormsModule, MatChipsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './filter-chips.scss',
  templateUrl: './filter-chips.html',
})
export class FilterChips {
  readonly label = input.required<string>();
  readonly options = input.required<readonly FilterOption[]>();
  readonly multiple = input(true);
  readonly control = input.required<FormControl<string[]>>();
}
