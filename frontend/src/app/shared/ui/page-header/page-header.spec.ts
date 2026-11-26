import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { PageHeader } from './page-header';

describe('PageHeader', () => {
  let component: PageHeader;
  let fixture: ComponentFixture<PageHeader>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PageHeader],
    }).compileComponents();

    fixture = TestBed.createComponent(PageHeader);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show the KPI reload button only after an error', () => {
    const reloadKpis = vi.fn();

    fixture.componentRef.setInput('data', {
      title: 'Title',
      description: 'Description',
      kpis: [],
      error: false,
      reloadKpis,
    });
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css('button'))).toBeNull();

    fixture.componentRef.setInput('data', {
      title: 'Title',
      description: 'Description',
      kpis: [],
      error: true,
      reloadKpis,
    });
    fixture.detectChanges();
    fixture.debugElement.query(By.css('button')).triggerEventHandler('click');

    expect(reloadKpis).toHaveBeenCalledOnce();
  });
});
