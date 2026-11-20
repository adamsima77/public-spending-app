import { Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

export interface PageHeaderKpi {
  label: string;
  value: string;
  icon: string;
}

export interface PageHeaderData {
  title: string;
  description: string;
  kpis?: PageHeaderKpi[];
  loading?: boolean;
}

@Component({
  imports: [
    MatDividerModule,
    MatCardModule,
    MatIconModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
  ],
  selector: 'app-page-header',
  styleUrl: './page-header.scss',
  templateUrl: './page-header.html',
})
export class PageHeader {
  readonly data = input<PageHeaderData>();
}
