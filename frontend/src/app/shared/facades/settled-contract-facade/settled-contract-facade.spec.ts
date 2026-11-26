import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { FilterService, SettledContractService } from '@generated';
import { SettledContractFacade } from './settled-contract-facade';

describe('SettledContractFacade', () => {
  let service: SettledContractFacade;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: SettledContractService,
          useValue: { settledContractKpis: vi.fn(() => of({ data: {} })) },
        },
        { provide: FilterService, useValue: {} },
      ],
    });
    service = TestBed.inject(SettledContractFacade);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should reuse the same KPI resource state', () => {
    expect(service.connectKpis()).toBe(service.connectKpis());
  });
});
