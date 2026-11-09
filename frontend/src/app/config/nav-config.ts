export interface NavConfig {
  label: string;
  path: string;
}

export const navConfig: NavConfig[] = [
  {
    label: 'Domov',
    path: '/',
  },
  {
    label: 'Oznámenia',
    path: '/oznamenia',
  },
  {
    label: 'Organizácie',
    path: '/organizacie',
  },
  {
    label: 'Vizualizácie',
    path: '/vizualizacie',
  },
  {
    label: 'O projekte',
    path: '/o-projekte',
  },
  {
    label: 'Kontakt',
    path: '/kontakt',
  },
];
