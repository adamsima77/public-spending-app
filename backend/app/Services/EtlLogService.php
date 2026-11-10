<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\EtlLog;
use Illuminate\Pagination\LengthAwarePaginator;

class EtlLogService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, EtlLog>
     */
    public function getAllLogs(array $filters = []): LengthAwarePaginator
    {
        $query = EtlLog::query()->with(['file.status']);

        foreach (['file_id', 'level'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        if (isset($filters['search'])) {
            $query->where('message', 'like', '%' . $filters['search'] . '%');
        }

        if (isset($filters['created_from'])) {
            $query->whereDate('created_at', '>=', $filters['created_from']);
        }

        if (isset($filters['created_to'])) {
            $query->whereDate('created_at', '<=', $filters['created_to']);
        }

        return $query
            ->orderByDesc('created_at')
            ->orderByDesc('id')
            ->paginate(
                (int) ($filters['per_page'] ?? 15),
                ['*'],
                'page',
                (int) ($filters['page'] ?? 1),
            );
    }
}
