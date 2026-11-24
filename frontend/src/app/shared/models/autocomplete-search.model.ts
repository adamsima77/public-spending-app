import { Observable } from 'rxjs';
import { FilterOption } from '@shared/ui/filters/models/filter-option.model';

export type AutocompleteSearch = (query: string, selectedId: string) => Observable<FilterOption[]>;
