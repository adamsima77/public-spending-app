import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FilterRangeSlider } from './filter-range-slider';

describe('FilterRangeSlider', () => {
  let component: FilterRangeSlider;
  let fixture: ComponentFixture<FilterRangeSlider>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterRangeSlider],
    }).compileComponents();

    fixture = TestBed.createComponent(FilterRangeSlider);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
