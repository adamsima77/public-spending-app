import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SettledContractFilters } from './settled-contract-filters';

describe('SettledContractFilters', () => {
  let component: SettledContractFilters;
  let fixture: ComponentFixture<SettledContractFilters>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SettledContractFilters],
    }).compileComponents();

    fixture = TestBed.createComponent(SettledContractFilters);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
