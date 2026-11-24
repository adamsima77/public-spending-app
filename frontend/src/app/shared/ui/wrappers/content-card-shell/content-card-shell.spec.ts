import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ContentCardShell } from './content-card-shell';

describe('ContentCardShell', () => {
  let component: ContentCardShell;
  let fixture: ComponentFixture<ContentCardShell>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContentCardShell],
    }).compileComponents();

    fixture = TestBed.createComponent(ContentCardShell);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
