import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { MatCard, MatCardContent } from '@angular/material/card';
import { PageHeaderData } from '@shared/ui/page-header/models/page-header.model';
import { PageHeader } from '@shared/ui/page-header/page-header';

@Component({
  selector: 'app-page-card-shell',
  standalone: true,
  imports: [MatCard, MatCardContent, PageHeader],
  templateUrl: './page-card-shell.component.html',
  styleUrl: './page-card-shell.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PageCardShellComponent {
  readonly headerData = input.required<PageHeaderData>();
}
