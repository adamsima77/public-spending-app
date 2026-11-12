import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SettledContracts } from './settled-contracts';

describe('SettledContracts', () => {
  let component: SettledContracts;
  let fixture: ComponentFixture<SettledContracts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SettledContracts],
    }).compileComponents();

    fixture = TestBed.createComponent(SettledContracts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
