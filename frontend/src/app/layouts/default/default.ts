import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Navbar } from '../../components/layout/navbar/navbar';
import { Sidebar } from '../../components/layout/sidebar/sidebar';
import { Footer } from '../../components/layout/footer/footer';
import { NavConfig } from '../../config/nav-config';
import { navConfig } from '../../config/nav-config';
import { SidebarService } from '../../core/services/sidebar.service';

@Component({
  imports: [RouterOutlet, Navbar, Sidebar, Footer],
  selector: 'app-default',
  styleUrl: './default.scss',
  templateUrl: './default.html',
})
export class Default {
  navigationConfig = signal<NavConfig[]>(navConfig);
  sidebarService = inject(SidebarService);
  changeSidebarState(): void {
    this.sidebarService.isSidebarActive.update((prev) => !prev);
  }
}
