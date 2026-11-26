import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, FormGroup } from '@angular/forms';
import { signal } from '@angular/core';
import { of } from 'rxjs';
import { OrganizationFacade } from '@shared/facades/organization-facade/organization-facade';
import { Organizations } from './organizations';

describe('Organizations', () => {
  let component: Organizations;
  let fixture: ComponentFixture<Organizations>;

  beforeEach(async () => {
    const facade = {
      getCompanySizes: () => of([]),
      getOrganizationCountries: () => of([]),
      getInitialFilterValues: () =>
        new FormGroup({
          search: new FormControl('', { nonNullable: true }),
          country: new FormControl<string[]>([], { nonNullable: true }),
          company_size: new FormControl<string[]>([], { nonNullable: true }),
          role: new FormControl<string[]>([], { nonNullable: true }),
        }),
      connectOrganizations: () => ({
        organizations: signal(undefined),
        loading: signal(false),
        error: signal(false),
        reload: vi.fn(),
        hasActiveFilters: signal(false),
      }),
      connectKpis: () => ({
        kpis: signal(undefined),
        loading: signal(false),
        error: signal(false),
        reload: vi.fn(),
      }),
      toKpiCards: () => [],
    };

    await TestBed.configureTestingModule({
      imports: [Organizations],
      providers: [{ provide: OrganizationFacade, useValue: facade }],
    }).compileComponents();

    fixture = TestBed.createComponent(Organizations);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
