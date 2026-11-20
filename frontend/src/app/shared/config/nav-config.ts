export interface NavConfig {
  label: string;
  path: string;
}

export const navConfig: NavConfig[] = [
  {
    label: 'Oznámenia',
    path: '/oznamenia',
  },
  {
    label: 'Zmluvy',
    path: '/zmluvy',
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
