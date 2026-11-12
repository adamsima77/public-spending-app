import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
import { environment } from '../../../environments/environment';

@Component({
  imports: [MatCardModule, MatButtonModule, RouterLink],
  selector: 'app-about-project',
  styleUrl: './about-project.scss',
  templateUrl: './about-project.html',
})
export class AboutProject {
  readonly docsUrl: string = environment.docsUrl;
}
