import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { FilterService, OrganizationService } from '@generated';
import { OrganizationFacade } from './organization-facade';

describe('OrganizationFacade', () => {
  let service: OrganizationFacade;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: OrganizationService,
          useValue: { organizationKpis: vi.fn(() => of({ data: {} })) },
        },
        { provide: FilterService, useValue: {} },
      ],
    });
    service = TestBed.inject(OrganizationFacade);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should reuse the same KPI resource state', () => {
    expect(service.connectKpis()).toBe(service.connectKpis());
  });
});
