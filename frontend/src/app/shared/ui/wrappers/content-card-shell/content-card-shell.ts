import { Component } from '@angular/core';
import { input } from '@angular/core';
import {
  MatCard,
  MatCardHeader,
  MatCardTitle,
  MatCardContent,
  MatCardActions,
} from '@angular/material/card';

@Component({
  imports: [MatCard, MatCardHeader, MatCardTitle, MatCardContent, MatCardActions],
  selector: 'app-content-card-shell',
  styleUrl: './content-card-shell.scss',
  templateUrl: './content-card-shell.html',
})
export class ContentCardShell {
  readonly title = input.required<string>();
}
