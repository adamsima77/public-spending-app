import {
  Component,
  DestroyRef,
  ElementRef,
  afterNextRender,
  afterRenderEffect,
  computed,
  inject,
  input,
  signal,
  untracked,
  viewChild,
  viewChildren,
} from '@angular/core';
import { SidebarService } from '../../../core/services/sidebar/sidebar.service';
import { NavConfig } from '../../../config/nav-config';
import { LucideMenu } from '@lucide/angular';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { IndicatorStyle } from './navbar.model';

@Component({
  imports: [LucideMenu, RouterLink, MatButtonModule],
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

  protected readonly activeIndex = computed(() =>
    (this.navigationConfig() ?? []).findIndex((item) => this.sidebarService.isActive(item.path)),
  );

  constructor() {
    afterRenderEffect(() => {
      this.activeIndex();
      this.linkElements();

      untracked(() => this.updateIndicatorPosition());
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
    const index = this.activeIndex();
    const el = index >= 0 ? this.linkElements()[index]?.nativeElement : undefined;
    const navigation = this.linksElement()?.nativeElement.parentElement;

    const nextIndicatorStyle =
      el && navigation && el.offsetWidth > 0
        ? {
            left: `${String(el.getBoundingClientRect().left - navigation.getBoundingClientRect().left)}px`,
            width: `${String(el.offsetWidth)}px`,
          }
        : null;

    const previousIndicatorStyle = this.indicatorStyle();
    const unchanged =
      previousIndicatorStyle?.left === nextIndicatorStyle?.left &&
      previousIndicatorStyle?.width === nextIndicatorStyle?.width;

    if (!unchanged) {
      this.indicatorStyle.set(nextIndicatorStyle);
    }
  }
}
