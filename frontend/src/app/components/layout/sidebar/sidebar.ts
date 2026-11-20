import { Component, inject, input } from '@angular/core';
import { NavConfig } from '@shared/config/nav-config';
import { RouterLink } from '@angular/router';
import { NavigationService } from '@core/services/navigation-service/navigation.service';

@Component({
  imports: [RouterLink],
  selector: 'app-sidebar',
  styleUrl: './sidebar.scss',
  templateUrl: './sidebar.html',
})
export class Sidebar {
  navigationConfig = input<NavConfig[]>();
  navigationService = inject(NavigationService);

  closeSidebar(): void {
    this.navigationService.close();
  }
}
