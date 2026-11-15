import { TestBed } from '@angular/core/testing';
import { OrganizationFacade } from './organization-facade';

describe('OrganizationFacade', () => {
  let service: OrganizationFacade;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(OrganizationFacade);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
