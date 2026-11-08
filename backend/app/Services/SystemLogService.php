<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\SystemLog;
use Illuminate\Pagination\CursorPaginator;

class SystemLogService
{
    /** @param array<string, mixed> $filters
     * @return CursorPaginator<int, SystemLog>
     */
    public function getAllLogs(array $filters = []): CursorPaginator
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
            ->cursorPaginate((int) ($filters['per_page'] ?? 15));
    }
}
