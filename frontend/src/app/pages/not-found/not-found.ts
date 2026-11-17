import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { LucideSearchX, LucideHouse, LucideBuildingComplex, LucideFileText } from '@lucide/angular';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [
    RouterLink,
    MatCardModule,
    MatButtonModule,
    LucideSearchX,
    LucideHouse,
    LucideBuildingComplex,
    LucideFileText,
  ],
  templateUrl: './not-found.html',
  styleUrl: './not-found.scss',
})
export class NotFound {}
