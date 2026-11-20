import { DestroyRef, Service, Signal, inject, signal } from '@angular/core';
import { IsActiveMatchOptions, NavigationEnd, Router, isActive } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

const EXACT_MATCH: IsActiveMatchOptions = {
  paths: 'exact',
  queryParams: 'ignored',
  fragment: 'ignored',
  matrixParams: 'ignored',
};

const SUBSET_MATCH: IsActiveMatchOptions = {
  ...EXACT_MATCH,
  paths: 'subset',
};

@Service()
export class NavigationService {
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly _isSidebarActive = signal(false);
  private readonly _currentUrl = signal(this.router.url);
  private readonly activeSignals = new Map<string, Signal<boolean>>();
  readonly isSidebarActive = this._isSidebarActive.asReadonly();
  readonly currentUrl = this._currentUrl.asReadonly();

  constructor() {
    this.router.events.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((event) => {
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
    let active = this.activeSignals.get(path);

    if (!active) {
      active = isActive(path, this.router, path === '/' ? EXACT_MATCH : SUBSET_MATCH);
      this.activeSignals.set(path, active);
    }

    return active();
  }
}
