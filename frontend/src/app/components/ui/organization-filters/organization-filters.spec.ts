import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OrganizationFilters } from './organization-filters';

describe('OrganizationFilters', () => {
  let component: OrganizationFilters;
  let fixture: ComponentFixture<OrganizationFilters>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrganizationFilters],
    }).compileComponents();

    fixture = TestBed.createComponent(OrganizationFilters);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
