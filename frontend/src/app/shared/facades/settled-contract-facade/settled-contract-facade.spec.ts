import { TestBed } from '@angular/core/testing';
import { SettledContractFacade } from './settled-contract-facade';

describe('SettledContractFacade', () => {
  let service: SettledContractFacade;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SettledContractFacade);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
