export interface PageHeaderKpi {
  label: string;
  value: string;
  icon: string;
}

export interface PageHeaderData {
  title: string;
  description: string;
  kpis?: PageHeaderKpi[];
  loading?: boolean;
}
