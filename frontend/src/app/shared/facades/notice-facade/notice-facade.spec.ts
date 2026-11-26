import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { FilterService, NoticeService } from '@generated';
import { NoticeFacade } from './notice-facade';

describe('NoticeFacade', () => {
  let service: NoticeFacade;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: NoticeService, useValue: { noticeKpis: vi.fn(() => of({ data: {} })) } },
        { provide: FilterService, useValue: {} },
      ],
    });
    service = TestBed.inject(NoticeFacade);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should reuse the same KPI resource state', () => {
    expect(service.connectKpis()).toBe(service.connectKpis());
  });
});
