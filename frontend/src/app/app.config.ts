import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient } from '@angular/common/http';
import { provideApiConfiguration } from './generated';
import { environment } from '../environments/environment';
import { provideClientHydration } from '@angular/platform-browser';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { SlovakPaginatorIntl } from './shared/translations/slovak-paginator-intl';
import { MatPaginatorIntl } from '@angular/material/paginator';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(),
    provideApiConfiguration(environment.apiUrl),
    provideClientHydration(),
    provideCharts(withDefaultRegisterables()),
    { provide: MatPaginatorIntl, useClass: SlovakPaginatorIntl },
  ],
};
