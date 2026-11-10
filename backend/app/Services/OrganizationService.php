<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Organization;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class OrganizationService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, Organization>
     */
    public function getAllOrganizations(array $filters = []): LengthAwarePaginator
    {
        $query = Organization::query()->with(['nutCode', 'companySize']);

        foreach (['country', 'nuts_code', 'company_size'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('name', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('cin', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('tin', 'like', '%' . $filters['search'] . '%');
            });
        }

        return $query
            ->orderBy('id')
            ->paginate(
                (int) ($filters['per_page'] ?? 15),
                ['*'],
                'page',
                (int) ($filters['page'] ?? 1),
            );
    }
}
