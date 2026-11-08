<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\CpvCode;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class CpvCodeService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, CpvCode>
     */
    public function getAllCpvCodes(array $filters = []): LengthAwarePaginator
    {
        $query = CpvCode::query()->with(['parent']);

        foreach (['level', 'parent_code'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('code', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('name_sk', 'like', '%' . $filters['search'] . '%');
            });
        }

        return $query->orderBy('code')->paginate((int) ($filters['per_page'] ?? 50));
    }
}
