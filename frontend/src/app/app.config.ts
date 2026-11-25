import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  provideRouter,
  withComponentInputBinding,
  withViewTransitions,
} from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient } from '@angular/common/http';
import { provideApiConfiguration } from './generated';
import { environment } from '../environments/environment';
import { provideClientHydration } from '@angular/platform-browser';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { SlovakPaginatorIntl } from './shared/translations/slovak-paginator-intl';
import { MatPaginatorIntl } from '@angular/material/paginator';

const leaf = (route: ActivatedRouteSnapshot): ActivatedRouteSnapshot =>
  route.firstChild ? leaf(route.firstChild) : route;

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(
      routes,
      withComponentInputBinding(),
      withViewTransitions({
        skipInitialTransition: true,
        onViewTransitionCreated: ({ transition, from, to }) => {
          if (leaf(from).routeConfig === leaf(to).routeConfig) {
            transition.skipTransition();
            void transition.ready.catch(() => undefined);
            void transition.finished.catch(() => undefined);
            void transition.updateCallbackDone.catch(() => undefined);
          }
        },
      }),
    ),
    provideHttpClient(),
    provideApiConfiguration(environment.apiUrl),
    provideClientHydration(),
    provideCharts(withDefaultRegisterables()),
    { provide: MatPaginatorIntl, useClass: SlovakPaginatorIntl },
  ],
};
