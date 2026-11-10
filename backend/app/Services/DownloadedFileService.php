<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\DownloadedFile;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Pagination\LengthAwarePaginator;

class DownloadedFileService
{
    /** @param array<string, mixed> $filters
     * @return LengthAwarePaginator<int, DownloadedFile>
     */
    public function getAllDownloadedFiles(array $filters = []): LengthAwarePaginator
    {
        $query = DownloadedFile::query()->with(['status']);

        foreach (['status_id', 'format'] as $field) {
            if (isset($filters[$field])) {
                $query->where($field, $filters[$field]);
            }
        }

        if (isset($filters['search'])) {
            $query->where(function (Builder $query) use ($filters): void {
                $query->where('filename', 'like', '%' . $filters['search'] . '%')
                    ->orWhere('file_id', 'like', '%' . $filters['search'] . '%');
            });
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
