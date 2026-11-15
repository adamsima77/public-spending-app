import { Injectable } from '@angular/core';
import { MatPaginatorIntl } from '@angular/material/paginator';

@Injectable()
export class SlovakPaginatorIntl extends MatPaginatorIntl {
  override itemsPerPageLabel = 'Riadkov na stránku:';
  override nextPageLabel = 'Ďalšia stránka';
  override previousPageLabel = 'Predchádzajúca stránka';
  override firstPageLabel = 'Prvá stránka';
  override lastPageLabel = 'Posledná stránka';

  override getRangeLabel = (page: number, pageSize: number, length: number): string => {
    if (length === 0) {
      return `0 z 0`;
    }
    const start = page * pageSize + 1;
    const end = Math.min((page + 1) * pageSize, length);

    return `${start.toString()}-${end.toString()} z ${length.toString()}`;
  };
}
