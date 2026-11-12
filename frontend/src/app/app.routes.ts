import { Routes } from '@angular/router';
import { Default } from './layouts/default/default';

export const routes: Routes = [
  {
    path: '',
    component: Default,
    children: [
      {
        path: '',
        loadComponent: () => import('./pages/home/home').then((m) => m.Home),
      },
      {
        path: 'kontakt',
        loadComponent: () => import('./pages/contact/contact').then((m) => m.Contact),
      },
      {
        path: 'o-projekte',
        loadComponent: () =>
          import('./pages/about-project/about-project').then((m) => m.AboutProject),
      },
      {
        path: 'oznamenia',
        loadComponent: () => import('./pages/notices/notices').then((m) => m.Notices),
      },
      {
        path: 'organizacie',
        loadComponent: () =>
          import('./pages/organizations/organizations').then((m) => m.Organizations),
      },
      {
        path: 'vizualizacie',
        loadComponent: () =>
          import('./pages/visualizations/visualizations').then((m) => m.Visualizations),
      },
      {
        path: 'zmluvy',
        loadComponent: () =>
          import('./pages/settled-contracts/settled-contracts').then((m) => m.SettledContracts),
      },
      {
        path: '**',
        loadComponent: () => import('./pages/not-found/not-found').then((m) => m.NotFound),
      },
    ],
  },
];
