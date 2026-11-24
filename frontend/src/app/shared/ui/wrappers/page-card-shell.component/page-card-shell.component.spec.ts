import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PageCardShellComponent } from './page-card-shell.component';

describe('PageCardShellComponent', () => {
  let component: PageCardShellComponent;
  let fixture: ComponentFixture<PageCardShellComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PageCardShellComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PageCardShellComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
