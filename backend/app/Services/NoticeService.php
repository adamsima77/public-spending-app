<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Notice;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class NoticeService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, Notice>
     */
    public function getNotices(array $filters = []): LengthAwarePaginator
    {
        $query = Notice::query()->with([
            'procedure.buyer',
            'procedure.cpvCode',
            'procedure.nutCode',
            'procedure.procedureType',
            'procedure.contractNature',
            'formType',
            'noticeType',
            'legalBasis',
        ]);

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('notice_id', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('title', 'like', '%' . $filters['search'] . '%');
            });
        }

        foreach (['notice_type', 'form_type', 'procedure_id'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        if (isset($filters['is_latest'])) {
            $query->where('is_latest', $filters['is_latest']);
        }

        if (isset($filters['published_from'])) {
            $query->whereDate('published_at', '>=', $filters['published_from']);
        }

        if (isset($filters['published_to'])) {
            $query->whereDate('published_at', '<=', $filters['published_to']);
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
