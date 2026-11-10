import {
  Component,
  DestroyRef,
  ElementRef,
  afterNextRender,
  afterRenderEffect,
  inject,
  input,
  signal,
  viewChild,
  viewChildren,
} from '@angular/core';
import { SidebarService } from '../../../core/services/sidebar/sidebar.service';
import { NavConfig } from '../../../config/nav-config';
import { LucideCircleUser, LucideMenu } from '@lucide/angular';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { IndicatorStyle } from './navbar.model';

@Component({
  imports: [LucideCircleUser, LucideMenu, RouterLink, MatButtonModule],
  selector: 'app-navbar',
  styleUrl: './navbar.scss',
  templateUrl: './navbar.html',
})
export class Navbar {
  navigationConfig = input<NavConfig[]>();
  linksElement = viewChild<ElementRef<HTMLElement>>('links');
  linkElements = viewChildren<ElementRef<HTMLAnchorElement>>('navLink');
  sidebarService = inject(SidebarService);
  indicatorStyle = signal<IndicatorStyle | null>(null);
  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    afterRenderEffect(() => {
      this.sidebarService.currentUrl();
      this.linkElements();
      this.updateIndicatorPosition();
    });

    afterNextRender(() => {
      const links = this.linksElement()?.nativeElement;

      if (!links) {
        return;
      }

      const observer = new ResizeObserver(() => this.updateIndicatorPosition());

      observer.observe(links);
      this.destroyRef.onDestroy(() => observer.disconnect());
    });
  }

  changeSidebarState(): void {
    this.sidebarService.toggle();
  }

  private updateIndicatorPosition(): void {
    const el = this.linkElements().find(({ nativeElement }) =>
      nativeElement.classList.contains('active'),
    )?.nativeElement;

    this.indicatorStyle.set(
      el && el.offsetWidth > 0
        ? { left: `${String(el.offsetLeft)}px`, width: `${String(el.offsetWidth)}px` }
        : null,
    );
  }
}
