import { Component, inject, input } from '@angular/core';
import { NavConfig } from '../../../config/nav-config';
import { RouterLink } from '@angular/router';
import { SidebarService } from '../../../core/services/sidebar.service';

@Component({
  imports: [RouterLink],
  selector: 'app-sidebar',
  styleUrl: './sidebar.scss',
  templateUrl: './sidebar.html',
})
export class Sidebar {
  navigationConfig = input<NavConfig[]>();
  sidebarService = inject(SidebarService);

  closeSidebar(): void {
    this.sidebarService.updateSidebarState(false);
  }
}
