import { Service, computed, inject, signal } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

@Service()
export class SidebarService {
  private readonly router = inject(Router);
  private readonly _isSidebarActive = signal(false);
  private readonly _currentUrl = signal(this.router.url);
  private readonly currentPath = computed(() => this._currentUrl().split(/[?#]/)[0]);
  readonly isSidebarActive = this._isSidebarActive.asReadonly();
  readonly currentUrl = this._currentUrl.asReadonly();
  constructor() {
    this.router.events
      .pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd))
      .subscribe((event) => {
        this._currentUrl.set(event.urlAfterRedirects);
        this._isSidebarActive.set(false);
      });
  }

  toggle(): void {
    this._isSidebarActive.update((v) => !v);
  }

  close(): void {
    this._isSidebarActive.set(false);
  }

  isActive(path: string): boolean {
    return this.currentPath() === path;
  }
}
