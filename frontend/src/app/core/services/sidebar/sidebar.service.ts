import { Service, computed, inject, signal } from '@angular/core';
import {
  NavigationCancel,
  NavigationEnd,
  NavigationError,
  NavigationStart,
  Router,
} from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DestroyRef } from '@angular/core';

@Service()
export class SidebarService {
  private readonly router = inject(Router);
  private readonly _isSidebarActive = signal(false);
  private readonly _currentUrl = signal(this.router.url);
  private readonly currentPath = computed(() => this._currentUrl().split(/[?#]/)[0]);
  readonly isSidebarActive = this._isSidebarActive.asReadonly();
  readonly currentUrl = this._currentUrl.asReadonly();
  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    this.router.events.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((event) => {
      if (event instanceof NavigationStart) {
        return;
      }

      if (event instanceof NavigationCancel || event instanceof NavigationError) {
        return;
      }

      if (!(event instanceof NavigationEnd)) {
        return;
      }

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
    const currentPath = this.currentPath();
    const active = currentPath === path;

    return active;
  }
}
