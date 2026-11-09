import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Visualizations } from './visualizations';

describe('Visualizations', () => {
  let component: Visualizations;
  let fixture: ComponentFixture<Visualizations>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Visualizations],
    }).compileComponents();

    fixture = TestBed.createComponent(Visualizations);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
