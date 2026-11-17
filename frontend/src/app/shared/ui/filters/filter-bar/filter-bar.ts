import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-filter-bar',
  imports: [MatButtonModule, MatIconModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrl: './filter-bar.scss',
  templateUrl: './filter-bar.html',
})
export class FilterBar {
  readonly hasActive = input(false);
  readonly resetFilters = output();
}
