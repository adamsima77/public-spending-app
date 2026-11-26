import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, FormGroup } from '@angular/forms';
import { signal } from '@angular/core';
import { SettledContractFacade } from '@shared/facades/settled-contract-facade/settled-contract-facade';
import { SettledContracts } from './settled-contracts';

describe('SettledContracts', () => {
  let component: SettledContracts;
  let fixture: ComponentFixture<SettledContracts>;

  beforeEach(async () => {
    const facade = {
      getInitialFilterValues: () =>
        new FormGroup({
          search: new FormControl('', { nonNullable: true }),
          buyer_id: new FormControl('', { nonNullable: true }),
          conclusion_from: new FormControl<string | Date | null>('', { nonNullable: true }),
          conclusion_to: new FormControl<string | Date | null>('', { nonNullable: true }),
          has_url: new FormControl<string[]>([], { nonNullable: true }),
          has_tenders: new FormControl<string[]>([], { nonNullable: true }),
          only_current: new FormControl<string[]>([], { nonNullable: true }),
        }),
      connectSettledContracts: () => ({
        settledContracts: signal(undefined),
        loading: signal(false),
        error: signal(false),
        reload: vi.fn(),
        hasActiveFilters: signal(false),
        buyers: {
          options: signal([]),
          selected: signal(null),
          onQuery: vi.fn(),
        },
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
      imports: [SettledContracts],
      providers: [{ provide: SettledContractFacade, useValue: facade }],
    }).compileComponents();

    fixture = TestBed.createComponent(SettledContracts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
