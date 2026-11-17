import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { LucideSearch } from '@lucide/angular';

@Component({
  selector: 'app-search-field',
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatButtonModule,
    LucideSearch,
    ReactiveFormsModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './search-field.html',
  styleUrl: './search-field.scss',
})
export class SearchField {
  readonly placeholder = input('Vyhľadajte...');
  readonly control = input.required<FormControl<string>>();

  protected clear(): void {
    this.control().setValue('');
  }
}
