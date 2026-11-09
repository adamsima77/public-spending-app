import {
  Component,
  DestroyRef,
  ElementRef,
  afterRenderEffect,
  afterNextRender,
  inject,
  input,
  signal,
  viewChild,
  viewChildren,
} from '@angular/core';
import { SidebarService } from '../../../core/services/sidebar.service';
import { NavConfig } from '../../../config/nav-config';
import { LucideCircleUser, LucideMenu } from '@lucide/angular';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';

export interface IndicatorStyle {
  left: string;
  width: string;
}

export const DEFAULT_INDICATOR_STYLE: IndicatorStyle = {
  left: '0px',
  width: '0px',
};

@Component({
  imports: [LucideCircleUser, LucideMenu, RouterLink, MatButtonModule],
  selector: 'app-navbar',
  styleUrl: './navbar.scss',
  templateUrl: './navbar.html',
})
export class Navbar {
  navigationConfig = input<NavConfig[]>();
  navigationElement = viewChild<ElementRef<HTMLElement>>('navigation');
  linkElements = viewChildren<ElementRef<HTMLAnchorElement>>('navLink');
  sidebarService = inject(SidebarService);
  indicatorStyle = signal<IndicatorStyle>(DEFAULT_INDICATOR_STYLE);
  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    afterRenderEffect(() => {
      this.sidebarService.currentUrl();
      this.navigationConfig();
      this.linkElements();

      this.updateIndicatorPosition();
    });

    afterNextRender(() => {
      const navigationElement = this.navigationElement()?.nativeElement;

      if (!navigationElement || typeof ResizeObserver === 'undefined') {
        return;
      }

      const resizeObserver = new ResizeObserver(() => {
        this.updateIndicatorPosition();
      });

      resizeObserver.observe(navigationElement);
      this.destroyRef.onDestroy(() => resizeObserver.disconnect());
    });
  }

  changeSidebarState(): void {
    this.sidebarService.isSidebarActive.update((prev) => !prev);
  }

  updateIndicatorPosition(): void {
    const activeLink = this.linkElements().find(({ nativeElement }) =>
      nativeElement.classList.contains('active'),
    );

    if (!activeLink) {
      return;
    }

    const element = activeLink.nativeElement;

    if (element.offsetWidth === 0) {
      return;
    }

    this.indicatorStyle.set({
      left: `${element.offsetLeft.toString()}px`,
      width: `${element.offsetWidth.toString()}px`,
    });
  }
}
