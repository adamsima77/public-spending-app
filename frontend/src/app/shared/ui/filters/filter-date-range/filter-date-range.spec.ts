import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FilterDateRange } from './filter-date-range';

describe('FilterDateRange', () => {
  let component: FilterDateRange;
  let fixture: ComponentFixture<FilterDateRange>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterDateRange],
    }).compileComponents();

    fixture = TestBed.createComponent(FilterDateRange);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
