import { TestBed } from '@angular/core/testing';
import { NoticeFacade } from './notice-facade';

describe('NoticeFacade', () => {
  let service: NoticeFacade;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NoticeFacade);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
