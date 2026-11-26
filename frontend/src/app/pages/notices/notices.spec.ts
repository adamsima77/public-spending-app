import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, FormGroup } from '@angular/forms';
import { signal } from '@angular/core';
import { of } from 'rxjs';
import { NoticeFacade } from '@shared/facades/notice-facade/notice-facade';
import { Notices } from './notices';

describe('Notices', () => {
  let component: Notices;
  let fixture: ComponentFixture<Notices>;

  beforeEach(async () => {
    const facade = {
      getNoticeTypes: () => of([]),
      getFormTypes: () => of([]),
      getInitialFilterValues: () =>
        new FormGroup({
          search: new FormControl('', { nonNullable: true }),
          notice_type: new FormControl<string[]>([], { nonNullable: true }),
          form_type: new FormControl<string[]>([], { nonNullable: true }),
          procedure_id: new FormControl<number | null>(null),
          is_latest: new FormControl<boolean | null>(null),
          published_from: new FormControl<string | Date | null>('', { nonNullable: true }),
          published_to: new FormControl<string | Date | null>('', { nonNullable: true }),
        }),
      connectNotices: () => ({
        notices: signal(undefined),
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
      imports: [Notices],
      providers: [{ provide: NoticeFacade, useValue: facade }],
    }).compileComponents();

    fixture = TestBed.createComponent(Notices);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
