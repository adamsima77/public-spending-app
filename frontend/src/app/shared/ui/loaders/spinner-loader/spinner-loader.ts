import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-spinner-loader',
  imports: [MatProgressSpinnerModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './spinner-loader.html',
  styleUrl: './spinner-loader.scss',
})
export class SpinnerLoader {
  public readonly diameter = input(40);
  public readonly label = input('Načítavam údaje');
}
