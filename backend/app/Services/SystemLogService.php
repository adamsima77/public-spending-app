<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\SystemLog;
use Illuminate\Pagination\LengthAwarePaginator;

class SystemLogService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, SystemLog>
     */
    public function getAllLogs(array $filters = []): LengthAwarePaginator
    {
        $query = SystemLog::query()->with(['user.role']);

        foreach (['type', 'event', 'method', 'user_id'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
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
