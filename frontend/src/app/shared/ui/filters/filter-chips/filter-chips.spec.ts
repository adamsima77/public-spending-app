import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FilterChips } from './filter-chips';

describe('FilterChips', () => {
  let component: FilterChips;
  let fixture: ComponentFixture<FilterChips>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterChips],
    }).compileComponents();

    fixture = TestBed.createComponent(FilterChips);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
