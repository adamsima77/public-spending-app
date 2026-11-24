import { Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { SpinnerLoaderComponent } from '@shared/ui/loaders/spinner-loader/spinner-loader';
import { PageHeaderData } from '@shared/ui/page-header/models/page-header.model';

@Component({
  imports: [
    MatDividerModule,
    MatCardModule,
    MatIconModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    SpinnerLoaderComponent,
  ],
  selector: 'app-page-header',
  styleUrl: './page-header.scss',
  templateUrl: './page-header.html',
})
export class PageHeader {
  readonly data = input<PageHeaderData>();
}
