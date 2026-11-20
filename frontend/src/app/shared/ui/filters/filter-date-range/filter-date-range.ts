import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { provideNativeDateAdapter } from '@angular/material/core';

@Component({
  selector: 'app-filter-date-range',
  imports: [ReactiveFormsModule, MatFormFieldModule, MatDatepickerModule],
  providers: [provideNativeDateAdapter()],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './filter-date-range.html',
  styleUrl: './filter-date-range.scss',
})
export class FilterDateRange {
  readonly label = input('Obdobie');
  readonly fromControl = input.required<FormControl<string | Date | null>>();
  readonly toControl = input.required<FormControl<string | Date | null>>();
}
