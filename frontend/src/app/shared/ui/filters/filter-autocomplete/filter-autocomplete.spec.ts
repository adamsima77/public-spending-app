import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FilterAutocomplete } from './filter-autocomplete';

describe('FilterAutocomplete', () => {
  let component: FilterAutocomplete;
  let fixture: ComponentFixture<FilterAutocomplete>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FilterAutocomplete],
    }).compileComponents();

    fixture = TestBed.createComponent(FilterAutocomplete);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
