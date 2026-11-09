import { Service, inject, signal } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

@Service()
export class SidebarService {
  isSidebarActive = signal<boolean>(false);
  currentUrl = signal<string>('');

  private readonly router = inject(Router);

  constructor() {
    this.currentUrl.set(this.router.url);

    this.router.events
      .pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd))
      .subscribe((event) => {
        this.currentUrl.set(event.urlAfterRedirects);
        this.isSidebarActive.set(false);
      });
  }

  updateSidebarState(isActive: boolean): void {
    this.isSidebarActive.set(isActive);
  }

  isActive(path: string): boolean {
    return this.currentUrl() === path;
  }
}
