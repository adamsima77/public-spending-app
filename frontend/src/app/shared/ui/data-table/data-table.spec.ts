import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DataTable } from './data-table';

describe('DataTable', () => {
  let component: DataTable<unknown>;
  let fixture: ComponentFixture<DataTable<unknown>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DataTable],
    }).compileComponents();

    fixture = TestBed.createComponent(DataTable<unknown>);
    fixture.componentRef.setInput('columns', []);
    fixture.componentRef.setInput('rows', []);
    fixture.componentRef.setInput('reload', vi.fn());
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show a retry button only after a loading error', () => {
    const reload = vi.fn();

    fixture.componentRef.setInput('reload', reload);
    fixture.detectChanges();

    expect(fixture.debugElement.query(By.css('.table-error'))).toBeNull();

    fixture.componentRef.setInput('error', true);
    fixture.detectChanges();

    fixture.debugElement.query(By.css('.table-error button')).triggerEventHandler('click');

    expect(reload).toHaveBeenCalledOnce();
  });
});
