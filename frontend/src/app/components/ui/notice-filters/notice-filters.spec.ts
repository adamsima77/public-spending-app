import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoticeFilters } from './notice-filters';

describe('NoticeFilters', () => {
  let component: NoticeFilters;
  let fixture: ComponentFixture<NoticeFilters>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NoticeFilters],
    }).compileComponents();

    fixture = TestBed.createComponent(NoticeFilters);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
